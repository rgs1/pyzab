""" a peer's state (and transitions across states) """


_states_by_name = {
    "LOOKING": 0,
    "FOLLOWING": 1,
    "LEADING": 2,
}
_states_by_num = {num: name for name, num in _states_by_name.items()}


class State(object):
    LOOKING = _states_by_name["LOOKING"]
    FOLLOWING = _states_by_name["FOLLOWING"]
    LEADING = _states_by_name["LEADING"]
