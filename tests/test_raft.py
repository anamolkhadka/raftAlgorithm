import unittest
import subprocess
import time
import grpc
import sys
import os

# Adjust the import paths for the server and gRPC files
sys.path.append(os.path.join(os.path.dirname(__file__), "../server_python/examples/python/raft"))

import raft_service_pb2
import raft_service_pb2_grpc


class TestRaft(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        Start 5 Raft servers before running the tests.
        """
        cls.server_processes = []
        cls.server_logs = []
        ports = [5001, 5002, 5003, 5004, 5005]
        peers = [f"localhost:{p}" for p in ports]

        for i, port in enumerate(ports):
            peers_without_self = [peer for peer in peers if peer != f"localhost:{port}"]
            process = subprocess.Popen(
                ["python", os.path.join(os.path.dirname(__file__), "../server_python/examples/python/raft/raft_server.py"),
                 str(i + 1), str(port)] + peers_without_self,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            cls.server_processes.append(process)
            cls.server_logs.append(f"server_{i + 1}.log")

        time.sleep(10)  # Allow servers to initialize and elect a leader

    @classmethod
    def tearDownClass(cls):
        """
        Stop all Raft servers after the tests and save logs.
        """
        for i, process in enumerate(cls.server_processes):
            process.terminate()
            process.wait()
            stdout, stderr = process.communicate()
            with open(cls.server_logs[i], "w") as log_file:
                log_file.write(f"STDOUT:\n{stdout.decode()}\nSTDERR:\n{stderr.decode()}\n")

    def test_leader_election(self):
        """
        Verify that one leader is elected in the cluster.
        """
        leaders = []
        for process in self.server_processes:
            stdout, _ = process.communicate(timeout=5)
            if b"transitions to Leader" in stdout:
                leaders.append(stdout.decode().split("Process")[1].split("transitions")[0].strip())

        self.assertEqual(len(leaders), 1, "There should be exactly one leader.")
        print(f"Leader elected: {leaders[0]}")

    def test_log_replication(self):
        """
        Verify that commands sent to the leader are replicated to all followers.
        """
        command = "operation_1"

        # Identify leader
        leader_address = self.find_leader()
        self.assertIsNotNone(leader_address, "Leader not identified for log replication test.")

        # Send client request to the leader
        client = self.create_client(leader_address)
        response = self.send_client_request(client, command)
        self.assertTrue(response.success, "Leader did not apply the command successfully.")

        time.sleep(5)  # Allow log replication

        # Verify logs on all servers
        for process in self.server_processes:
            stdout, _ = process.communicate(timeout=5)
            self.assertIn(command, stdout.decode(), f"Command '{command}' not found in server logs.")

    def test_leader_failure(self):
        """
        Verify that a new leader is elected when the current leader fails.
        """
        # Identify and terminate the leader
        leader_index = None
        leader_address = None
        for i, process in enumerate(self.server_processes):
            stdout, _ = process.communicate(timeout=5)
            if b"transitions to Leader" in stdout:
                leader_index = i
                leader_address = f"localhost:{5000 + (i + 1)}"
                break

        self.assertIsNotNone(leader_index, "Leader not found.")
        self.server_processes[leader_index].terminate()
        self.server_processes[leader_index].wait()

        time.sleep(10)  # Allow election timeout for new leader

        # Verify new leader is elected
        leaders = []
        for i, process in enumerate(self.server_processes):
            if i != leader_index:  # Skip the terminated process
                stdout, _ = process.communicate(timeout=5)
                if b"transitions to Leader" in stdout:
                    leaders.append(stdout.decode().split("Process")[1].split("transitions")[0].strip())

        self.assertEqual(len(leaders), 1, "There should be exactly one new leader.")
        print(f"New leader elected: {leaders[0]}")

    def create_client(self, address):
        """
        Create a gRPC client for testing.
        """
        return grpc.insecure_channel(address)

    def send_client_request(self, client, command):
        """
        Send a client request to the Raft cluster.
        """
        stub = raft_service_pb2_grpc.RaftServiceStub(client)
        request = raft_service_pb2.ClientRequestMessage(command=command)
        return stub.ClientRequest(request)

    def find_leader(self):
        """
        Find the current leader by parsing logs.
        """
        for i, process in enumerate(self.server_processes):
            stdout, _ = process.communicate(timeout=5)
            if b"transitions to Leader" in stdout:
                return f"localhost:{5000 + (i + 1)}"
        return None


if __name__ == "__main__":
    unittest.main()