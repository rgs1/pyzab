""" peer test cases """

import logging
import time
import unittest

from pyzab.peer import Peer


class PeerTestCase(unittest.TestCase):
    """ test Peer class """

    def setUp(self):
        pass

    def test_basic(self):
        logging.basicConfig(level=logging.INFO)

        conf_template = """
           server.0=localhost:%d
           server.1=localhost:%d
           server.2=localhost:%d
           server.3=localhost:%d
           server.4=localhost:%d

           myid=%d
        """

        # TODO: assign available ports
        ports = [port for port in range(3000, 3005)]

        # start peers
        peers = []
        for peer_id in range(0, 5):
            confs = conf_template % (tuple(ports) + tuple([peer_id]))
            peer = Peer(confs)
            peer.start()
            peers.append(peer)

        # TODO: wait for election to happen
        waiting = True
        while waiting:
            waiting = False
            for peer in peers:
                if len(peer.votes) == len(peers):
                    peer.running = False
                else:
                    waiting = True
            if waiting:
                time.sleep(1)

        # wait for threads to exit
        while any(peer.isAlive() for peer in peers): pass

        self.assertTrue(True)
