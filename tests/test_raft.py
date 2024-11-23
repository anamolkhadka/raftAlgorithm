import unittest
import grpc
import time
import raft_service_pb2
import raft_service_pb2_grpc

class TestRaft(unittest.TestCase):
    def setUp(self):
        """
        Set up gRPC clients for all the servers.
        """
        self.ports = [5001, 5002, 5003, 5004, 5005]
        self.clients = {
            port: raft_service_pb2_grpc.RaftServiceStub(
                grpc.insecure_channel(f"localhost:{port}")
            ) for port in self.ports
        }

    # def find_leader(self):
    #     """
    #     Identify the leader by querying the status of all servers.
    #     """
    #     for port, client in self.clients.items():
    #         try:
    #             response = client.GetStatus(raft_service_pb2.GetStatusRequest())
    #             if response.state == "Leader":
    #                 return f"localhost:{port}"
    #         except grpc.RpcError:
    #             pass
    #     return None
    
    def find_leader(self, retries=3, delay=2):
        for _ in range(retries):
            for port, client in self.clients.items():
                try:
                    response = client.GetStatus(raft_service_pb2.GetStatusRequest())
                    if response.state == "Leader":
                        return f"localhost:{port}"
                except grpc.RpcError:
                    pass
            time.sleep(delay)  # Wait before retrying
        return None


    def test_leader_election(self):
        """
        Verify one leader is elected in the cluster.
        """
        leader_address = self.find_leader()
        self.assertIsNotNone(leader_address, "No leader elected.")
        print("✔ Verify one leader is elected in the cluster.")

    def test_leader_failure(self):
        """
        Verify a new leader is elected when the current leader fails.
        """
        # Identify the leader
        leader_address = self.find_leader()
        self.assertIsNotNone(leader_address, "No leader elected initially.")

        print(f"Simulating failure for leader at port {leader_address.split(':')[1]}. Please stop the leader server manually.")
        input("Press Enter after stopping the leader server...")  # Wait for user confirmation

        # Wait for a new leader to be elected
        time.sleep(10)
        new_leader_address = self.find_leader()
        self.assertIsNotNone(new_leader_address, "No new leader elected.")
        self.assertNotEqual(
            leader_address, new_leader_address, f"Leader did not change after failure. Still {leader_address}"
        )
        print("✔ Verify a new leader is elected when the current leader fails.")

    def test_log_replication(self):
        """
        Verify commands sent to the leader are replicated to all followers.
        """
        leader_address = self.find_leader()
        self.assertIsNotNone(leader_address, "No leader identified for log replication test.")
        print(f"Leader identified for log replication: {leader_address}")

        leader_client = self.clients[int(leader_address.split(":")[1])]  # Match port to client

        # Send a command to the leader
        command = "operation_1"
        request = raft_service_pb2.ClientRequestMessage(command=command)
        response = leader_client.ClientRequest(request)
        self.assertTrue(response.success, "Leader did not successfully apply the command.")

        time.sleep(5)  # Wait for log replication

        # Verify the logs in all followers
        for port, client in self.clients.items():
            if f"localhost:{port}" != leader_address:
                try:
                    log_response = client.GetLog(raft_service_pb2.GetLogRequest())
                    log_commands = [entry.command for entry in log_response.entries]
                    self.assertIn(command, log_commands, f"Command '{command}' not found in logs of server at port {port}.")
                except grpc.RpcError:
                    print(f"Skipping server at port {port} due to connection failure.")
        print("✔ Verify commands sent to the leader are replicated to all followers.")


    def test_leader_status_request(self):
        """
        Verify that the leader responds correctly to GetStatus requests.
        """
        leader_address = self.find_leader()
        self.assertIsNotNone(leader_address, "No leader identified for status request test.")

        leader_client = self.clients[int(leader_address.split(":")[1])]
        try:
            response = leader_client.GetStatus(raft_service_pb2.GetStatusRequest())
            self.assertEqual(response.state, "Leader", "Leader does not report itself as a leader.")
            print(f"✔ Leader at {leader_address} responds correctly to status requests.")
        except grpc.RpcError:
            self.fail(f"Leader at {leader_address} did not respond to status request.")


    def test_log_consistency(self):
        """
        Verify that all servers have consistent logs with the leader.
        """
        leader_address = self.find_leader()
        self.assertIsNotNone(leader_address, "No leader identified for log consistency test.")
        print(f"Leader identified for log consistency: {leader_address}")

        leader_client = self.clients[int(leader_address.split(":")[1])]
        leader_log_response = leader_client.GetLog(raft_service_pb2.GetLogRequest())
        leader_logs = [(entry.index, entry.term, entry.command) for entry in leader_log_response.entries]

        for port, client in self.clients.items():
            if f"localhost:{port}" != leader_address:
                try:
                    log_response = client.GetLog(raft_service_pb2.GetLogRequest())
                    follower_logs = [(entry.index, entry.term, entry.command) for entry in log_response.entries]
                    self.assertEqual(
                        leader_logs,
                        follower_logs,
                        f"Log mismatch between leader and server at port {port}.",
                    )
                    print(f"✔ Logs consistent for server at port {port}.")
                except grpc.RpcError:
                    print(f"Skipping server at port {port} due to connection failure.")
        print("✔ Verify logs are consistent across all servers.")


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestRaft)
    runner = unittest.TextTestRunner(resultclass=unittest.TextTestResult, verbosity=2)
    result = runner.run(suite)

    total_tests = result.testsRun
    failed_tests = len(result.failures) + len(result.errors)
    passed_tests = total_tests - failed_tests

    print("\n----------------------------------------------------------------------")
    print(f"Ran {total_tests} tests in {result.stopTime - result.startTime:.3f}s")
    print(f"Tests Passed: {passed_tests}, Tests Failed: {failed_tests}")

    if failed_tests == 0:
        print("ALL TESTS PASSED !")
    else:
        print("FAILED")


