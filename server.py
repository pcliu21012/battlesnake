import os
import random
import json

import cherrypy
import QLearner as ql
import numpy as np

import util

"""
This is a simple Battlesnake server written in Python.
For instructions see https://github.com/BattlesnakeOfficial/starter-snake-python/README.md
"""
class Battlesnake(object):
    # Global variable
    STEP_REWARD = -1.0

    def __init__(self):
        # Runtime settings
        self.is_learning_mode = True
        self.prev_state = {}
        self.health_threshold = 30

        # Load learner parameters from learner.json
        with open('learner.json') as f:
            self.config = json.load(f)
            if 'is_learning_mode' in self.config:
                self.is_learning_mode = self.config['is_learning_mode']

        # Initialize the QLearner
        self.learner = ql.QLearner(
            num_states=self.config['num_states'],
            num_actions=self.config['num_actions'],
            alpha=self.config['alpha'],
            gamma=self.config['gamma'],
            rar=self.config['rar'],
            radr=self.config['radr'],
            dyna=self.config['dyna'],
            verbose=self.config['verbose'],
        )
        if 'Q' in self.config:
            self.learner.load(self.config['Q'])

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
    @cherrypy.tools.json_out()
    def switch(self):
        # This function is called when you want to swtich between learning and testing modes
        self.is_learning_mode = not self.is_learning_mode
        print("is_learning_mode = {}".format(self.is_learning_mode))
        return {
            "is_learning_mode": self.is_learning_mode,
        }

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def start(self):
        # This function is called everytime your snake is entered into a game.
        # cherrypy.request.json contains information about the game that's about to be played.
        data = cherrypy.request.json

        state, block_arr = util.discretize_entire_directional_area(data, self.config['num_actions'], self.health_threshold)
        _ = self.learner.querysetstate(state, block_arr)

        print("START")
        return "ok"

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def move(self):
        # This function is called on every turn of a game. It's how your snake decides where to move.
        # Valid moves are "up", "down", "left", or "right".
        # TODO: Use the information in cherrypy.request.json to decide your next move.
        data = cherrypy.request.json

        # Choose a random direction to move in
        possible_moves = ["up", "down", "left", "right"]
        #move = random.choice(possible_moves)

        # Construct states and query learner
        r = self.__calc_reward(data)
        state, block_arr = util.discretize_entire_directional_area(data, self.config['num_actions'], self.health_threshold)
        if self.is_learning_mode:
            action = self.learner.query(state, r, block_arr)
        else:
            action = self.learner.querysetstate(state, block_arr)
        move = possible_moves[action]
        self.prev_state = self.__construct_remember_state(data)

        print(f"THIS MOVE: {move}")
        return {"move": move}

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def end(self):
        # This function is called when a game your snake was in ends.
        # It's purely for informational purposes, you don't have to make any decisions here.
        data = cherrypy.request.json

        # Punish or reward when game end
        r = self.__calc_reward(data)
        state, block_arr = util.discretize_entire_directional_area(data, self.config['num_actions'], self.health_threshold)
        if self.is_learning_mode:
            _ = self.learner.query(state, r, block_arr)

        print("END")

        # Record Q table
        # print("Learner Q table:")
        print(self.learner.dump())
        # print()

        return "ok"

    def __construct_remember_state(self, data):
        rem = {}
        rem['health'] = data['you']['health']
        rem['length'] = data['you']['length']
        return rem

    def __calc_reward(self, data):
        rem = self.__construct_remember_state(data)
        r = Battlesnake.STEP_REWARD
        if rem['health'] == 0:
            r = -10000.0
        elif 'health' in self.prev_state and rem['health'] >= self.prev_state['health']:
            r = 100.0
        return r

if __name__ == "__main__":
    server = Battlesnake()
    cherrypy.config.update({"server.socket_host": "0.0.0.0"})
    cherrypy.config.update(
        {"server.socket_port": int(os.environ.get("PORT", "8080")),}
    )
    print("Starting Battlesnake Server...")
    cherrypy.quickstart(server)
