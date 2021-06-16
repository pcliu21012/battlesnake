import os
import random
import json
import cherrypy
import util
import config

import QLearner as ql


class RememberState(object):
    def __init__(self, data):
        self.state = {
            'health': data['you']['health'],
            'length': data['you']['length'],
        }

    def health(self):
        return self.state['health']

    def length(self):
        return self.state['length']


"""
This is a simple Battlesnake server written in Python.
For instructions see https://github.com/BattlesnakeOfficial/starter-snake-python/README.md
"""
class Battlesnake(object):
    def __init__(self):
        # Runtime default settings
        self.health_threshold = {}
        self.prev_state = {}

        # Load learner parameters from learner.json
        with open('learner.json') as f:
            raw_config = json.load(f)
            self.config = config.LearnerConfig(raw_config)
            self.runtime_config = config.RuntimeConfig(raw_config)
            self.reward_config = config.RewardConfig(raw_config)

        self.is_learning_mode = self.runtime_config.is_learning_mode()

        # Initialize the QLearner
        self.learner = ql.QLearner(
            num_states=self.config.num_states(),
            num_actions=self.config.num_actions(),
            alpha=self.config.alpha(),
            gamma=self.config.gamma(),
            rar=self.config.rar(),
            radr=self.config.radr(),
            dyna=self.config.dyna(),
            verbose=self.config.verbose(),
        )
        if self.config.Q():
            if os.path.isfile(self.config.Q()):
                self.learner.load(self.config.Q())

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
        # This function is called when you register your Battlesnake on play.battlesnake.com
        # It controls your Battlesnake appearance and author permissions.
        # TIP: If you open your Battlesnake URL in browser you should see this data
        return {
            "apiversion": "1",
            "author": "",  # TODO: Your Battlesnake Username
            "color": "#ffcc00",  # TODO: Personalize
            "head": "tongue",  # TODO: Personalize
            "tail": "present",  # TODO: Personalize
        }

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def start(self):
        # This function is called everytime your snake is entered into a game.
        # cherrypy.request.json contains information about the game that's about to be played.
        data = cherrypy.request.json

        # Start the game with initial setup
        game_id = self.__unique_id(data)
        self.learner.start(game_id)
        self.health_threshold[game_id] = self.runtime_config.health_threshold()

        print("START")
        return "ok"

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def move(self):
        # This function is called on every turn of a game. It's how your snake decides where to move.
        # Valid moves are "up", "down", "left", or "right".
        data = cherrypy.request.json

        # Choose a random direction to move in
        possible_moves = ["up", "down", "left", "right"]
        #move = random.choice(possible_moves)

        # Construct states and query learner
        game_id = self.__unique_id(data)
        if game_id not in self.prev_state:
            state, block_arr = util.discretize_narrow_directional_area(data, self.config.num_actions(), self.health_threshold[game_id])
            action = self.learner.querysetstate(state, block_arr, game_id)
        else:
            # Calculate reward based on previous state
            r = self.__calc_reward(data, game_id)

            state, block_arr = util.discretize_narrow_directional_area(data, self.config.num_actions(), self.health_threshold[game_id])
            if self.is_learning_mode:
                action = self.learner.query(state, r, block_arr, game_id)
            else:
                action = self.learner.querysetstate(state, block_arr, game_id)
        move = possible_moves[action]

        # Memorize previous state
        self.prev_state[game_id] = RememberState(data)

        print(f"THIS MOVE({game_id}): {move}")
        return {"move": move}

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def end(self):
        # This function is called when a game your snake was in ends.
        # It's purely for informational purposes, you don't have to make any decisions here.
        data = cherrypy.request.json

        game_id = self.__unique_id(data)
        # Punish or reward when game end in learning mode
        if self.is_learning_mode and game_id in self.prev_state:
            # Calculate reward based on previous state
            r = self.__calc_reward(data, game_id)
            state, block_arr = util.discretize_narrow_directional_area(data, self.config.num_actions(), self.health_threshold[game_id])
            _ = self.learner.query(state, r, block_arr, game_id)
            # print(self.learner.dump(self.config.Q()))

        # Clean up to save memory
        self.prev_state.pop(game_id, None)
        self.health_threshold.pop(game_id, None)
        self.learner.end(game_id)

        if self.runtime_config.dump_at_end():
            self.dump()

        print("END")
        return "ok"

    @cherrypy.expose
    def switch(self):
        # This function is called when you want to swtich between learning and testing modes
        self.is_learning_mode = not self.is_learning_mode
        msg = "is_learning_mode = {}".format(self.is_learning_mode)
        print(msg)
        return msg

    @cherrypy.expose
    def dump(self):
        # This function is called when you want to dump the Q tablel to file
        print(self.learner.dump(self.config.Q()))
        return "ok"

    # Helper methods
    def __unique_id(self, data):
        # concat game_id with you_id
        game_id = data['game']['id']
        you_id = data['you']['id']
        return f"{game_id}:{you_id}"

    def __calc_reward(self, data, game_id):
        curr_s = RememberState(data)
        prev_s = self.prev_state[game_id]
        r = self.reward_config.default()
        if curr_s.health() == 0:
            r = self.reward_config.die()
        elif curr_s.health() >= prev_s.health():
            r = self.reward_config.eat_food()
            # After eating food, decay the health threshold
            health_t_decay = self.runtime_config.health_threshold_decay()
            self.health_threshold[game_id] *= health_t_decay
        elif prev_s.health() <= self.health_threshold[game_id]:
            r = self.reward_config.low_health()
        return r

if __name__ == "__main__":
    server = Battlesnake()
    cherrypy.config.update({"server.socket_host": "0.0.0.0"})
    cherrypy.config.update(
        {"server.socket_port": int(os.environ.get("PORT", "8080")),}
    )
    print("Starting Battlesnake Server...")
    cherrypy.quickstart(server)
