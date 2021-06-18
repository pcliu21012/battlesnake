class LearnerConfig(object):
    def __init__(self, config):
        self.num_states = config.get('num_states', 100)
        self.num_actions = config.get('num_actions', 4)
        self.alpha = config.get('alpha', 0.2)
        self.gamma = config.get('gamma', 0.9)
        self.rar = config.get('rar', 0.5)
        self.radr = config.get('radr', 0.999)
        self.dyna = config.get('dyna', 0)
        self.verbose = config.get('verbose', False)
        self.Q = config.get('Q', None)


class RuntimeConfig(object):
    def __init__(self, config):
        config = config['runtime'] if 'runtime' in config else {}
        self.is_learning_mode = config.get('is_learning_mode', True)
        self.health_threshold = config.get('health_threshold', 100)
        self.health_threshold_decay = config.get('health_threshold_decay', 0.9)
        self.is_food_strategy_threshold = config.get('is_food_strategy_threshold', 2)
        self.dump_at_end = config.get('dump_at_end', False)


class RewardConfig(object):
    def __init__(self, config):
        config = config['reward'] if 'reward' in config else {}
        self.default = config.get('default', -1.0)
        self.low_health = config.get('low_health', -10.0)
        self.die = config.get('die', -10000.0)
        self.eat_food = config.get('eat_food', 100.0)
