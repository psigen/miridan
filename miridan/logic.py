from miridan import api
from miridan.rules import GAME_DOMAIN
from miridan.world import Entity

from flask import jsonify, request
from flask.ext.restful import Resource, abort
from flask.ext.security import login_required
from pddlpy import Scope
import inspect
from mongoengine.errors import ValidationError


def get_args(fn):
    return [arg for arg in inspect.getargspec(fn)[0]
            if arg != "self"]


class PredicateView(Resource):
    def get(self):
        predicate_dict = {k: get_args(v.__call__)
                          for (k, v) in GAME_DOMAIN.predicates.iteritems()}
        return jsonify(predicates=predicate_dict)
api.add_resource(PredicateView, '/predicate')


class PredicateEval(Resource):
    @login_required
    def get(self, predicate_name):
        try:
            with Scope(world=Entity):
                predicate = GAME_DOMAIN.predicates[predicate_name]
                args = {name: arg for (name, arg) in request.args.iteritems()}

                return jsonify(predicate=predicate_name,
                               args=args,
                               result=bool(predicate(**args)))
        except KeyError:
            abort(404, message="Predicate '{}' was not found."
                               .format(predicate_name))
        except (TypeError, AttributeError), e:
            abort(400, message=repr(e))
api.add_resource(PredicateEval, '/predicate/<predicate_name>')


class ActionView(Resource):
    def get(self):
        action_dict = {k: {"args": get_args(v.__call__)}
                       for (k, v) in GAME_DOMAIN.actions.iteritems()}
        return jsonify(actions=action_dict)
        return jsonify(actions=GAME_DOMAIN.actions.keys())
api.add_resource(ActionView, '/action')


class ActionEval(Resource):

    # TODO: This alias should be removed.
    @login_required
    def get(self, action_name):
        return self.put(action_name)

    @login_required
    def put(self, action_name):
        try:
            with Scope(world=Entity):
                try:
                    action = GAME_DOMAIN.actions[action_name]
                except KeyError, e:
                    abort(404, message="Action '{}' was not found."
                          .format(action_name))
                args = {name: arg for (name, arg) in request.args.iteritems()}

                if action.pre(**args):
                    action(**args)
                    success = action.post(**args)
                    if success:
                        return jsonify(action=action_name,
                                       args=args,
                                       result=True)
                    else:
                        return jsonify(action=action_name,
                                       args=args,
                                       result=False,
                                       reason="Postcondition: {}"
                                              .format(success.why()))
                else:
                    action(request.args)
                    return jsonify(action=action_name,
                                   args=args,
                                   result=False,
                                   reason="Precondition: {}"
                                          .format(success.why()))
        except (TypeError, AttributeError, KeyError, ValidationError), e:
            abort(400, message=repr(e))
api.add_resource(ActionEval, '/action/<action_name>')
