""" config parser """

import re


class PeerConfig(object):
    """
    Contains a peer's coordinates
    """
    def __init__(self, peer_id, host, election_port, zab_port=None, client_port=None):
        self.peer_id, self.host, self.election_port = peer_id, host, election_port
        self.zab_port, self.client_port = zab_port, client_port

    @property
    def election_endpoint(self):
        return self.host, self.election_port


class Config(object):
    """
    A representation of peers in a config file/str
    """
    def __init__(self, peers, myid):
        self.me = None
        self.peers = []
        self.myid = myid

        for peer in peers:
            if peer.peer_id == self.myid:
                self.me = peer
            else:
                self.peers.append(peer)

    @property
    def election_endpoint(self):
        return self.me.election_endpoint

    @classmethod
    def parse(cls, confs):
        """
        Parses a config like:

        server.0=localhost:%d
        server.1=localhost:%d
        server.2=localhost:%d
        server.3=localhost:%d
        server.4=localhost:%d

        myid=%d

        and returns the corresponding Config object.
        """
        myid = -1
        peers = []
        for line in confs.split("\n"):
            line = line.lstrip(" ").rstrip(" ")
            if line.startswith("server"):
                try:
                    key, value = line.split("=")
                    _, peer_id = key.split(".")
                    host, port = value.rsplit(":", 1)
                    peer = PeerConfig(int(peer_id), host, int(port))
                    peers.append(peer)
                except ValueError:
                    raise ValueError("Bad config line: %s" % line)
            elif line.startswith("myid"):
                key, value = line.split("=")
                try:
                    myid = int(value)
                except ValueError:
                    raise ValueError("Bad config line: %s" % line)
            elif re.match("^ *$", line):
                continue
            else:
                raise ValueError("Bad config line: %s" % line)

        return Config(peers, myid)
