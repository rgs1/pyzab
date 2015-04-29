""" peer test cases """

import logging
import time
import unittest

from pyzab.voter import Voter


class VoterTestCase(unittest.TestCase):
    """ test Voter class """

    def setUp(self):
        pass

    def test_basic(self):
        logging.basicConfig(level=logging.INFO)

        self.run_election(
            zxids=[0x0, 0x0, 0x0, 0x0, 0x0],
            expected_leader_id=0
        )

        self.run_election(
            zxids=[0x0, 0x100, 0x100, 0x100, 0x100],
            expected_leader_id=1
        )

        self.run_election(
            zxids=[0x100, 0x100, 0x100, 0x0, 0x0],
            expected_leader_id=0
        )

        self.run_election(
            zxids=[0x0, 0x0, 0x100, 0x100, 0x100],
            expected_leader_id=2
        )

    def run_election(self, zxids, expected_leader_id):
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

        # start voters
        voters = []
        for peer_id in range(0, 5):
            confs = conf_template % (tuple(ports) + tuple([peer_id]))
            voters.append(Voter(confs, zxid=zxids[peer_id]))

        # wait for all voters to find the elected leader
        election_done = False
        for _ in xrange(0, 5):
            if all(voter.leader_id is not None for voter in voters):
                election_done = True
                break
            time.sleep(1.0)

        self.assertTrue(election_done)

        # wait for threads to exit
        for voter in voters:
            voter.running = False
        while any(voter.isAlive() for voter in voters): pass

        self.assertTrue(all(voter.leader_id == expected_leader_id for voter in voters))
