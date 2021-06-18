import os
import random
import json
import cherrypy
import util

import config as cf
import QLearner as ql

class RememberState(object):
    def __init__(self, data):
        self.health = data['you']['health']
        self.length = data['you']['length']


class QLearnerStrategy(object):
    def __init__(self, raw_config):
        # Runtime default settings
        self.health_threshold = {}
        self.prev_state = {}

        # Load learner parameters from learner.json
        self.config = cf.LearnerConfig(raw_config)
        self.runtime_config = cf.RuntimeConfig(raw_config)
        self.reward_config = cf.RewardConfig(raw_config)
        self.is_learning_mode = self.runtime_config.is_learning_mode

        # Initialize the QLearner
        self.learner = ql.QLearner(
            num_states=self.config.num_states,
            num_actions=self.config.num_actions,
            alpha=self.config.alpha,
            gamma=self.config.gamma,
            rar=self.config.rar,
            radr=self.config.radr,
            dyna=self.config.dyna,
            verbose=self.config.verbose,
        )
        if self.config.Q:
            if os.path.isfile(self.config.Q):
                self.learner.load(self.config.Q)

    def start(self, data):
        # Start the game with initial setup
        game_id = util.unique_id(data)
        self.learner.start(game_id)
        self.health_threshold[game_id] = self.runtime_config.health_threshold

    def move(self, data):

        # Choose a random direction to move in
        possible_moves = ["up", "down", "left", "right"]
        #move = random.choice(possible_moves)

        # Construct states and query learner
        game_id = util.unique_id(data)
        if game_id not in self.prev_state:
            state, block_arr = util.discretize(data, self.config.num_actions, self.health_threshold[game_id])
            action = self.learner.querysetstate(state, block_arr, game_id)
        else:
            # Calculate reward based on previous state
            r = self.__calc_reward(data, game_id)

            state, block_arr = util.discretize(data, self.config.num_actions, self.health_threshold[game_id])
            if self.is_learning_mode:
                action = self.learner.query(state, r, block_arr, game_id)
            else:
                action = self.learner.querysetstate(state, block_arr, game_id)
        move = possible_moves[action]

        # Memorize previous state
        self.prev_state[game_id] = RememberState(data)

        # print(f"THIS TURN({data['turn']})")
        # print(f"THIS MOVE({game_id}): {move}")
        # print(f"THIS STATE({state})")
        return move

    def end(self, data):
        game_id = util.unique_id(data)
        # Punish or reward when game end in learning mode
        if self.is_learning_mode and game_id in self.prev_state:
            # Calculate reward based on previous state
            r = self.__calc_reward(data, game_id, is_end=True)
            state, block_arr = util.discretize(data, self.config.num_actions, self.health_threshold[game_id])
            _ = self.learner.query(state, r, block_arr, game_id)
            # print(self.learner.dump(self.config.Q))

        # Clean up to save memory
        self.prev_state.pop(game_id, None)
        self.health_threshold.pop(game_id, None)
        self.learner.end(game_id)

        if self.runtime_config.dump_at_end:
            self.dump()

    def dump(self):
        # This function is called when you want to dump the Q tablel to file
        print(self.learner.dump(self.config.Q))
        return "ok"

    def __calc_reward(self, data, game_id, is_end=False):
        curr_s = RememberState(data)
        prev_s = self.prev_state[game_id]
        r = self.reward_config.default

        # Starving to die
        if curr_s.health == 0 or (is_end and util.is_die(data)):
            print("!!!!I'm die!!!!")
            r = self.reward_config.die
        elif curr_s.health >= prev_s.health:
            r = self.reward_config.eat_food
            # After eating food, decay the health threshold
            health_t_decay = self.runtime_config.health_threshold_decay
            self.health_threshold[game_id] *= health_t_decay
        elif prev_s.health <= self.health_threshold[game_id]:
            r = self.reward_config.low_health
        return r