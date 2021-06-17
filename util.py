import numpy as np

def discretize(data, states, num_actions):
    return discretize_possible_routes(data, states, num_actions)

def is_die(data):
    board = data['board']
    h = board['height']
    w = board['width']
    you = data['you']
    head = you['head']
    if not isInsideBoundary(head['y'], head['x'], w, h):
        return True
    if 'snakes' in board:
        for snake in board['snakes']:
            for pos in snake['body']:
                if pos['y'] == head['y'] and pos['x'] == head['x']:
                    return True
    for pos in you['body']:
        if pos['y'] == head['y'] and pos['x'] == head['x']:
            return True
    return False


def isInsideBoundary(y, x, w, h):
    if y < 0 or x < 0 or y >= h or x >= w:
        return False
    return True

# Construct the game board based on data
def construct_borad(data):
    # 0 = empty
    # 1 = barrier
    # 2 = food
    # 3 = head
    board = data['board']
    h = board['height']
    w = board['width']
    states = np.zeros((h, w))

    if 'snakes' in board:
        for snake in board['snakes']:
            for pos in snake['body']:
                if isInsideBoundary(pos['y'], pos['x'], w, h):
                    states[pos['y'], pos['x']] = 1
    if 'food' in board:
        for pos in board['food']:
            states[pos['y'], pos['x']] = 2
    you = data['you']
    for pos in you['body']:
        if isInsideBoundary(pos['y'], pos['x'], w, h):
            states[pos['y'], pos['x']] = 1
    head = you['head']
    if isInsideBoundary(head['y'], head['x'], w, h):
        states[head['y'], head['x']] = 3
    return states

# Determine block array
def determine_block_array(data, states, num_actions):
    # Block_arr inidicates if there is an immediate block at earch direction. ["up", "down", "left", "right"]
    # This is extra constraint information, not part fo the state
    board = data['board']
    h = board['height']
    w = board['width']
    you = data['you']
    head = you['head']
    block_arr = np.zeros(num_actions, dtype=bool)

    tail_map = {}
    if 'snakes' in board:
        for snake in board['snakes']:
            tail_pos = snake['body'][-1]
            # Don't chase our tail if length too short
            if snake['id'] == you['id'] and snake['length'] <= 3:
                continue
            # Don't chase tail if the snake just got a food
            if snake['health'] == 100:
                continue
            tail_map["{},{}".format(tail_pos['y'], tail_pos['x'])] = True

    def is_tail(y, x):
        return "{},{}".format(y, x) in tail_map

    direction_pos = (
        (head['y'] + 1, head['x']),
        (head['y'] - 1, head['x']),
        (head['y'], head['x'] - 1),
        (head['y'], head['x'] + 1)
    )
    for i in range(len(direction_pos)):
        (y, x) = direction_pos[i]
        if (isInsideBoundary(y, x, w, h) and states[y, x] == 1 and not is_tail(y, x)) or not isInsideBoundary(y, x, w, h):
            block_arr[i] = True

    return block_arr

# Discretize state based on entire directional area
def discretize_entire_directional_area(data, num_actions, health_threshold):
    # 0 = empty
    # 1 = barrier
    # 2 = food
    # 3 = head
    board = data['board']
    h = board['height']
    w = board['width']
    you = data['you']
    head = you['head']
    states = construct_borad(data)

    block_arr = determine_block_array(data, states, num_actions)

    # Barrier ration for four directions (0-9)
    up_ratio = 1
    down_ratio = 1
    left_ratio = 1
    right_ratio = 1
    if not head['y'] == h - 1:
        up_ratio = np.sum(states[head['y'] + 1 : h, :] == 1) / (w * (h - head['y'] - 1))
    if not head['y'] == 0:
        down_ratio = np.sum(states[0 : head['y'] - 1, :] == 1) / (w * head['y'])
    if not head['x'] == 0:
        left_ratio = np.sum(states[:, 0 : head['x'] - 1] == 1) / (head['x'] * h)
    if not head['x'] == w - 1:
        right_ratio = np.sum(states[:, head['x'] + 1 : w] == 1) / ((w - head['x'] - 1) * h)

    # Food signal for four direction (0-1)
    up_food = 1 if np.sum(states[head['y'] + 1 : h, :] == 2) > 0 else 0
    down_food = 1 if np.sum(states[0 : head['y'] - 1, :] == 2) > 0 else 0
    left_food = 1 if np.sum(states[:, 0 : head['x'] - 1] == 2) > 0 else 0
    right_food = 1 if np.sum(states[:, head['x'] + 1 : w] == 2) > 0 else 0

    # Low health indicator (0-1)
    is_dying = 0 if you['health'] > health_threshold else 1

    state_score = round(up_ratio * 10 - 0.5) + round(down_ratio * 10 - 0.5) * pow(10, 1) + round(left_ratio * 10 - 0.5) * pow(10, 2) + round(right_ratio * 10 - 0.5) * pow(10, 3)
    state_score += up_food * pow(10, 4) + down_food * pow(10, 4) * pow(2, 1) + left_food * pow(10, 4) * pow(2, 2)  + right_food * pow(10, 4) * pow(2, 3)
    state_score += is_dying * pow(10, 4) * pow(2, 4)

    return state_score, block_arr

