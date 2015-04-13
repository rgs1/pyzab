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


class PeerHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        data = read_string(self.request)
        cur_thread = threading.current_thread()
        logging.info("Received vote from client: %s", data)
        vote = Vote(
            self.server.peer_config.myid,
            State.LOOKING,
            self.server.peer_config.myid,
            State.LOOKING
        )
        self.request.sendall(write_string(str(vote)))


class PeerServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    allow_reuse_address = True
    peer_config = None


class Peer(threading.Thread):
    """
    A peer receives connections from peers w/ > id and connects to peers w/
    a lower id.

    It then sends & receives votes until a leader is elected.
    """

    def __init__(self, confs):
        """ parse conf """
        super(Peer, self).__init__()
        self.setDaemon(True)

        self.running = False
        self.config = Config.parse(confs)

    def run(self):
        self.running = True

        server = PeerServer(self.config.host_port, PeerHandler)
        server.peer_config = self.config
        ip, port = server.server_address

        self.name = "Peer({}:{})".format(ip, port)

        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.name = "PeerServer({}:{})".format(ip, port)
        server_thread.daemon = True
        server_thread.start()

        logging.info("Server loop running in thread: %s", server_thread.name)

        for peer in self.config.peers:
            if self.config.myid > peer.peer_id:
                logging.info("Connecting to peer %d (myid=%d)", peer.peer_id, self.config.myid)
                vote = Vote(self.config.myid, State.LOOKING, self.config.myid, State.LOOKING)
                self.connect(peer.host, peer.port, str(vote))

        while self.running:
            time.sleep(0.5)

        server.shutdown()

    def connect(self, ip, port, message):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))
        try:
            sock.sendall(write_string(message))
            response = read_string(sock)
            logging.info("Received reply vote: %s", response)
        finally:
            sock.close()
