from miridan import api
from miridan import db
from miridan.world import Entity, Player, World
from miridan.users import User

from flask import jsonify, request
from flask.ext.restful import Resource, abort
from flask.ext.security import login_required
from pddlpy import Predicate, Action, Domain
import inspect


def message(msg, user=None):
    """
    Sends a string message to the engine log.
    """
    Log(user=User.current().id, message=msg).save()


class Log(db.Document):
    meta = {'max_documents': 1000}
    user = db.ReferenceField(User, dbref=False)
    message = db.StringField(max_length=255)


def get_args(fn):
    return [arg for arg in inspect.getargspec(fn)[0]
            if arg != "self"]


class LogView(Resource):
    def get(self):
        logs = [{"user": log.user.email,
                 "message": log.message}
                for log in Log.objects]
        return jsonify({"logs": logs})
api.add_resource(LogView, '/log')


class PredicateView(Resource):
    def get(self):
        predicate_dict = {k: get_args(v.__call__)
                          for (k, v) in predicates.iteritems()}
        return jsonify(predicates=predicate_dict)
api.add_resource(PredicateView, '/predicate')


class PredicateEval(Resource):
    @login_required
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
api.add_resource(PredicateEval, '/predicate/<predicate_name>')


class ActionView(Resource):
    def get(self):
        action_dict = {k: {"args": get_args(v.__call__)}
                       for (k, v) in actions.iteritems()}
        return jsonify(actions=action_dict)
        return jsonify(actions=actions.keys())
api.add_resource(ActionView, '/action')


class ActionEval(Resource):
    @login_required
    def get(self, action_name):
        try:
            with Domain(world=Entity):
                action = actions[action_name]
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
        except KeyError, e:
            abort(404, message="Action '{}' was not found."
                  .format(action_name))
        except (TypeError, AttributeError), e:
            abort(400, message=repr(e))
api.add_resource(ActionEval, '/action/<action_name>')


class IsHeavy(Predicate):
    def __call__(self, obj):
        obj = Entity.objects.with_id(obj)
        return obj is not None and obj.mass > 10.0

    def __str__(self):
        return "{} must be heavy".format(self.args['obj'])


class IsHeld(Predicate):
    def __call__(self, player, obj):
        player = Player.objects.with_id(player)
        obj = Entity.objects.with_id(obj)
        return (player is not None
                and obj is not None
                and obj.container == player)

    def __str__(self):
        return "{} must be held".format(self.args['obj'])


class IsMyPlayer(Predicate):
    def __call__(self, player):
        player = Player.objects.with_id(player)
        return player is not None and player.user.id == User.current().id

    def __str__(self):
        return "{} must be your player".format(self.args['player'])


class IsObject(Predicate):
    def __call__(self, obj):
        obj = Entity.objects.with_id(obj)
        return obj is not None

    def __str__(self):
        return "{} must be your player".format(self.args['player'])


class PickUp(Action):
    def __call__(self, player, obj):
        obj = Entity.objects.with_id(obj)
        player = Player.objects.with_id(player)

        obj.location = None
        obj.container = player
        obj.save()

        message("{player} is picking up {obj}."
                .format(player=player.id, obj=obj.id))

    def pre(self, player, obj):
        return (IsObject(obj=obj)
                & ~IsHeld(player=player, obj=obj)
                & ~IsHeavy(obj=obj)
                & IsMyPlayer(player=player))

    def post(self, player, obj):
        return IsHeld(player=player, obj=obj)


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
