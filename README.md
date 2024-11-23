# Raft Consensus Algorithm Implementation

This project implements the **Raft consensus algorithm** with two core features: **Leader Election** and **Log Replication**. The system uses **gRPC** for communication between nodes (servers) and a client that interacts with the cluster.

---

## **Overview**

The Raft consensus algorithm ensures reliable distributed system behavior through:

1. **Leader Election**: Nodes elect a leader using randomized election timeouts and manage failover scenarios gracefully.
2. **Log Replication**: The leader replicates client commands across all followers to maintain a consistent state.

The system is composed of:

- **5 Nodes (Servers)**:
  - **4 Python servers**
  - **1 Java server**
- **1 Client**: A client application that interacts with the cluster to send commands.

---

## **Raft Functionalities**

### **Core Features**
1. **Leader Election:**
   - Nodes autonomously elect a leader.
   - In case of a leader failure, another node is elected as the new leader.
   - Election mechanisms ensure no "split-brain" condition occurs.

2. **Log Replication:**
   - The leader replicates log entries to followers.
   - Commands are committed only after reaching a majority (quorum) of nodes.
   - Ensures state consistency across all nodes.

3. **Client Request Handling:**
   - The client can send commands to **any node** in the cluster.
     - If the contacted node is the leader, it processes the request.
     - If the contacted node is a follower, it forwards the request to the leader (if known).
     - During an election, the client receives a message: "No leader available."

4. **Heartbeat Mechanism:**
   - The leader periodically sends heartbeats (`AppendEntries`) to followers to maintain its authority.
   - Followers reset their election timers upon receiving these heartbeats.

5. **Failover Recovery:**
   - In the event of a leader crash, the system elects a new leader from the remaining nodes.
   - The new leader seamlessly takes over request handling.

6. **Fault Tolerance:**
   - Nodes track unreachable peers and periodically retry communication.
   - Network partitions and node crashes are handled without impacting the cluster’s overall functionality.

---

## **Project Structure**

- **Client**: `raftAlgorithm/client/raft_client.py`
- **Protos**: `raftAlgorithm/protos/raft_service.proto`
- **Java Server**: `raftAlgorithm/server_java/examples/src/main/java/io/grpc/examples/raft/RaftServer.java`
- **Python Server**: `raftAlgorithm/server_python/examples/python/raft/raft_server.py`

---

## **Running the Project Locally**

### **Start the Java Server**
- cd server_java/examples
- Build command ./gradlew installDist.
- Run command ./build/install/examples/bin/raft_server <serverId> <port> <peer1> <peer2> ...
- E.g. ./build/install/examples/bin/raft-server 5 5005 localhost:5001 localhost:5002 localhost:5003 localhost:5004

### **Start the Python Server**
- cd raftAlgorithm/server_python/examples/python/raft
- Generate gRPC stubs: python -m grpc_tools.protoc -I../../protos --python_out=. --pyi_out=. --grpc_python_out=. ../../protos/raft_service.proto
- Run the server: python raft/raft_server.py <server_id> <port> <peer1> <peer2> ...
  E.g. python raft_server.py 1 5001 localhost:5002 localhost:5003 localhost:5004 localhost:5005,
  python raft_server.py 2 5002 localhost:5001 localhost:5003 localhost:5004 localhost:5005, etc.
- Run four python servers in 4 different terminals.

### **Start the Python Client**
- Open new terminal.
- cd raftAlgorithm/client
- Generate gRPC stubs: python -m grpc_tools.protoc -I../protos --python_out=. --grpc_python_out=. ../protos/raft_service.proto
- python raft_client.py

### **Stopping the servers**
- Ctrl/Cmd + c to exit the servers.
- Note: if the servers are not stopped properly, there will be issue in the communication between servers in the next run.
- lsof -i :Port command to see the process running in the used ports.
- kill -9 <PID> to kill it completely before running the servers cluster. OR
- kill -9 $(lsof -t -i :5001) to kill all process in the given port.

### Running the Unit test cases
- Starts the Servers Manually like before. Open 5 terminals and run the following commands. 1 in each.
- python raft_server.py 1 5001 localhost:5002 localhost:5003 localhost:5004 localhost:5005
- python raft_server.py 2 5002 localhost:5001 localhost:5003 localhost:5004 localhost:5005
- python raft_server.py 3 5003 localhost:5001 localhost:5002 localhost:5004 localhost:5005
- python raft_server.py 4 5004 localhost:5001 localhost:5002 localhost:5003 localhost:5005
- python raft_server.py 5 5005 localhost:5001 localhost:5002 localhost:5003 localhost:5004
- Open another terminal.
- cd raftAlgorithm/tests
- python -m unittest test_raft.py
- Follow the instruction. For killing the leader. Ctrl + c.
- See the test cases results.


## **Running the Project with Docker**
- cd raftAlgorithm
- Build the Images. docker-compose build
- Run the containers. docker-compose up
- Check Logs. docker-compose logs -f
- Stop the Containers. docker-compose down or stop from the docker desktop.

### Testing with Docker
- You can see the logs inside the docker container to see the log replication and leader election entries.
- For testing with raft_client.py and unit test case test_raft.py, please follow the local approach as instructed above. These test cases
does not run as intented with the docker containers.