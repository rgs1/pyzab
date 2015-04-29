""" vote test cases """

import unittest

from pyzab.config import PeerConfig
from pyzab.fle import FastLeaderElection
from pyzab.state import State
from pyzab.vote import Vote


class FastLeaderElectionTestCase(unittest.TestCase):
    """ test FLE """

    def setUp(self):
        pass

    def test_basic(self):
        peers = [
            PeerConfig(0, '127.0.0.1', 3000, 0, 0),
            PeerConfig(1, '127.0.0.1', 3001, 0, 0),
            PeerConfig(2, '127.0.0.1', 3002, 0, 0),
        ]

        v0 = Vote(0, State.LOOKING, 0, 0x0)
        v1 = Vote(1, State.LOOKING, 0, 0x0)
        v2 = Vote(2, State.LOOKING, 2, 0x0)

        fle = FastLeaderElection(peers)

        self.assertEquals(fle.quorum, 2)
        self.assertFalse(fle.has_quorum)
        self.assertTrue(fle.leader_id == None)

        fle.update(v0)
        fle.update(v1)
        fle.update(v2)

        self.assertTrue(fle.has_quorum)
        self.assertTrue(fle.leader_id == 0)
