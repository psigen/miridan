"""
Module that defines all predicates in this world.
"""
import inspect


class Predicate(object):
    """
    Base class for all predicates.
    """
    def __init__(self, database):
        self._database = database

    def __call__(self, **kwargs):
        """
        Evaluate whether this predicate is true for the current arguments.
        """
        return True

    def apply(self, **kwargs):
        """
        Change the database however is necessary to represent this state.
        """
        pass


def load(database):
    """
    Load all the predicates into a dictionary.
    """
    table = {}
    g = globals().copy()
    for name, obj in g.iteritems():
        if inspect.isclass(obj) and issubclass(obj, Predicate):
            table[name] = obj(database)
    return table
