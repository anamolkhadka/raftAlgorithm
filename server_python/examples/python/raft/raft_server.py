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
    GetStatusResponse,
    GetLogResponse
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
        self.leader_id = None  # Initialize leader_id to track the current leader
        self.unreachable_peers = {}  # Track unreachable peers and their retry times
        self.retry_interval = 5  # Retry unreachable peers every 5 seconds
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
        # Check if the peer is in the unreachable list and if its retry timer has passed
        if peer in self.unreachable_peers:
            if time.time() < self.unreachable_peers[peer]:
                print(f"Process {self.server_id}: Skipping unreachable peer {peer} for RequestVote.")
                return  # Skip if still within retry interval
            else:
                print(f"Process {self.server_id}: Retrying previously unreachable peer {peer} for RequestVote.")
        
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
                # Remove peer from unreachable list if it responds successfully.
                if peer in self.unreachable_peers:
                    del self.unreachable_peers[peer]
            except grpc.RpcError as e:
                print(f"RPC error while contacting Process {peer}: {e}")
                # Mark the peer as unreachable and set a new retry time
                self.unreachable_peers[peer] = time.time() + self.retry_interval

    def initialize_leader_state(self):
        self.leader_id = self.server_id  # Set leader_id to self
        for peer in self.peers:
            self.next_index[peer] = len(self.logs)
            self.match_index[peer] = -1
        self.send_heartbeat()  # Immediately send heartbeats after election

    def send_heartbeat(self):
        if self.state == "Leader":
            print(f"Process {self.server_id} sends AppendEntries (heartbeat) to peers")
            for peer in self.peers:
                threading.Thread(target=self.append_entries_to_peer, args=(peer,)).start()
            self.start_heartbeat_timer()  # Schedule next heartbeat
    
    # Get status method for test script.
    def GetStatus(self, request, context):
        """
        Handle GetStatus RPC to provide the server's current status.
        """
        print(f"Process {self.server_id} responding to GetStatus request.")
        return GetStatusResponse(
            state=self.state,
            current_term=self.current_term,
            voted_for=self.voted_for if self.voted_for is not None else -1,
            leader_id=self.leader_id if self.leader_id is not None else -1
        )
    
    def to_proto_log_entry(self, log_entry):
        """
        Convert internal LogEntry to ProtoLogEntry.
        """
        return ProtoLogEntry(
            index=log_entry.index,
            term=log_entry.term,
            command=log_entry.command
        )

    def GetLog(self, request, context):
        """
        Handle GetLog RPC to provide the server's log entries.
        """
        print(f"Process {self.server_id} responding to GetLog request.")
        proto_logs = [self.to_proto_log_entry(log) for log in self.logs]
        return GetLogResponse(entries=proto_logs)



    def append_entries_to_peer(self, peer):
        if peer in self.unreachable_peers:
            if time.time() < self.unreachable_peers[peer]:
                print(f"Process {self.server_id}: Skipping unreachable peer {peer} for AppendEntries.")
                return  # Skip if still within retry interval
            else:
                print(f"Process {self.server_id}: Retrying previously unreachable peer {peer} for AppendEntries.")
        
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
                # Remove peer from unreachable list if it responds successfully
                if peer in self.unreachable_peers:
                    del self.unreachable_peers[peer]
            except grpc.RpcError as e:
                print(f"Process {self.server_id}: Failed to contact peer {peer} for AppendEntries. Error: {e.details()} - {e.code()}")
                # Mark the peer as unreachable and set a new retry time
                self.unreachable_peers[peer] = time.time() + self.retry_interval
    
    def get_leader_address(self):
        """
        Return the address of the leader based on self.leader_id.
        """
        if self.leader_id is not None:
            leader_port = 5000 + self.leader_id  # Assuming ports are sequential
            leader_address = f"localhost:{leader_port}"
            print(f"Process {self.server_id}: Leader ID {self.leader_id} mapped to {leader_address}")
            return leader_address
        print(f"Process {self.server_id}: No valid leader_id found")
        return None

    def ClientRequest(self, request, context):
        print(f"Process {self.server_id} received ClientRequest: {request.command}")
        print(f"Process {self.server_id}: State = {self.state}, Leader ID = {self.leader_id}, Term = {self.current_term}")
        
        if self.state != "Leader":
            # Forward to the leader
            leader_address = self.get_leader_address()
            if leader_address:
                print(f"Process {self.server_id}: Forwarding request to leader at {leader_address}")
                with grpc.insecure_channel(leader_address) as channel:
                    stub = raft_service_pb2_grpc.RaftServiceStub(channel)
                    forward_request = ClientRequestMessage(command=request.command)
                    try:
                        forward_response = stub.ClientRequest(forward_request)
                        return forward_response
                    except grpc.RpcError as e:
                        print(f"Process {self.server_id}: Failed to forward to leader {leader_address}. Error: {e.details()}")
                        return ClientResponseMessage(success=False, message="Leader unreachable")
            else:
                print(f"Process {self.server_id}: No leader available to forward request.")
                return ClientResponseMessage(success=False, message="No leader available")
        
        # Leader processes the command
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
        print(f"Process {self.server_id}: Current Leader ID = {self.leader_id}, Received Leader ID = {request.leaderId}")
        success = False
        if request.term >= self.current_term:
            self.current_term = request.term
            self.state = "Follower"
            if self.leader_id != request.leaderId:  # Log leader_id updates
                self.leader_id = request.leaderId
                print(f"Process {self.server_id}: Updated leader_id to {self.leader_id}")
            self.reset_election_timer()
            # Validate log consistency
            if request.prevLogIndex == -1 or (
                len(self.logs) > request.prevLogIndex
                and self.logs[request.prevLogIndex].term == request.prevLogTerm
            ):
                success = True
                # Append new entries if applicable
                try:
                    self.logs = self.logs[:request.prevLogIndex + 1] + [
                        LogEntry(entry.index, entry.term, entry.command) for entry in request.entries
                    ]
                    # Update commit index
                    if request.leaderCommit > self.commit_index:
                        self.commit_index = min(request.leaderCommit, len(self.logs) - 1)
                except IndexError:
                    print(f"Process {self.server_id}: IndexError during log replication")
                    success = False
        print(f"Process {self.server_id}: AppendEntries success: {success}, Leader ID: {self.leader_id}")
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