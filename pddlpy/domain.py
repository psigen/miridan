

class Domain(object):
    def __init__(self, name="Domain", predicates=None, actions=None):
        self.name = name
        self.predicates = [] if predicates is None else predicates
        self.actions = [] if actions is None else actions
