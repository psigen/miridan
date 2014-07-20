

class Domain(object):
    def __init__(self, predicates=None, actions=None):
        self.predicates = [] if predicates is None else predicates
        self.actions = [] if actions is None else actions
