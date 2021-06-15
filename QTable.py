import json

import numpy as np


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


class QTableMap(object):
    """
    This is a map based Q learner table.
    """
    def __init__(
        self,
        num_states,
        num_actions
    ):
        """
        Constructor method
        """
        self.Q = {}
        self.num_actions = num_actions

    def get(self, state, action=None):
        # print("{}, {}".format(state, action))
        if state in self.Q:
            if action is not None:
                return self.Q[state][action]
            else:
                return self.Q[state]
        else:
            if action is not None:
                return 0.0
            else:
                return np.zeros(self.num_actions)

    def update(self, state, action, val):
        if state not in self.Q:
            self.Q[state] = np.zeros(self.num_actions)
        self.Q[state][action] = val

    def load(self, fname):
        with open(fname) as f:
            data = json.load(f)
            self.Q = np.array(data)
            # print(self.Q)

    def dump(self):
        fname = 'qtable.json'
        with open(fname, 'w') as f:
            json.dump(self.Q, f, cls=NumpyEncoder)
        return "Writing QTable into {}".format(fname)


class QTableArray(object):
    """
    This is a map based Q learner table.
    """
    def __init__(
        self,
        num_states,
        num_actions
    ):
        """
        Constructor method
        """
        self.Q = np.zeros((num_states, num_actions))

    def get(self, state, action=None):
        if action is not None:
            return self.Q[state, action]
        else:
            return self.Q[state]

    def update(self, state, action, val):
        self.Q[state, action] = val

    def load(self, fname):
        with open(fname) as f:
            data = json.load(f)
            self.Q = np.array(data)

    def dump(self):
        fname = 'qtable.json'
        with open(fname, 'w') as f:
            json.dump(self.Q, f, cls=NumpyEncoder)
        return "Writing QTable into {}".format(fname)
