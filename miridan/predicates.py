"""
Module that defines all predicates in this world.
"""
from miridan import database
import inspect


class BasePredicate(object):
    """
    Represents a predicate that already has grounded atoms.
    """
    def __init__(self, **kwargs):
        self.args = kwargs
        self.__call__ = self.__class__.__nonzero__

    def __nonzero__(self):
        """
        Evaluate this grounded predicate.
        """
        return self.__class__.__call__(self, **self.args)

    def __and__(self, other):
        """
        Create a new joint predicate.
        """
        return AndPredicate(self, other)

    def __invert__(self):
        """
        Create a new joint predicate.
        """
        return NotPredicate(self)


class AndPredicate(BasePredicate):
    def __init__(self, left, right):
        self.left = left
        self.right = right
        self.__call__ = self.__class__.__nonzero___

    def __nonzero__(self):
        return self.left() & self.right()


class NotPredicate(BasePredicate):
    def __init__(self, inner):
        self.inner = inner
        self.__call__ = self.__class__.__nonzero___

    def __nonzero__(self):
        return ~self.inner()


class Predicate(BasePredicate):
    pass


class IsHeavy(Predicate):
    def __call__(self, obj):
        try:
            return database[obj]['mass'] > 10.0
        except KeyError:
            return False


class IsHeld(Predicate):
    def __call__(self, obj):
        try:
            return database[obj]['held']
        except KeyError:
            return False


class IsHolding(Predicate):
    def __call__(self, obj):
        try:
            return database[obj]['holding']
        except KeyError:
            return False


def load(database):
    """
    Load all the predicates into a dictionary.
    """
    table = {}
    g = globals().copy()
    for name, obj in g.iteritems():
        if inspect.isclass(obj) and issubclass(obj, Predicate):
            table[name] = obj()
    return table
