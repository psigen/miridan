"""
Module that defines all predicates in this world.
"""
from pddlpy.scope import Scope


class BasePredicate(object):
    """
    Represents a predicate that already has grounded atoms.
    """
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.__call__ = self.__class__.__nonzero__

    def __getattr__(self, item):
        """
        Attempt to resolve unknown attributes from Domain scope.
        """
        try:
            return Scope.root[item]
        except KeyError:
            raise AttributeError(item)

    def __nonzero__(self):
        """
        Evaluate this grounded predicate.
        """
        return self.__class__.__call__(self, *self.args, **self.kwargs)

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

    def __call__(self, **kwargs):
        """
        Empty implementation of predicate is trivially true.
        """
        return True

    def why(self):
        """
        Diagnostic function to determine why a predicate failed.
        """
        return str(self)


class AndPredicate(BasePredicate):
    def __init__(self, left, right):
        self.left = left
        self.right = right
        self.__call__ = self.__class__.__nonzero__

    def __nonzero__(self):
        return bool(self.left) & bool(self.right)

    def why(self):
        if not self.left:
            return self.left.why()
        else:
            return self.right.why()


class NotPredicate(BasePredicate):
    def __init__(self, inner):
        self.inner = inner
        self.__call__ = self.__class__.__nonzero__

    def __nonzero__(self):
        return ~bool(self.inner)

    def why(self):
        return "NOT(" + self.inner.why() + ")"


class Predicate(BasePredicate):
    pass
