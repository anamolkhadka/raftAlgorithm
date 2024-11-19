import grpc
import time
import threading
import random
from concurrent import futures
from raft_service_pb2 import (
    RequestVoteRequest, 
    RequestVoteResponse, 
    AppendEntriesResponse, 
    AppendEntriesRequest,
    ClientRequestMessage,
    ClientResponseMessage,
    LogEntry as ProtoLogEntry,
)
import raft_service_pb2_grpc


class LogEntry:
    def __init__(self, index, term, command):
        self.index = index
        self.term = term
        self.command = command


class RaftServer(raft_service_pb2_grpc.RaftServiceServicer):
    def __init__(self, server_id, peers):
        self.server_id = server_id
        self.peers = peers  # List of other server addresses
        self.current_term = 0
        self.voted_for = None
        self.state = "Follower"  # Follower, Candidate, Leader
        self.logs = []  # Log entries: list of LogEntry
        self.commit_index = -1  # Index of the last committed log entry
        self.next_index = {}  # Next log index to send to each peer (Leader state)
        self.match_index = {}  # Highest log index known to be replicated on each peer (Leader state)
        self.heartbeat_interval = 0.1  # 100ms
        self.election_timeout = random.uniform(0.15, 0.3)  # Random between 150ms and 300ms
        self.election_timer = None
        self.heartbeat_timer = None
        self.vote_count = 0  # To track votes received during an election
        self.reset_election_timer()

    def reset_election_timer(self):
        if self.election_timer:
            self.election_timer.cancel()
        self.election_timer = threading.Timer(self.election_timeout, self.start_election)
        self.election_timer.start()

    def start_heartbeat_timer(self):
        if self.heartbeat_timer:
            self.heartbeat_timer.cancel()
        self.heartbeat_timer = threading.Timer(self.heartbeat_interval, self.send_heartbeat)
        self.heartbeat_timer.start()

    def start_election(self):
        self.state = "Candidate"
        self.current_term += 1
        self.voted_for = self.server_id
        self.vote_count = 1  # Vote for itself
        print(f"Process {self.server_id} transitions to Candidate for term {self.current_term}")
        self.reset_election_timer()  # Reset election timer for a new term
        self.send_request_vote()

    def send_request_vote(self):
        print(f"Process {self.server_id} sends RPC RequestVote to peers")
        for peer in self.peers:
            threading.Thread(target=self.request_vote_from_peer, args=(peer,)).start()

    def request_vote_from_peer(self, peer):
        with grpc.insecure_channel(peer) as channel:
            stub = raft_service_pb2_grpc.RaftServiceStub(channel)
            request = RequestVoteRequest(
                term=self.current_term,
                candidateId=self.server_id,
                lastLogIndex=len(self.logs) - 1,
                lastLogTerm=self.logs[-1].term if self.logs else 0,
            )
            try:
                response = stub.RequestVote(request)
                print(f"Process {self.server_id} receives RPC RequestVoteResponse from Process {peer}: {response.voteGranted}")
                if response.voteGranted:
                    self.vote_count += 1
                    if self.vote_count > len(self.peers) // 2:
                        self.state = "Leader"
                        print(f"Process {self.server_id} transitions to Leader for term {self.current_term}")
                        self.initialize_leader_state()
                        self.start_heartbeat_timer()
            except grpc.RpcError as e:
                print(f"RPC error while contacting Process {peer}: {e}")

    def initialize_leader_state(self):
        for peer in self.peers:
            self.next_index[peer] = len(self.logs)
            self.match_index[peer] = -1

    def send_heartbeat(self):
        if self.state == "Leader":
            print(f"Process {self.server_id} sends AppendEntries (heartbeat) to peers")
            for peer in self.peers:
                threading.Thread(target=self.append_entries_to_peer, args=(peer,)).start()
            self.start_heartbeat_timer()  # Schedule next heartbeat

    def append_entries_to_peer(self, peer):
        with grpc.insecure_channel(peer) as channel:
            stub = raft_service_pb2_grpc.RaftServiceStub(channel)
            prev_log_index = self.next_index[peer] - 1
            prev_log_term = self.logs[prev_log_index].term if prev_log_index >= 0 else 0
            entries = [
                ProtoLogEntry(index=log.index, term=log.term, command=log.command)
                for log in self.logs[self.next_index[peer]:]
            ]
            request = AppendEntriesRequest(
                term=self.current_term,
                leaderId=self.server_id,
                entries=entries,
                prevLogIndex=prev_log_index,
                prevLogTerm=prev_log_term,
                leaderCommit=self.commit_index,
            )
            try:
                response = stub.AppendEntries(request)
                print(f"Process {self.server_id} receives AppendEntriesResponse from Process {peer}: {response.success}")
                if response.success:
                    self.match_index[peer] = len(self.logs) - 1
                    self.next_index[peer] = len(self.logs)
                else:
                    self.next_index[peer] -= 1  # Decrement and retry
            except grpc.RpcError as e:
                print(f"RPC error while contacting Process {peer}: {e}")
    
    def get_leader_address(self):
        if self.leader_id is not None:
            leader_index = self.leader_id - 1  # Assuming IDs are 1-based
            return self.peers[leader_index]
        return None

    def ClientRequest(self, request, context):
        print(f"Process {self.server_id} received ClientRequest: {request.command}")
        if self.state != "Leader":
            # Forward to the leader
            leader_address = self.get_leader_address()
            if leader_address:
                with grpc.insecure_channel(leader_address) as channel:
                    stub = raft_service_pb2_grpc.RaftServiceStub(channel)
                    forward_request = ClientRequestMessage(command=request.command)
                    forward_response = stub.ClientRequest(forward_request)
                    return forward_response
            else:
                return ClientResponseMessage(success=False, message="No leader available")
        
        # Append to log and replicate
        log_entry = LogEntry(len(self.logs), self.current_term, request.command)
        self.logs.append(log_entry)
        self.replicate_log()
        return ClientResponseMessage(success=True, message="Command applied")

    def replicate_log(self):
        print(f"Process {self.server_id} replicates log entries to followers")
        for peer in self.peers:
            threading.Thread(target=self.append_entries_to_peer, args=(peer,)).start()

    def RequestVote(self, request, context):
        print(f"Process {self.server_id} receives RPC RequestVote from Process {request.candidateId}")
        vote_granted = False
        if request.term > self.current_term:
            self.current_term = request.term
            self.state = "Follower"
            self.voted_for = None
        if (self.voted_for is None or self.voted_for == request.candidateId) and request.term >= self.current_term:
            self.voted_for = request.candidateId
            vote_granted = True
            self.reset_election_timer()
            print(f"Process {self.server_id} grants vote to Process {request.candidateId}: {vote_granted}")
        return RequestVoteResponse(term=self.current_term, voteGranted=vote_granted)

    def AppendEntries(self, request, context):
        print(f"Process {self.server_id} receives RPC AppendEntries from Process {request.leaderId}")
        success = False
        if request.term >= self.current_term:
            self.current_term = request.term
            self.state = "Follower"
            self.reset_election_timer()
            # Validate log consistency
            if request.prevLogIndex == -1 or (
                len(self.logs) > request.prevLogIndex
                and self.logs[request.prevLogIndex].term == request.prevLogTerm
            ):
                success = True
                # Append new entries
                self.logs = self.logs[:request.prevLogIndex + 1] + [
                    LogEntry(entry.index, entry.term, entry.command) for entry in request.entries
                ]
                # Update commit index
                if request.leaderCommit > self.commit_index:
                    self.commit_index = min(request.leaderCommit, len(self.logs) - 1)
        print(f"Process {self.server_id}: AppendEntries success: {success}")
        return AppendEntriesResponse(term=self.current_term, success=success)


def serve(server_id, port, peers):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    raft_service_pb2_grpc.add_RaftServiceServicer_to_server(RaftServer(server_id, peers), server)
    server.add_insecure_port(f'[::]:{port}')
    print(f"Process {server_id} started, listening on {port}")
    server.start()
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print(f"Process {server_id} shutting down")
        server.stop(0)  # Gracefully stop the server

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python raft_server.py <server_id> <port> <peer1> <peer2> ...")
        sys.exit(1)

    server_id = int(sys.argv[1])
    port = int(sys.argv[2])
    peers = sys.argv[3:]
    serve(server_id, port, peers)