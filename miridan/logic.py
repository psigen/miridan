from miridan import app
from miridan import db

from flask import jsonify, request, abort
from pddlpy import Predicate, Action, Domain

actions = miridan.actions.load(database)
predicates = miridan.predicates.load(database)


@app.route('/object/')
@app.route('/objects/')
def list_objects():
    return jsonify(objects=database)


@app.route('/object/<object_name>')
@app.route('/objects/<object_name>')
def show_object(object_name):
    try:
        return jsonify(object=database[object_name])
    except KeyError:
        abort(404)


@app.route('/action/')
@app.route('/actions/')
def list_actions():
    # TODO: provide args
    return jsonify(actions=actions.keys())


@app.route('/action/<action_name>',  methods=["GET", "POST"])
@app.route('/actions/<action_name>',  methods=["GET", "POST"])
def action(action_name=None):
    try:
        with Domain(db=db):
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
    except TypeError:
        abort(404)


@app.route('/predicate/')
@app.route('/predicates/')
def list_predicates():
    # TODO: provide predicates
    return jsonify(predicates=predicates.keys())


@app.route('/predicate/<predicate_name>', methods=["GET", "POST"])
@app.route('/predicates/<predicate_name>', methods=["GET", "POST"])
def predicate(predicate_name=None):
    try:
        with Domain(db=db):
            predicate = predicates[predicate_name]
            args = {name: arg for (name, arg) in request.args.iteritems()}

            return jsonify(predicate=predicate_name,
                           args=args,
                           result=predicate(**args))
    except KeyError:
        abort(404)


class IsHeavy(Predicate):
    def __call__(self, obj):
        try:
            return self.db[obj]['mass'] > 10.0
        except KeyError:
            return False


class IsHeld(Predicate):
    def __call__(self, obj):
        try:
            return self.db[obj]['held']
        except KeyError:
            return False


class IsHolding(Predicate):
    def __call__(self, obj):
        try:
            return self.db[obj]['holding']
        except KeyError:
            return False


class PickUp(Action):
    def __call__(self, player, obj):
        self.db[obj]['held'] = True
        self.db[obj]['x'] = None
        self.db[obj]['y'] = None

    def pre(self, player, obj):
        return ~IsHeld(obj=obj) & ~IsHeavy(obj=obj) & ~IsHolding(obj=player)

    def post(self, player, obj):
        return IsHeld(obj=obj) & IsHolding(obj=player)
