class LearnerConfig(object):
    def __init__(self, config):
        self.config = config

    def num_states(self):
        return self.config.get('num_states', 100)

    def num_actions(self):
        return self.config.get('num_actions', 4)

    def alpha(self):
        return self.config.get('alpha', 0.2)

    def gamma(self):
        return self.config.get('gamma', 0.9)

    def rar(self):
        return self.config.get('rar', 0.5)

    def radr(self):
        return self.config.get('radr', 0.99)

    def dyna(self):
        return self.config.get('dyna', 0)

    def verbose(self):
        return self.config.get('verbose', False)

    def Q(self):
        return self.config.get('Q', None)


class RuntimeConfig(object):
    def __init__(self, config):
        self.config = config['runtime'] if 'runtime' in config else {}

    def is_learning_mode(self):
        return self.config.get('is_learning_mode', True)

    def health_threshold(self):
        return self.config.get('health_threshold', 100)

    def health_threshold_decay(self):
        return self.config.get('health_threshold_decay', 0.9)

    def dump_at_end(self):
        return self.config.get('dump_at_end', False)


class RewardConfig(object):
    def __init__(self, config):
        self.config = config['reward'] if 'reward' in config else {}

    def default(self):
        return self.config.get('default', -1.0)

    def low_health(self):
        return self.config.get('low_health', -10.0)

    def die(self):
        return self.config.get('die', -10000.0)

    def eat_food(self):
        return self.config.get('eat_food', 100.0)
