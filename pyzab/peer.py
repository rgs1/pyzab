""" Peer handler: elect a leader """

import logging
import socket
import threading
import time
import SocketServer

from .config import Config
from .serialization import read_string, write_string
from .state import State
from .vote import Vote


class Peer(threading.Thread):
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

            self.request.settimeout(10)

            while self.server.peer.running:
                try:
                    data = read_string(self.request)
                except socket.timeout:
                    # that's ok, just try again
                    continue

                if data is None:
                    logging.error("client went away")
                    break

                logging.info("Received vote from client: %s", data)
                vote = self.server.peer.vote
                self.request.sendall(write_string(str(vote)))

    class Server(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
        allow_reuse_address = True
        peer_config = None

    class Client(threading.Thread):
        """ handles connection to a remote peer """

        TIMEOUT = 5

        def __init__(self, peer, pconfig):
            super(Peer.Client, self).__init__()
            self.setDaemon(True)

            self.running = False
            self.peer = peer
            self.pconfig = pconfig
            self.myid = self.peer.config.myid

        def run(self):
            """ main loop """

            logging.info("Connecting to peer %d (myid=%d)", self.pconfig.peer_id, self.myid)
            self.running = True
            timeout = Peer.Client.TIMEOUT

            while self.running:
                # first, lets connect
                try:
                    sock = socket.create_connection((self.pconfig.host, self.pconfig.port), timeout)
                except socket.timeout:
                    logging.error("Connection timeout..sleeping")
                    time.sleep(3)
                    continue

                # send out vote every 60 secs
                while self.running:
                    try:
                        sock.sendall(write_string(str(self.peer.vote)))
                        response = read_string(sock)
                        if response is None:
                            logging.error("server went away")
                        logging.info("Received reply vote: %s", response)
                        time.sleep(60)
                    except socket.error as se:
                        logging.error("Failed to read/write: %s", se)
                        sock.close()
                        break

    def __init__(self, confs):
        """ parse conf """
        super(Peer, self).__init__()
        self.setDaemon(True)

        self.running = False
        self.config = Config.parse(confs)

        # initially, we vote for ourselves
        self.vote = Vote(self.config.myid, State.LOOKING, self.config.myid, State.LOOKING)

    def run(self):
        self.running = True

        server = Peer.Server(self.config.host_port, Peer.ServerHandler)
        server.peer = self
        ip, port = server.server_address

        self.name = "Peer({}:{})".format(ip, port)

        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.name = "PeerServer({}:{})".format(ip, port)
        server_thread.daemon = True
        server_thread.start()

        logging.info("Server loop running in thread: %s", server_thread.name)

        clients = []
        for pconfig in self.config.peers:
            if self.config.myid > pconfig.peer_id:
                client = Peer.Client(self, pconfig)
                client.start()
                clients.append(client)

        while self.running:
            time.sleep(0.5)

        # shutdown
        for client in clients:
            client.running = False
        server.shutdown()
