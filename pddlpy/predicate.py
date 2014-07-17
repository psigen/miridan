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

    def why(self):
        """
        Diagnostic function to determine why a predicate failed.
        """
        return str(self) if self else None


class AndPredicate(BasePredicate):
    def __init__(self, left, right):
        self.left = left
        self.right = right
        self.__call__ = self.__class__.__nonzero___

    def __nonzero__(self):
        return self.left() & self.right()

    def why(self):
        return self.left.why() or self.right.why()


class NotPredicate(BasePredicate):
    def __init__(self, inner):
        self.inner = inner
        self.__call__ = self.__class__.__nonzero___

    def __nonzero__(self):
        return ~self.inner()

    def why(self):
        return str(self) if not self else None  # TODO: fix this


class Predicate(BasePredicate):
    pass


def load():
    """
    Load all the predicates into a dictionary.
    """
    table = {}
    g = globals().copy()
    for name, obj in g.iteritems():
        if inspect.isclass(obj) and issubclass(obj, Predicate):
            table[name] = obj()
    return table
