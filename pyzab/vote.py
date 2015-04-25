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

    def __gt__(self, other):
        """
        Bigger zxid wins. if that's tied, smaller id breaks the tie.
        """
        if self.zxid > other.zxid:
            return True
        if self.zxid == other.zxid and self.proposed_id < other.proposed_id:
            return True
        return False

    def __lt__(self, other):
        return other > self

    @classmethod
    def parse(cls, vstr):
        """
        Given a valid JSON repr of a Vote, returns the corresponding Vote object
        """
        vd = json.loads(vstr)
        return Vote(
            int(vd["myid"]),
            int(vd["mystate"]),
            int(vd["proposed_id"]),
            vd["zxid"] if type(vd["zxid"]) == int else int(vd["zxid"], 16)
        )
