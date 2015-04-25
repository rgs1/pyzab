""" vote test cases """

import unittest

from pyzab.state import State
from pyzab.vote import Vote


class VoteTestCase(unittest.TestCase):
    """ test Vote class """

    def setUp(self):
        pass

    def test_serialize_deserialize(self):
        v1 = Vote(1, State.LOOKING, 3, 0xdeadbeef)
        v2 = Vote.parse(str(v1))
        self.assertTrue(v1 == v2)

    def test_comparisons(self):
        # biggest zxid wins
        self.assertTrue(
            Vote(0, State.LOOKING, 0, 0x1) > Vote(1, State.LOOKING, 1, 0x0)
        )
        # biggest zxid wins
        self.assertTrue(
            Vote(0, State.LOOKING, 0, 0x2) < Vote(1, State.LOOKING, 1, 0x3)
        )
        # same zxid but smaller id wins
        self.assertTrue(
            Vote(0, State.LOOKING, 0, 0x5) > Vote(1, State.LOOKING, 1, 0x5)
        )
