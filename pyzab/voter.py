""" Handles setting up voters so an election can be called """

import logging
import socket
import threading
import time
import SocketServer

from .config import Config
from .fle import FastLeaderElection
from .serialization import read_string, write_string
from .state import State
from .vote import Vote


class Voter(threading.Thread):
    """
    A peer receives connections from peers w/ > id and connects to peers w/
    a lower id.

    It then sends & receives votes until a leader is elected.
    """

    class ServerHandler(SocketServer.BaseRequestHandler):
        def handle(self):
            """
            loop & exchange votes w/ the remote peer's vote

            TODO: check if a connection exists for this peer & reject if so

            """

            myid = self.server.voter.config.myid
            voter = self.server.voter

            self.request.settimeout(10)

            while voter.running:
                try:
                    data = read_string(self.request)
                except socket.timeout:
                    # that's ok, just try again
                    continue

                if data is None:
                    logging.error("client went away")
                    break

                try:
                    othervote = Vote.parse(data)
                    logging.info("received vote from client: %s", othervote)
                    voter.update_vote(othervote)
                except ValueError:
                    logging.error("badly serialized vote: %s", data)
                    break

                self.request.sendall(write_string(voter.vote))

    class Server(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
        allow_reuse_address = True
        voter = None

    class Client(threading.Thread):
        """ handles connection to a remote peer """

        TIMEOUT = 5

        def __init__(self, voter, pconfig):
            super(Voter.Client, self).__init__()
            self.setDaemon(True)

            self.running = False
            self.voter = voter
            self.pconfig = pconfig
            self.myid = voter.config.myid

            self.start()

        def run(self):
            """ main loop """

            logging.info("Connecting to peer %d (myid=%d)", self.pconfig.peer_id, self.myid)
            self.running = True
            timeout = Voter.Client.TIMEOUT
            endpoint = self.pconfig.election_endpoint
            voter = self.voter

            while self.running:
                # first, lets connect
                try:
                    sock = socket.create_connection(endpoint, timeout)
                except socket.error as se:
                    logging.error("connection error: %s", se)
                    time.sleep(3)
                    continue

                # next, send out vote every 60 secs
                while self.running:
                    try:
                        sock.sendall(write_string(voter.vote))
                        data = read_string(sock)
                        if data is None:
                            logging.error("server went away")

                        our_vote_changed = False
                        try:
                            othervote = Vote.parse(data)
                            logging.info("received vote from server: %s", othervote)
                            our_vote_changed = voter.update_vote(othervote)
                        except ValueError:
                            logging.error("badly serialized vote: %s", data)
                            sock.close()
                            break

                        # if our vote changed, don't sleep! send it out immediately
                        if not our_vote_changed:
                            # sleep for 60 seconds, but in small bits to check if we are still running
                            for _ in xrange(0, 600):
                                if not self.running:
                                    break
                                time.sleep(0.1)
                    except socket.error as se:
                        logging.error("failed to read/write: %s", se)
                        sock.close()
                        break

            logging.info("exiting Voter.Client's main loop")

    def __init__(self, confs, zxid=0x0):
        """ parse conf """
        super(Voter, self).__init__()
        self.setDaemon(True)

        self.running = False
        self.config = Config.parse(confs)

        self.state = State.LOOKING
        self.zxid = zxid

        # initially, we vote for ourselves
        myid = self.config.myid
        self.fle_lock = threading.Lock()
        self.fle = FastLeaderElection(self.config.members)
        self.fle.update(
            Vote(self.config.myid, self.state, self.config.myid, self.zxid)
        )

        self.start()

    @property
    def vote(self):
        """
        this voter's vote
        """
        return self.fle.get(self.config.myid)

    def update_vote(self, othervote):
        """
        update the vote (and check if our vote needs to change)
        """
        assert othervote.myid != self.config.myid

        self.fle.update(othervote)

        # should our vote change?
        with self.fle_lock:
            if othervote > self.vote:
                newvote = Vote(self.vote.myid, self.state, othervote.proposed_id, othervote.zxid)
                self.fle.update(newvote)
                return True

        return False

    @property
    def leader_id(self):
        """
        the elected leader, if any
        """
        return self.fle.leader_id

    def run(self):
        self.running = True

        server = Voter.Server(self.config.election_endpoint, Voter.ServerHandler)
        server.voter = self
        ip, port = server.server_address

        self.name = "Voter({}:{})".format(ip, port)

        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.name = "VoterServer({}:{})".format(ip, port)
        server_thread.daemon = True
        server_thread.start()

        logging.info("Server loop running in thread: %s", server_thread.name)

        clients = []
        for pconfig in self.config.peers:
            if self.config.myid > pconfig.peer_id:
                clients.append(Voter.Client(self, pconfig))

        while self.running:
            time.sleep(0.5)

        # shutdown
        for client in clients:
            client.running = False
            while client.isAlive():
                time.sleep(0.1)

        server.shutdown()
        server = None
