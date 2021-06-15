import json

import numpy as np

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
        if state in self.Q:
            if action:
                return self.Q[state][action]
            else:
                return self.Q[state]
        else:
            if action:
                return 0.0
            else:
                return np.zeros(self.num_actions)

    def update(self, state, action, val):
        if state not in self.Q:
            self.Q[state] = np.array(self.num_actions)
        self.Q[state][action] = val

    def load(self, data):
        self.Q = data

    def dumps(self):
        return json.dumps(self.Q)


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
        if action:
            return self.Q[state, action]
        else:
            return self.Q[state]

    def update(self, state, action, val):
        self.Q[state, action] = val

    def load(self, data):
        self.Q = np.array(data)

    def dumps(self):
        return json.dumps(self.Q.tolist())
