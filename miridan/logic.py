from miridan import app
from miridan import database

import miridan.predicates
import miridan.actions
from flask import jsonify, request

actions = miridan.actions.load(database)
predicates = miridan.predicates.load(database)


@app.route('/objects')
def list_objects():
    return jsonify(objects=database)


@app.route('/object/<object_name>')
def show_object(object_name):
    return jsonify(object=database[object_name])


@app.route('/actions')
def list_actions():
    # TODO: provide args
    return jsonify(actions=actions.keys())


@app.route('/action/<action_name>',  methods=["GET", "POST"])
def action(action_name=None):
    try:
        action = actions[action_name]

        if action.pre(**request.args):
            action(**request.args)
            action.post.apply(**request.args)
            return jsonify(action=action_name,
                           args=request.args,
                           result=action.post(**request.args))
        else:
            action(request.args)
            return jsonify(action=action_name,
                           args=request.args,
                           result=False,
                           reason="Preconditions not met.")
    except KeyError:
        return jsonify(action=action,
                       args=request.args,
                       result=None,
                       reason="Invalid action.")


@app.route('/predicates')
def list_predicates():
    # TODO: provide predicates
    return jsonify(predicates=predicates.keys())


@app.route('/predicate/<predicate_name>', methods=["GET", "POST"])
def predicate(predicate_name=None):
    try:
        predicate = predicates[predicate_name]
        return jsonify(predicate=predicate_name,
                       args=request.args,
                       result=predicate(**request.args))
    except KeyError:
        return jsonify(predicate=predicate_name,
                       args=request.args,
                       result=None,
                       reason="Invalid predicate.")
