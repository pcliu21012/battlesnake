import numpy as np
class HeadLogic:
    def __init__(self):
        self.small_area_threshold = 11

    def get_heads_position(self, data):
        board = data['board']
        my_id = data['you']['id']
        heads = []
        lengths = []
        if 'snakes' in board:
            for snake in board['snakes']:
                if not snake['id'] == my_id:
                    head = snake['head']
                    heads.append((head['y'], head['x']))
                    lengths.append(len(snake['body']))
        return heads, lengths

    def head_move(self, data, block_arr, routes):
        other_heads, other_lengths = self.get_heads_position(data)
        my_head = (data['you']['head']['y'], data['you']['head']['x'])
        my_length = len(data['you']['body'])
        move_scores = [0, 0, 0, 0]
        for head, length in zip(other_heads, other_lengths):
            if self.is_diagonal(head, my_head):
                if length >= my_length:
                    # dodge
                    move_scores = self.head_dodge_move(head, my_head, move_scores)
                else:
                    # attack
                    move_scores = self.head_attack_move(head, my_head, move_scores)
            if self.is_opposite(head, my_head):
                if length >= my_length:
                    # dodge
                    move_scores = self.opposite_head_dodge_move(head, my_head, move_scores)
                else:
                    # attack
                    move_scores = self.opposite_head_attack_move(head, my_head, move_scores)

        for a in range(len(block_arr)):
            if block_arr[a]:
                move_scores[a] = 0

        if sum(move_scores) == 0:
            return None

        move = np.argmax(move_scores)
        if routes[move] < self.small_area_threshold:
            return None

        return move


    def is_diagonal(self, head, my_head):
        return abs(head[0] - my_head[0]) == 1 and abs(head[1] - my_head[1]) == 1

    def is_opposite(self, head, my_head):
        return (abs(head[0] - my_head[0]) == 2 and abs(head[1] - my_head[1]) == 0) or (abs(head[0] - my_head[0]) == 0 and abs(head[1] - my_head[1]) == 2)

    def head_dodge_move(self, head, my_head, move_scores):
        if head[0] - my_head[0] == 1 and head[1] - my_head[1] == 1:
            # up right, dodge down or left
            move_scores[1] += 1
            move_scores[2] += 1
        elif head[0] - my_head[0] == 1 and head[1] - my_head[1] == -1:
            # up left, dodge down or right
            move_scores[1] += 1
            move_scores[3] += 1
        elif head[0] - my_head[0] == -1 and head[1] - my_head[1] == 1:
            # down right, dodge up or left
            move_scores[0] += 1
            move_scores[2] += 1
        else:
            # down left, dodge down or right
            move_scores[0] += 1
            move_scores[3] += 1
        return move_scores

    def head_attack_move(self, head, my_head, move_scores):
        if head[0] - my_head[0] == 1 and head[1] - my_head[1] == 1:
            # up right, attack up or right
            move_scores[0] += 1
            move_scores[3] += 1
        elif head[0] - my_head[0] == 1 and head[1] - my_head[1] == -1:
            # up left, attack up or left
            move_scores[0] += 1
            move_scores[2] += 1
        elif head[0] - my_head[0] == -1 and head[1] - my_head[1] == 1:
            # down right, attack down or right
            move_scores[1] += 1
            move_scores[3] += 1
        else:
            # down left, attack down or left
            move_scores[1] += 1
            move_scores[2] += 1
        return move_scores

    def opposite_head_dodge_move(self, head, my_head, move_scores):
        if head[0] - my_head[0] == 2 and head[1] - my_head[1] == 0:
            # up
            move_scores[1] += 1
            move_scores[2] += 1
            move_scores[3] += 1
        elif head[0] - my_head[0] == -2 and head[1] - my_head[1] == 0:
            # down
            move_scores[0] += 1
            move_scores[2] += 1
            move_scores[3] += 1
        elif head[0] - my_head[0] == 0 and head[1] - my_head[1] == -2:
            # left
            move_scores[0] += 1
            move_scores[1] += 1
            move_scores[3] += 1
        else:
            # right
            move_scores[0] += 1
            move_scores[1] += 1
            move_scores[2] += 1
        return move_scores

    def opposite_head_attack_move(self, head, my_head, move_scores):
        if head[0] - my_head[0] == 2 and head[1] - my_head[1] == 0:
            # up
            move_scores[0] += 1
        elif head[0] - my_head[0] == -2 and head[1] - my_head[1] == 0:
            # down
            move_scores[1] += 1
        elif head[0] - my_head[0] == 0 and head[1] - my_head[1] == -2:
            # left
            move_scores[2] += 1
        else:
            # right
            move_scores[3] += 1
        return move_scores