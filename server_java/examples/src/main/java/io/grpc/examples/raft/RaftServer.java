package io.grpc.examples.raft;

import io.grpc.*;
import io.grpc.stub.StreamObserver;

import java.io.IOException;
import java.util.*;
import java.util.concurrent.*;
import java.util.logging.Logger;
import raft.RaftServiceGrpc;
import raft.RaftServiceOuterClass.*;

public class RaftServer {
    private static final Logger logger = Logger.getLogger(RaftServer.class.getName());

    private final int serverId;
    private final List<String> peers;
    private final int port;
    private final ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(1);
    private Server server;

    private String state = "Follower";
    private int currentTerm = 0;
    private Integer votedFor = null;
    private Integer leaderId = null;
    private final List<LogEntry> logs = new ArrayList<>();
    private long lastHeartbeat = System.currentTimeMillis();
    private final Random random = new Random();

    public RaftServer(int serverId, int port, List<String> peers) {
        this.serverId = serverId;
        this.port = port;
        this.peers = peers;
    }

    private void start() throws IOException {
        server = Grpc.newServerBuilderForPort(port, InsecureServerCredentials.create())
                .addService(new RaftServiceImpl())
                .build()
                .start();
        logger.info("Server " + serverId + " started, listening on " + port);
        startElectionTimer();
    }

    private void startElectionTimer() {
        scheduler.scheduleAtFixedRate(() -> {
            if (System.currentTimeMillis() - lastHeartbeat > randomElectionTimeout()) {
                startElection();
            }
        }, 100, 100, TimeUnit.MILLISECONDS);
    }

    private void startHeartbeatTimer() {
        scheduler.scheduleAtFixedRate(this::sendHeartbeat, 0, 100, TimeUnit.MILLISECONDS);
    }

    private void startElection() {
        state = "Candidate";
        currentTerm++;
        votedFor = serverId;
        leaderId = null; // Reset leaderId during elections
        logger.info("Server " + serverId + " became Candidate for term " + currentTerm);

        int votes = 1; // Vote for itself
        for (String peer : peers) {
            boolean voteGranted = sendRequestVote(peer);
            if (voteGranted) {
                votes++;
            }
        }

        if (votes > peers.size() / 2) {
            state = "Leader";
            leaderId = serverId;
            logger.info("Server " + serverId + " became Leader for term " + currentTerm);
            startHeartbeatTimer();
        }
    }

    private boolean sendRequestVote(String peer) {
        ManagedChannel channel = ManagedChannelBuilder.forTarget(peer).usePlaintext().build();
        RaftServiceGrpc.RaftServiceBlockingStub stub = RaftServiceGrpc.newBlockingStub(channel);
        RequestVoteRequest request = RequestVoteRequest.newBuilder()
                .setTerm(currentTerm)
                .setCandidateId(serverId)
                .setLastLogIndex(logs.size() - 1)
                .setLastLogTerm(logs.isEmpty() ? 0 : logs.get(logs.size() - 1).getTerm())
                .build();
        try {
            RequestVoteResponse response = stub.requestVote(request);
            logger.info("Server " + serverId + " received RequestVoteResponse from peer: " + peer);
            return response.getVoteGranted();
        } catch (Exception e) {
            logger.warning("Failed to send RequestVote to peer " + peer + ": " + e.getMessage());
            return false;
        } finally {
            channel.shutdown();
        }
    }

    private void sendHeartbeat() {
        if (state.equals("Leader")) {
            logger.info("Server " + serverId + " sends heartbeat to peers");
            for (String peer : peers) {
                sendAppendEntries(peer);
            }
        }
    }

    private void sendAppendEntries(String peer) {
        ManagedChannel channel = ManagedChannelBuilder.forTarget(peer).usePlaintext().build();
        RaftServiceGrpc.RaftServiceBlockingStub stub = RaftServiceGrpc.newBlockingStub(channel);
        AppendEntriesRequest request = AppendEntriesRequest.newBuilder()
                .setTerm(currentTerm)
                .setLeaderId(serverId)
                .setPrevLogIndex(logs.size() - 1)
                .setPrevLogTerm(logs.isEmpty() ? 0 : logs.get(logs.size() - 1).getTerm())
                .setLeaderCommit(0)
                .build();
        try {
            AppendEntriesResponse response = stub.appendEntries(request);
            logger.info("Server " + serverId + " received AppendEntriesResponse from peer: " + peer);
        } catch (Exception e) {
            logger.warning("Failed to send AppendEntries to peer " + peer + ": " + e.getMessage());
        } finally {
            channel.shutdown();
        }
    }

