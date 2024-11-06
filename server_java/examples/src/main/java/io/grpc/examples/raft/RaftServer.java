package io.grpc.examples.raft;

import io.grpc.Grpc;
import io.grpc.InsecureServerCredentials;
import io.grpc.Server;
import io.grpc.stub.StreamObserver;
import java.io.IOException;
import java.util.concurrent.TimeUnit;
import java.util.logging.Logger;
import java.util.Random;
import java.util.Timer;
import java.util.TimerTask;

public class RaftServer {
    private static final Logger logger = Logger.getLogger(RaftServer.class.getName());
    private Server server;
    private static int nodeId; // Unique ID for the server
    private static String state = "Follower"; // Initial state

    // Election timeout settings
    private Timer electionTimer;
    private static final int HEARTBEAT_INTERVAL = 100; // 100ms
    private static final int MIN_ELECTION_TIMEOUT = 150; // 150ms
    private static final int MAX_ELECTION_TIMEOUT = 300; // 300ms

    private void start(int port) throws IOException {
        server = Grpc.newServerBuilderForPort(port, InsecureServerCredentials.create())
            .addService(new RaftServiceImpl())
            .build()
            .start();
        logger.info("Server " + nodeId + " started, listening on " + port);
        initializeElectionTimer();
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            System.err.println("*** shutting down gRPC server since JVM is shutting down");
            try {
                RaftServer.this.stop();
            } catch (InterruptedException e) {
                e.printStackTrace(System.err);
            }
            System.err.println("*** server shut down");
        }));
    }

    private void stop() throws InterruptedException {
        if (server != null) {
            server.shutdown().awaitTermination(30, TimeUnit.SECONDS);
        }
    }

    private void blockUntilShutdown() throws InterruptedException {
        if (server != null) {
            server.awaitTermination();
        }
    }

    private void initializeElectionTimer() {
        resetElectionTimer();
    }

    private void resetElectionTimer() {
        if (electionTimer != null) {
            electionTimer.cancel();
        }
        electionTimer = new Timer();
        int electionTimeout = new Random().nextInt(MAX_ELECTION_TIMEOUT - MIN_ELECTION_TIMEOUT) + MIN_ELECTION_TIMEOUT;
        electionTimer.schedule(new TimerTask() {
            @Override
            public void run() {
                startElection();
            }
        }, electionTimeout);
    }

    private void startElection() {
        logger.info("Server " + nodeId + " transitioning to Candidate state.");
        state = "Candidate";
        // Increment term, vote for itself, and send RequestVote RPCs
        // Implement logic for voting and majority check
    }

    public static void main(String[] args) throws IOException, InterruptedException {
        nodeId = Integer.parseInt(args[0]); // Pass node ID as a command-line argument
        int port = 50050 + nodeId; // Each node runs on a different port

        RaftServer server = new RaftServer();
        server.start(port);
        server.blockUntilShutdown();
    }

    static class RaftServiceImpl extends RaftServiceGrpc.RaftServiceImplBase {

        @Override
        public void requestVote(RequestVoteRequest req, StreamObserver<RequestVoteResponse> responseObserver) {
            logger.info("Process " + nodeId + " receives RPC RequestVote from Process " + req.getCandidateId());
            // Logic to handle the vote request

            // Send response
            RequestVoteResponse response = RequestVoteResponse.newBuilder()
                    .setTerm(req.getTerm())
                    .setVoteGranted(true) // This should be conditional based on the state
                    .build();
            logger.info("Process " + nodeId + " sends RPC RequestVote response to Process " + req.getCandidateId());
            responseObserver.onNext(response);
            responseObserver.onCompleted();
        }

        @Override
        public void appendEntries(AppendEntriesRequest req, StreamObserver<AppendEntriesResponse> responseObserver) {
            logger.info("Process " + nodeId + " receives RPC AppendEntries from Process " + req.getLeaderId());
            // Logic to handle heartbeat or log replication

            // Send response
            AppendEntriesResponse response = AppendEntriesResponse.newBuilder()
                    .setTerm(req.getTerm())
                    .setSuccess(true) // This should be conditional based on the state
                    .build();
            logger.info("Process " + nodeId + " sends RPC AppendEntries response to Process " + req.getLeaderId());
            responseObserver.onNext(response);
            responseObserver.onCompleted();
        }
    }
}
