""" a peer's vote """

from collections import namedtuple
import json


class Vote(namedtuple('Vote', 'myid mystate proposed_id zxid')):
    """
    Used in a FastLeaderElection to propose a leader (or to broadcast the current one).

    Note: zxid refer's to the (proposed or current) leader's zxid
    """
    def __str__(self):
        return json.dumps(self._asdict())

    @classmethod
    def parse(cls, vstr):
        """
        Given a valid JSON repr of a Vote, returns the corresponding Vote object
        """
        vd = json.loads(vstr)
        return Vote(vd["myid"], vd["mystate"], vd["proposed_id"], vd["zxid"])
