# Raft Consensus Algorithm Implementation

This project implements the Raft consensus algorithm with two key features: Leader Election and Log Replication. The system uses gRPC for communication between nodes (servers) and a client that interacts with the cluster.

# Overview

The Raft consensus algorithm is implemented with the following capabilities:

- Leader Election: Nodes can elect a leader using randomized election timeouts and handle network failures.
- Log Replication: The leader replicates client commands across all followers to maintain a consistent state.

The system consists of:

- 5 nodes (servers): 4 implemented in Python and 1 in Java.
- 1 client: Communicates with the cluster to send operations.

# Project Structure

- Client: raftAlgorithm->client->raft_client.py
- Protos: raftAlgorithm->protos->raft_service.proto
- Java Server: raftAlgorithm/server_java/examples/src/main/java/io/grpc/examples/raft/RaftServer.java
- Python Server: raftAlgorithm/server_python/examples/python/raft/raft_server.py

# Running the Project Locally

Start the Java Server
- cd server_java/examples
- Build command ./gradlew installDist. Need to add the peers to this build configuration.
- Run command ./build/install/examples/bin/raft-server

Start the Python Server
- cd raftAlgorithm/server_python/examples/python/raft
- Generate gRPC stubs: python -m grpc_tools.protoc -I../../protos --python_out=. --pyi_out=. --grpc_python_out=. ../../protos/raft_service.proto
- Run the server: python raft/raft_server.py <server_id> <port> <peer1> <peer2> ...
  E.g. python raft_server.py 1 5001 localhost:5002 localhost:5003
- Run four python servers in 4 different terminals.

Client
- Open new terminal.
- cd raftAlgorithm/client
- Generate gRPC stubs: python -m grpc_tools.protoc -I../protos --python_out=. --grpc_python_out=. ../protos/raft_service.proto
- python raft_client.py

# Features
- Dynamic Leader Election: Automatic leader election with failure recovery.
- Log Replication: Consistent replication of client operations across all nodes.
- Fault Tolerance: Handles network failures and node crashes gracefully.

