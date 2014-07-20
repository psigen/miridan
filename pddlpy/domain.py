import inspect
from pddlpy.predicate import Predicate
from pddlpy.action import Action


class Domain(object):
    def __init__(self, name="Domain", predicates=[], actions=[]):
        self.name = name
        self.predicates = {p.__class__.name: p for p in predicates}
        self.actions = {a.__class__.name: a for a in actions}

    def load(self, module):
        """
        Adds all predicates and actions from the specified module.
        Returns a self reference so that it can be chained.
        """
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and issubclass(obj, Predicate):
                self.predicates[name] = obj

        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and issubclass(obj, Action):
                self.actions[name] = obj()

        return self
