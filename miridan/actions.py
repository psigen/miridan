"""
Module that defines all actions in this world.
"""
import miridan.predicates
import inspect

class Action(object):
    """
    Base class for all actions.
    """
    def __init__(self, database):
        self._database = database
        self.pre = miridan.predicates.Predicate(self._database)
        self.post = miridan.predicates.Predicate(self._database)

    def __call__(self, **kwargs):
        """
        Modify the database as necessary to execute this action.
        """
        pass


def load(database):
    """
    Load all the actions into a dictionary.
    """
    table = {}
    g = globals().copy()
    for name, obj in g.iteritems():
        if inspect.isclass(obj) and issubclass(obj, Action):
            table[name] = obj(database)
    return table
