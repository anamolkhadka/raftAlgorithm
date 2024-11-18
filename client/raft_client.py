import grpc
import raft_service_pb2
import raft_service_pb2_grpc

def send_command(server_address, command):
    """
    Sends a client command to a server, which forwards it to the leader for processing.
    """
    try:
        with grpc.insecure_channel(server_address) as channel:
            stub = raft_service_pb2_grpc.RaftServiceStub(channel)
            
            # Create a log entry to send as part of the AppendEntriesRequest
            log_entry = raft_service_pb2.LogEntry(
                index=0,  # This will be adjusted by the leader
                term=0,   # This will be adjusted by the leader
                command=command
            )
            
            # Send the AppendEntries request with the log entry
            request = raft_service_pb2.AppendEntriesRequest(
                term=1,  # The term of the current request (placeholder)
                leaderId=1,  # Leader ID (placeholder)
                entries=[log_entry],  # Include the log entry
                prevLogIndex=0,  # Placeholder, as the leader adjusts this
                prevLogTerm=0,   # Placeholder
                leaderCommit=0   # Placeholder
            )
            response = stub.AppendEntries(request)
            print(f"Response from server: {response.success}")
    except grpc.RpcError as e:
        print(f"gRPC error occurred: {e.details()}")

if __name__ == "__main__":
    # Example usage: Send a command to a server at localhost:5001
    server_address = "localhost:5001"  # Address of any Raft server
    command = "operation_1"  # The operation to be executed
    send_command(server_address, command)
