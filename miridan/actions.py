"""
Module that defines all actions in this world.
"""
from miridan.predicates import *
import inspect


class Action(object):
    """
    Base class for all actions.
    """
    def __init__(self, database):
        self._database = database
        self.pre = Predicate(self._database)
        self.post = Predicate(self._database)

    def __call__(self, **kwargs):
        """
        Modify the database as necessary to execute this action.
        """
        pass


class PickUp(Action):
    def __call__(self, obj):
        self._database[obj]['held'] = True
        self._database[obj]['x'] = None
        self._database[obj]['y'] = None

    def pre(self, obj):
        return ~IsHeld(obj=obj) & ~IsHeavy(obj=obj)

    def post(self, obj):
        return IsHeld(obj=obj)


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
