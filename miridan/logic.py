from miridan import app
from miridan import db

from flask import jsonify, request, abort
from pddlpy import Predicate, Action, Domain
import inspect


@app.route('/action')
@app.route('/actions')
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


@app.route('/predicate')
@app.route('/predicates')
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
            return self.domain['db'][obj]['mass'] > 10.0
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
