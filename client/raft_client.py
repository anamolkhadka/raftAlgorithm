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
            
            # Create a client request
            request = raft_service_pb2.ClientRequestMessage(
                command=command  # The command to be processed
            )
            
            # Send the request to the server
            response = stub.ClientRequest(request)
            
            # Print the response from the server
            print(f"Response from server: Success={response.success}, Message='{response.message}'")
    except grpc.RpcError as e:
        print(f"gRPC error occurred: {e.details()}")


if __name__ == "__main__":
    # Example usage: Send a command to a server at localhost:5001
    server_address = "localhost:5002"  # Address of any Raft server
    command = "operation_1"  # The operation to be executed
    send_command(server_address, command)
