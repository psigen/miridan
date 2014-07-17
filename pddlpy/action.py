"""
Module that defines all actions in this world.
"""
from pddlpy.predicate import Predicate
from pddlpy.domain import Domain


class Action(object):
    """
    Base class for all actions.
    """
    def __init__(self):
        pass

    @property
    def domain(self):
        return Domain.root

    def __call__(self, *args, **kwargs):
        """
        Modify the database as necessary to execute this action.
        """
        pass

    def pre(self, *args, **kwargs):
        return Predicate()

    def post(self, *args, **kwargs):
        return Predicate()
