"""
Module that defines all actions in this world.
"""
from pddlpy.predicate import Predicate
import inspect


class Action(object):
    """
    Base class for all actions.
    """
    def __init__(self):
        pass

    def __call__(self, *args, **kwargs):
        """
        Modify the database as necessary to execute this action.
        """
        pass

    def pre(self, *args, **kwargs):
        return Predicate()

    def post(self, *args, **kwargs):
        return Predicate()


def load(database):
    """
    Load all the actions into a dictionary.
    """
    table = {}
    g = globals().copy()
    for name, obj in g.iteritems():
        if inspect.isclass(obj) and issubclass(obj, Action):
            table[name] = obj()
    return table
