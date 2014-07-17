"""
Module that defines all actions in this world.
"""
from miridan.predicates import *
from miridan import database
import inspect


class Action(object):
    """
    Base class for all actions.
    """
    def __init__(self):
        pass

    def __call__(self, **kwargs):
        """
        Modify the database as necessary to execute this action.
        """
        pass

    def pre(self, **kwargs):
        return Predicate()

    def post(self, **kwargs):
        return Predicate()


class PickUp(Action):
    def __call__(self, player, obj):
        database[obj]['held'] = True
        database[obj]['x'] = None
        database[obj]['y'] = None

    def pre(self, player, obj):
        return ~IsHeld(obj=obj) & ~IsHeavy(obj=obj) & ~IsHolding(obj=player)

    def post(self, player, obj):
        return IsHeld(obj=obj) & IsHolding(obj=player)


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
