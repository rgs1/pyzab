""" FastLeaderElection algorithm """

from collections import defaultdict

import operator


class FastLeaderElection(object):
    """
    Given a list of config.PeerConfig and a majority of votes, find the leader
    """

    def __init__(self, peers):
        self.peers_by_id = dict((p.peer_id, p) for p in peers)
        self.votes = set()

    @property
    def peers(self):
        return self.peers_by_id.values()

    def update(self, vote):
        """
        updates the vote
        """
        self.votes.add(vote)

    @property
    def has_quorum(self):
        """
        can the election take place?
        """
        return len(self.votes) >= self.quorum

    @property
    def quorum(self):
        """
        the minimum number of peers that must be present for an election to be valid
        """
        return (len(self.peers) / 2) + 1

    @property
    def leader(self):
        """
        returns the elected peer (None, if no quorum or peers haven't agreed)

        TODO: we should protect self.votes w/ a lock and take it during this method
        """
        if not self.has_quorum:
            return None

        tally = defaultdict(int)
        for vote in self.votes:
            tally[vote.proposed_id] += 1

        results = sorted(tally.items(), key=operator.itemgetter(1), reverse=True)
        leader_id, leader_count = results[0]
        # is there a tie?
        if tally.values().count(leader_count) > 1:
            return None

        assert leader_id in self.peers_by_id
        return self.peers_by_id[leader_id]
