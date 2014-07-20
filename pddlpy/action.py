"""
Module that defines all actions in this world.
"""
from pddlpy.predicate import Predicate
from pddlpy.scope import Scope


class Action(object):
    """
    Base class for all actions.
    """
    def __init__(self):
        pass

    def __getattr__(self, item):
        """
        Attempt to resolve unknown attributes from Domain scope.
        """
        try:
            return Scope.root[item]
        except KeyError:
            raise AttributeError(item)

    def __call__(self, *args, **kwargs):
        """
        Modify the database as necessary to execute this action.
        """
        pass

    def pre(self, *args, **kwargs):
        return Predicate()

    def post(self, *args, **kwargs):
        return Predicate()

    def cost(self):
        return 1.0  # TODO: what should this actually be?