    private int randomElectionTimeout() {
        return 150 + random.nextInt(150);
    }

    public static void main(String[] args) throws IOException, InterruptedException {
        if (args.length < 3) {
            System.err.println("Usage: RaftServer <serverId> <port> <peer1> <peer2> ...");
            System.exit(1);
        }
        int serverId = Integer.parseInt(args[0]);
        int port = Integer.parseInt(args[1]);
        List<String> peers = Arrays.asList(Arrays.copyOfRange(args, 2, args.length));

        final RaftServer raftServer = new RaftServer(serverId, port, peers);
        raftServer.start();
    }

    private class RaftServiceImpl extends RaftServiceGrpc.RaftServiceImplBase {
        @Override
        public void requestVote(RequestVoteRequest request, StreamObserver<RequestVoteResponse> responseObserver) {
            logger.info("Server " + serverId + " received RequestVote from " + request.getCandidateId());
            boolean voteGranted = false;
            if (request.getTerm() > currentTerm || (request.getTerm() == currentTerm
                    && (votedFor == null || votedFor == request.getCandidateId()))) {
                voteGranted = true;
                votedFor = request.getCandidateId();
                currentTerm = request.getTerm();
                lastHeartbeat = System.currentTimeMillis();
            }
            responseObserver
                    .onNext(RequestVoteResponse.newBuilder().setTerm(currentTerm).setVoteGranted(voteGranted).build());
            responseObserver.onCompleted();
        }

        @Override
        public void appendEntries(AppendEntriesRequest request,
                StreamObserver<AppendEntriesResponse> responseObserver) {
            logger.info("Server " + serverId + " received AppendEntries from " + request.getLeaderId());
            boolean success = false;
            if (request.getTerm() >= currentTerm) {
                currentTerm = request.getTerm();
                leaderId = request.getLeaderId();
                lastHeartbeat = System.currentTimeMillis();
                success = true;
            }
            responseObserver
                    .onNext(AppendEntriesResponse.newBuilder().setTerm(currentTerm).setSuccess(success).build());
            responseObserver.onCompleted();
        }

        @Override
        public void clientRequest(ClientRequestMessage request,
                StreamObserver<ClientResponseMessage> responseObserver) {
            logger.info("Server " + serverId + " received ClientRequest: " + request.getCommand());
            if (!state.equals("Leader")) {
                if (leaderId != null) {
                    String leaderAddress = "localhost:" + (5000 + leaderId);
                    logger.info("Server " + serverId + " forwarding request to leader at " + leaderAddress);
                    ManagedChannel channel = ManagedChannelBuilder.forTarget(leaderAddress).usePlaintext().build();
                    RaftServiceGrpc.RaftServiceBlockingStub stub = RaftServiceGrpc.newBlockingStub(channel);
                    try {
                        ClientResponseMessage response = stub.clientRequest(request);
                        responseObserver.onNext(response);
                    } catch (Exception e) {
                        logger.warning("Failed to forward request to leader: " + e.getMessage());
                        responseObserver.onNext(ClientResponseMessage.newBuilder().setSuccess(false)
                                .setMessage("Leader unreachable").build());
                    } finally {
                        channel.shutdown();
                    }
                } else {
                    responseObserver.onNext(ClientResponseMessage.newBuilder().setSuccess(false)
                            .setMessage("No leader available").build());
                }
            } else {
                logs.add(LogEntry.newBuilder().setIndex(logs.size()).setTerm(currentTerm)
                        .setCommand(request.getCommand()).build());
                responseObserver.onNext(
                        ClientResponseMessage.newBuilder().setSuccess(true).setMessage("Command applied").build());
            }
            responseObserver.onCompleted();
        }
    }
}