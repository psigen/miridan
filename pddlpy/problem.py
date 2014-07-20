

class Problem(object):
    def __init__(self, domain=None, init=None, goal=None):
        self.domain = domain

        self.init = [] if init is None else init
        self.goal = [] if goal is None else goal
