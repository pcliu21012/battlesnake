import util
import config as cf
import HeadLogic as hl

class HeadStrategy(object):
    def __init__(self, raw_config):
        # Load learner parameters from learner.json
        config = cf.LearnerConfig(raw_config)
        self.num_actions = config.num_actions
        self.small_area_threshold = 11
        self.headLogic = hl.HeadLogic()

    def start(self, data):
        pass

    def end(self, data):
        pass

    def move(self, data):
        # 0 = empty
        # 1 = barrier
        # 2 = food
        # 3 = head
        board = data['board']
        h = board['height']
        w = board['width']
        you = data['you']
        head = you['head']

        states = data['states']
        block_arr = data['block_arr']
        routes = data['routes']

        # Choose a random direction to move in
        possible_moves = ["up", "down", "left", "right"]

        # head move logic
        ideal_move = self.headLogic.head_move(data, block_arr, routes)
        if ideal_move is not None:
            return possible_moves[ideal_move]

        return None