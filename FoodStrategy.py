import util
import config as cf
import numpy as np

class State(object):
    def __init__(self, pos, direct, parent):
        self.pos = pos
        self.direct = direct
        self.parent = parent

class FoodStrategy(object):
    def __init__(self, raw_config):
        # Load learner parameters from learner.json
        config = cf.LearnerConfig(raw_config)
        self.num_actions = config.num_actions
        self.small_area_threshold = 11

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
        routes = [-1, -1, -1, -1]

        # Choose a random direction to move in
        possible_moves = ["up", "down", "left", "right"]

        block_arr = util.determine_block_array(data, states, self.num_actions)

        # Find the non-block direction which will have the maximum routes
        max_routes_dir = 0
        max_routes = -1
        for a in range(self.num_actions):
            if not block_arr[a]:
                possible_routes = util.calculate_possible_routes(head['y'], head['x'], a, w, h, states)
                routes[a] = possible_routes
                if possible_routes > max_routes:
                    max_routes_dir = a
                    max_routes = possible_routes

        foods = [] # list of tuple
        if 'food' in board:
            for pos in board['food']:
                foods.append((pos['y'], pos['x']))

        closest_food = self.find_closest_food(head['y'], head['x'], h, w, foods, states)
        if closest_food is None:
            # cannot reach any food
            return possible_moves[max_routes_dir]

        path = self.path_to_closest_food(head['y'], head['x'], h, w, closest_food, states) # list of direction

        ideal_move = path[0]
        if block_arr[ideal_move]:
            # First move to the closest food is block
            # chose the move with max possible routes
            ideal_move = max_routes_dir

        elif routes[ideal_move] < self.small_area_threshold:
            # First move is possible but towards to a small close area
            # chose the move with max possible routes
            ideal_move = max_routes_dir

        return possible_moves[ideal_move]

    def find_closest_food(self, head_y, head_x, h, w, foods, states):
        queue = []
        visited = set()
        queue.append((head_y, head_x))
        visited.add((head_y, head_x))
        while len(queue) != 0:
            pos = queue.pop(0)
            nears, _ = self.getAvailableNext(pos, h, w, states)
            for near in nears:
                if near in visited:
                    continue
                if pos in foods:
                    return pos
                queue.append(near)
                visited.add(near)
        return None # cannot reach any food

    def path_to_closest_food(self, head_y, head_x, h, w, closest_food, states):
        # BFS to find the closest route
        visited = set()
        queue = []
        visited.add((head_y, head_x))
        queue.append(State(pos=(head_y, head_x), direct=None, parent=None))
        while len(queue) > 0:
            s = queue.pop(0)
            next_pos, next_dirs = self.getAvailableNext(s.pos, h, w, states)
            for npos, nd in zip(next_pos, next_dirs):
                if npos in visited:
                    continue
                if npos == closest_food:
                    # Break the loop and return the path
                    path = []
                    cur = State(pos=npos, direct=nd, parent=s)
                    while cur.direct is not None:
                        path.append(cur.direct)
                        cur = cur.parent
                    path.reverse()
                    return path
                queue.append(State(pos=npos, direct=nd, parent=s))
                visited.add(npos)
        return []

    def getAvailableNext(self, pos, h, w, states):
        possible_nears = []
        possible_dirs = []
        if util.isInsideBoundary(pos[0] + 1, pos[1], w, h) and states[pos[0] + 1, pos[1]] not in (1, 3):
            possible_nears.append((pos[0] + 1, pos[1]))
            possible_dirs.append(0)
        if util.isInsideBoundary(pos[0] - 1, pos[1], w, h) and states[pos[0] - 1, pos[1]] not in (1, 3):
            possible_nears.append((pos[0] - 1, pos[1]))
            possible_dirs.append(1)
        if util.isInsideBoundary(pos[0], pos[1] - 1, w, h) and states[pos[0], pos[1] - 1] not in (1, 3):
            possible_nears.append((pos[0], pos[1] - 1))
            possible_dirs.append(2)
        if util.isInsideBoundary(pos[0], pos[1] + 1, w, h) and states[pos[0], pos[1] + 1] not in (1, 3):
            possible_nears.append((pos[0], pos[1] + 1))
            possible_dirs.append(3)
        return possible_nears, possible_dirs
