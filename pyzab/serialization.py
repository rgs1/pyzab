""" serialization helpers """

import struct


int_struct = struct.Struct('!i')


def read_string(sock):
    """ reads (i32) length and returns (str, offset) """
    lenb = sock.recv(4)
    if not lenb:
        return None

    lenb = int_struct.unpack_from(lenb, 0)[0]
    if lenb < 0:
        raise ValueError("bad str")
    data = sock.recv(lenb)
    return data.decode('utf-8')


def write_string(message):
    """ prepends the (i32) length to message """
    message = str(message)
    return int_struct.pack(len(message)) + message