# Discretize state based on narrow directional area
def discretize_narrow_directional_area(data, num_actions, health_threshold):
    # 0 = empty
    # 1 = barrier
    # 2 = food
    # 3 = head
    board = data['board']
    h = board['height']
    w = board['width']
    you = data['you']
    head = you['head']
    states = construct_borad(data)

    block_arr = determine_block_array(data, states, num_actions)

    def helper(h, w, y, x, n, dir):
        '''
        Calculate the top/down/left/right range based on the head position (x, y) and direction
        :param h: Height of the map
        :type h: int
        :param w: Width of the map
        :type w: int
        :param y: y position of sneak head
        :type y: int
        :param x: x position of sneak head
        :type x: int
        :param n: side length of the n * n area toward given direction
        :type n: int
        :param dir: index of ["up", "down", "left", "right"]
        :type dir: int
        :return: (y1, y2, x1, x2) are the range of index that is inside the map. (y2, x2) are excluding end point of the range.
        : b is the number of block that is out side the map boundary.
        :rtype: int

        '''
        if dir == 0:
            # up
            h1 = y + 1
            h2 = y + 4
            w1 = w - 1
            w2 = w + 1
        elif dir == 1:
            # down
            h1 = y - 4
            h2 = y - 1
            w1 = w - 1
            w2 = w + 1
        elif dir == 2:
            # left
            h1 = y - 1
            h2 = y + 1
            w1 = w - 4
            w2 = w - 1
        else:
            # right
            h1 = y - 1
            h2 = y + 1
            w1 = w + 1
            w2 = w + 4

        y1 = max(h1, 0)
        y2 = min(h2 + 1, h)
        x1 = max(w1, 0)
        x2 = min(w2 + 1, w)

        b = n * n - (y2 - y1) * (x2 - x1)

        return y1, y2, x1, x2, b

    '''
    Ratio of available blocks in the 3 * 3 area toward of each direction.
    Area outside of boundary counts as block.
    '''
    n = 3
    # up
    y1, y2, x1, x2, b = helper(h, w, head['y'], head['x'], n, 0)
    up_ratio = (np.sum(states[y1 : y2, x1 : x2] == 1) + b) / pow(n, 2)

    # down
    y1, y2, x1, x2, b = helper(h, w, head['y'], head['x'], n, 1)
    down_ratio = (np.sum(states[y1 : y2, x1 : x2] == 1) + b) / pow(n, 2)

    # left
    y1, y2, x1, x2, b = helper(h, w, head['y'], head['x'], n, 2)
    left_ratio = (np.sum(states[y1 : y2, x1 : x2] == 1) + b) / pow(n, 2)

    # right
    y1, y2, x1, x2, b = helper(h, w, head['y'], head['x'], n, 3)
    right_ratio = (np.sum(states[y1 : y2, x1 : x2] == 1) + b) / pow(n, 2)

    is_dying = 0 if data['you']['health'] > health_threshold else 1

    up_food = 1 if np.sum(states[head['y'] + 1 : h, :] == 2) > 0 else 0
    down_food = 1 if np.sum(states[0 : head['y'] - 1, :] == 2) > 0 else 0
    left_food = 1 if np.sum(states[:, 0 : head['x'] - 1] == 2) > 0 else 0
    right_food = 1 if np.sum(states[:, head['x'] + 1 : w] == 2) > 0 else 0

    state_score = round(up_ratio * 10 - 0.5) + round(down_ratio * 10 - 0.5) * pow(10, 1) + round(left_ratio * 10 - 0.5) * pow(10, 2) + round(right_ratio * 10 - 0.5) * pow(10, 3)
    state_score += up_food * pow(10, 4) * pow(2, 1) + down_food * pow(10, 4) * pow(2, 2) + left_food * pow(10, 4) * pow(2, 3)  + right_food * pow(10, 4) * pow(2, 4)
    state_score += is_dying * pow(10, 4) * pow(2, 5)

    return state_score, block_arr

