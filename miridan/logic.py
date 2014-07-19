from miridan import api
from miridan.world import Entity

from flask import jsonify, request
from flask.ext.restful import Resource, abort
from pddlpy import Predicate, Action, Domain
import inspect


def get_args(fn):
  return [arg for arg in inspect.getargspec(fn)[0]
          if arg != "self"]


class PredicateView(Resource):
    def get(self):
        predicate_dict = {k: get_args(v.__call__)
                          for (k, v) in predicates.iteritems()}
        return jsonify(predicates=predicate_dict)


class PredicateEval(Resource):
    def get(self, predicate_name):
        try:
            with Domain(world=Entity):
                predicate = predicates[predicate_name]
                args = {name: arg for (name, arg) in request.args.iteritems()}

                return jsonify(predicate=predicate_name,
                               args=args,
                               result=predicate(**args))
        except KeyError:
            abort(404, message="Predicate '{}' was not found."
                               .format(predicate_name))
        except (TypeError, AttributeError), e:
            abort(400, message=repr(e))


class ActionView(Resource):
    def get(self):
        action_dict = {k: {"args": get_args(v.__call__)}
                       for (k, v) in actions.iteritems()}
        return jsonify(actions=action_dict)
        return jsonify(actions=actions.keys())


class ActionEval(Resource):
    def get(self, action_name):
        try:
            with Domain(world=Entity):
                action = actions[action_name]
                args = {name: arg for (name, arg) in request.args.iteritems()}

                if action.pre(**args):
                    action(**args)
                    return jsonify(action=action_name,
                                   args=args,
                                   result=action.post(**args))
                else:
                    action(request.args)
                    return jsonify(action=action_name,
                                   args=args,
                                   result=False,
                                   reason="Preconditions not met.")
        except KeyError:
            abort(404, message="Action '{}' was not found.'"
                               .format(action_name))


api.add_resource(PredicateView, '/predicate')
api.add_resource(PredicateEval, '/predicate/<predicate_name>')
api.add_resource(ActionView, '/action')
api.add_resource(ActionEval, '/action/<action_name>')


class IsHeavy(Predicate):
    def __call__(self, name):
        obj = self.world.objects(name=name).first()
        return obj is not None and obj.mass > 10.0


class IsHeld(Predicate):
    def __call__(self, name):
        obj = self.world.objects(name=name).first()
        return obj is not None and obj.location is None


class IsHolding(Predicate):
    def __call__(self, name):
        obj = self.world.objects(name=name).first()
        return obj is not None


class PickUp(Action):
    def __call__(self, player, obj):
        obj = self.world.objects(name=obj).first()
        obj.held = True
        obj.location = None
        obj.save()

    def pre(self, player, obj):
        return ~IsHeld(obj=obj) & ~IsHeavy(obj=obj) & ~IsHolding(obj=player)

    def post(self, player, obj):
        return IsHeld(obj=obj) & IsHolding(obj=player)


def load_predicates():
    """
    Load all the predicates into a dictionary.
    """
    table = {}
    g = globals().copy()
    for name, obj in g.iteritems():
        if inspect.isclass(obj) and issubclass(obj, Predicate):
            table[name] = obj()
    return table


def load_actions():
    """
    Load all the actions into a dictionary.
    """
    table = {}
    g = globals().copy()
    for name, obj in g.iteritems():
        if inspect.isclass(obj) and issubclass(obj, Action):
            table[name] = obj()
    return table


actions = load_actions()
predicates = load_predicates()
