"""
Module that defines all predicates in this world.
"""
import inspect


class NonSymbolicException(Exception):
    pass


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

    def clear(self, **kwargs):
        """
        Change the database however is necessary to NOT represent this state.
        """
        pass


class NonSymbolicPredicate(Predicate):
    """
    Base class for predicates that can be evaluated, but not applied.
    """
    def apply(self, **kwargs):
        raise NonSymbolicException()


class IsHeavy(NonSymbolicPredicate):
    def __call__(self, obj):
        try:
            return self._database[obj]['mass'] > 10.0
        except KeyError:
            return False


class IsHeld(Predicate):
    def __call__(self, obj):
        try:
            return self._database[obj]['held']
        except KeyError:
            return False

    def apply(self, obj):
        self._database[obj]['held'] = True

    def clear(self, obj):
        self._database[obj]['held'] = False


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