# Discretize state based on possible routes
def discretize_possible_routes(data, num_actions, health_threshold):
    # 0 = empty
    # 1 = barrier
    # 2 = food
    # 3 = head
    board = data['board']
    h = board['height']
    w = board['width']
    you = data['you']
    head = you['head']
    states = construct_borad(data)

    block_arr = determine_block_array(data, states, num_actions)

    def helper(head_y, head_x, dir):
        '''
        Calculate the number of possible routes to the boundary (or blocks) based on the head position (x, y) and direction
        :param y: y position of sneak head
        :type y: int
        :param x: x position of sneak head
        :type x: int
        :param dir: index of ["up", "down", "left", "right"]
        :type dir: int
        :return: the number of routes
        :rtype: int

        '''
        def getAvailableNext(pos):
            possible_nears = []
            if isInsideBoundary(pos[0] + 1, pos[1], w, h) and states[pos[0] + 1, pos[1]] not in (1, 3):
                possible_nears.append((pos[0] + 1, pos[1]))
            if isInsideBoundary(pos[0] - 1, pos[1], w, h) and states[pos[0] - 1, pos[1]] not in (1, 3):
                possible_nears.append((pos[0] - 1, pos[1]))
            if isInsideBoundary(pos[0], pos[1] - 1, w, h) and states[pos[0], pos[1] - 1] not in (1, 3):
                possible_nears.append((pos[0], pos[1] - 1))
            if isInsideBoundary(pos[0], pos[1] + 1, w, h) and states[pos[0], pos[1] + 1] not in (1, 3):
                possible_nears.append((pos[0], pos[1] + 1))
            return possible_nears

        if dir == 0:
            root_y = head_y + 1
            root_x = head_x
        elif dir == 1:
            root_y = head_y - 1
            root_x = head_x
        elif dir == 2:
            root_y = head_y
            root_x = head_x - 1
        else:
            root_y = head_y
            root_x = head_x + 1

        if not isInsideBoundary(root_y, root_x, w, h ) or states[root_y, root_x] == 1:
            return 0

        total_routes = 0
        queue = [] # list of position
        visited = {} # {position : count}
        root = (root_y, root_x)
        queue.append(root)
        visited.update({root : 1})
        while len(queue) != 0:
            pos = queue.pop()
            pos_count = visited[pos]
            nears = getAvailableNext(pos)
            for near in nears:
                if near in visited:
                    visited.update({near : visited[near] + pos_count})
                else:
                    queue.append(near)
                    visited.update({near : pos_count})
            if len(nears):
                # leaf (end point)
                total_routes = total_routes + pos_count

        return total_routes

    '''
    Ratio of available blocks in the 3 * 3 area toward of each direction.
    Area outside of boundary counts as block.
    '''
    # up
    up_routes = helper(head['y'], head['x'], 0)

    # down
    down_routes = helper(head['y'], head['x'], 1)

    # left
    left_routes = helper(head['y'], head['x'], 2)

    # right
    right_routes = helper(head['y'], head['x'], 3)

    sum_routes = up_routes + down_routes + left_routes + right_routes + 1
    up_ratio = up_routes / sum_routes
    down_ratio = down_routes / sum_routes
    left_ratio = left_routes / sum_routes
    right_ratio = right_routes / sum_routes

    is_dying = 0 if data['you']['health'] > health_threshold else 1

    up_food = 1 if np.sum(states[head['y'] + 1 : h, :] == 2) > 0 else 0
    down_food = 1 if np.sum(states[0 : head['y'] - 1, :] == 2) > 0 else 0
    left_food = 1 if np.sum(states[:, 0 : head['x'] - 1] == 2) > 0 else 0
    right_food = 1 if np.sum(states[:, head['x'] + 1 : w] == 2) > 0 else 0

    state_score = round(up_ratio * 10 - 0.5) + round(down_ratio * 10 - 0.5) * pow(10, 1) + round(left_ratio * 10 - 0.5) * pow(10, 2) + round(right_ratio * 10 - 0.5) * pow(10, 3)
    state_score += up_food * pow(10, 4) * pow(2, 1) + down_food * pow(10, 4) * pow(2, 2) + left_food * pow(10, 4) * pow(2, 3)  + right_food * pow(10, 4) * pow(2, 4)
    state_score += is_dying * pow(10, 4) * pow(2, 5)

    return state_score, block_arr
