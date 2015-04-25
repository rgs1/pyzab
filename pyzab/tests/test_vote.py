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
