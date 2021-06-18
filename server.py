import os
import json
import cherrypy

import config as cf
import QLearnerStrategy as qs
import FoodStrategy as fs
import HeadStrategy as hs
import util

"""
This is a simple Battlesnake server written in Python.
For instructions see https://github.com/BattlesnakeOfficial/starter-snake-python/README.md
"""
class Battlesnake(object):
    def __init__(self):
        # Load learner parameters from learner.json
        with open('learner.json') as f:
            self.raw_config = json.load(f)

        self.runtime_config = cf.RuntimeConfig(self.raw_config)
        self.qlearnerStrategy = qs.QLearnerStrategy(self.raw_config)
        self.foodStrategy = fs.FoodStrategy(self.raw_config)
        self.headStrategy = hs.HeadStrategy(self.raw_config)

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

        self.qlearnerStrategy.start(data)
        self.foodStrategy.start(data)

        print("START")
        return "ok"

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def move(self):
        # This function is called on every turn of a game. It's how your snake decides where to move.
        # Valid moves are "up", "down", "left", or "right".
        data = cherrypy.request.json

        # calculate routes
        board = data['board']
        h = board['height']
        w = board['width']
        you = data['you']
        head = you['head']
        states = util.construct_borad(data)
        routes = [-1, -1, -1, -1]

        block_arr = util.determine_block_array(data, states, len(routes))

        for a in range(len(routes)):
            if not block_arr[a]:
                possible_routes = util.calculate_possible_routes(head['y'], head['x'], a, w, h, states)
                routes[a] = possible_routes

        data['states'] = states
        data['block_arr'] = block_arr
        data['routes'] = routes

        # HeadStrategy first
        move = self.headStrategy.move(data)
        if move is None:
            def is_food_strategy_mode():
                board = data['board']
                my_id = data['you']['id']
                max_other_length = 0
                if 'snakes' in board:
                    for snake in board['snakes']:
                        if not snake['id'] == my_id:
                            max_other_length = max(max_other_length, len(snake['body']))
                return len(data['you']['body']) < max_other_length + self.runtime_config.is_food_strategy_threshold

            if is_food_strategy_mode():
                mode = "FOOD"
                move = self.foodStrategy.move(data)
            else:
                mode = "LEARN"
                move = self.qlearnerStrategy.move(data)
        else:
            mode = "HEAD"

        print(f"THIS TURN({data['turn']}) <{mode}> MOVE({move})")

        return {"move": move}

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def end(self):
        # This function is called when a game your snake was in ends.
        # It's purely for informational purposes, you don't have to make any decisions here.
        data = cherrypy.request.json

        # self.qlearnerStrategy.end(data)
        self.foodStrategy.end(data)

        print("END")
        return "ok"

if __name__ == "__main__":
    server = Battlesnake()
    cherrypy.config.update({"server.socket_host": "0.0.0.0"})
    cherrypy.config.update(
        {"server.socket_port": int(os.environ.get("PORT", "8080")),}
    )
    print("Starting Battlesnake Server...")
    cherrypy.quickstart(server)
