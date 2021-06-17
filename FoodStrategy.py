import numpy as np
import util
import config

class FoodStrategy(object):
    def __init__(self, raw_config):
        # Load learner parameters from learner.json
        self.config = config.LearnerConfig(raw_config)
        self.runtime_config = config.RuntimeConfig(raw_config)
        self.num_actions = self.config.num_actions()

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
        states = util.construct_borad(data)

        # Choose a random direction to move in
        possible_moves = ["up", "down", "left", "right"]

        block_arr = util.determine_block_array(data, states, self.num_actions)

        def non_block_dir_with_max_routes():
            for dir in range(len(block_arr)):
                if not block_arr[dir]:
                    possible_routes = util.calculate_possible_routes(head['y'], head['x'], dir, w, h, states)
                    if possible_routes > max_routes:
                        max_routes_dir = dir
            return max_routes_dir

        foods = [] # list of tuple
        if 'food' in board:
            for pos in board['food']:
                foods.append((pos['y'], pos['x']))

        closest_food = self.find_closest_food(head['y'], head['x'], h, w, foods, states)
        if closest_food is None:
            # cannot reach any food
            return possible_moves[non_block_dir_with_max_routes()]

        path = self.path_to_closest_food(head['y'], head['x'], h, w, closest_food, states) # list of direction

        ideal_move = path[0]
        if block_arr[ideal_move]:
            # First move to the closest food is block
            # chose the move with max possible routes
            max_routes_dir = 0
            max_routes = -1
            ideal_move = non_block_dir_with_max_routes()

        elif util.calculate_possible_routes(head['y'], head['x'], ideal_move, w, h, states) < 11:
            # First move is possible but towards to a small close area
            # chose the move with max possible routes
            ideal_move = non_block_dir_with_max_routes()

        return possible_moves[ideal_move]

    def find_closest_food(self, head_y, head_x, h, w, foods, states):
        queue = []
        visited = set()
        queue.append((head_y, head_x))
        visited.add((head_y, head_x))
        while len(queue) != 0:
            pos = queue.pop(0)
            if pos in foods:
                return pos
            nears = self.getAvailableNext(pos, h, w, states)
            for near in nears:
                if near not in visited:
                    queue.append(near)
                    visited.add(near)
        return None # cannot reach any food

    def path_to_closest_food(self, head_y, head_x, h, w, closest_food, states):
        # dfs
        path = []
        visited = set()
        def path_dfs_helper(y, x):

            if not util.isInsideBoundary(y, x, w, h) or states[y, x] == 1:
                return False

            if (y, x) in visited:
                return False

            if (y, x) == closest_food:
                return True

            visited.add((y, x))

            path.append(0)
            if path_dfs_helper(y + 1, x):
                return True
            path.pop()

            path.append(1)
            if path_dfs_helper(y - 1, x):
                return True
            path.pop()

            path.append(2)
            if path_dfs_helper(y, x - 1):
                return True
            path.pop()

            path.append(3)
            if path_dfs_helper(y, x + 1):
                return True
            path.pop()

        path_dfs_helper(head_y, head_x)

        return path

    def getAvailableNext(self, pos, h, w, states):
        possible_nears = []
        if util.isInsideBoundary(pos[0] + 1, pos[1], w, h) and states[pos[0] + 1, pos[1]] not in (1, 3):
            possible_nears.append((pos[0] + 1, pos[1]))
        if util.isInsideBoundary(pos[0] - 1, pos[1], w, h) and states[pos[0] - 1, pos[1]] not in (1, 3):
            possible_nears.append((pos[0] - 1, pos[1]))
        if util.isInsideBoundary(pos[0], pos[1] - 1, w, h) and states[pos[0], pos[1] - 1] not in (1, 3):
            possible_nears.append((pos[0], pos[1] - 1))
        if util.isInsideBoundary(pos[0], pos[1] + 1, w, h) and states[pos[0], pos[1] + 1] not in (1, 3):
            possible_nears.append((pos[0], pos[1] + 1))
        return possible_nears






