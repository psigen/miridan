from miridan import db
from miridan import api

from flask import jsonify, request
from flask.ext.login import login_required
from flask.ext.restful import Resource, abort
from flask.ext.mongoengine import ValidationError
from mongoengine.errors import InvalidQueryError, OperationError


VIEW_RADIUS = 20


class WorldObject(db.Document):
    location = db.PointField()
    name = db.StringField(primary_key=True)
    meta = {'allow_inheritance': True}


class Player(WorldObject):
    pass


class WorldView(Resource):
    @login_required
    def get(self):
        """
        Return all the nearby objects to the player in the world.
        """
        # TODO: figure out range from actual player object.
        return WorldObject.objects(
            location__geo_within_center=[(0, 0), VIEW_RADIUS]).to_json()


# TODO: add admin authentication to arbitrarily modify objects.
class WorldObjectView(Resource):
    def get(self, name):
        obj = WorldObject.objects(name=name).first()
        if obj is not None:
            return obj.to_json()
        abort(404, message="World object '{0}' does not exist.".format(name))

    def patch(self, name):
        try:
            obj = WorldObject.objects(name=name).first()
            update_fields = {'set__'+key: value
                             for (key, value) in request.json.iteritems()}
            obj.update(**update_fields)
            obj.save()
            return obj.to_json(), 201
        except (InvalidQueryError, OperationError, ValidationError), e:
            abort(400, message=str(e))

    def delete(self, name):
        WorldObject.objects(name=name).delete()
        return '', 204

    def put(self, name):
        try:
            request.json['name'] = name
            obj = WorldObject(**request.json)
            obj.save()
            return obj.to_json(), 201
        except ValidationError, e:
            print request.json
            abort(400, message=str(e))

api.add_resource(WorldView, '/world')
api.add_resource(WorldObjectView, '/world/<name>')
