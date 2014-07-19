from miridan import db
from miridan import api
from miridan.users import User

from flask import request, jsonify
from flask.json import loads
from flask.ext.security import login_required, current_user
from flask.ext.restful import Resource, abort
from flask.ext.mongoengine import ValidationError
from mongoengine.errors import InvalidQueryError, OperationError


VIEW_RADIUS = 20


class World(db.Document):
    name = db.StringField(primary_key=True)


class Entity(db.Document):
    meta = {'allow_inheritance': True}
    location = db.PointField()
    name = db.StringField(primary_key=True)
    description = db.StringField()
    image = db.ImageField()
    world = db.ReferenceField(World, dbref=False)


class Player(Entity):
    user = db.ReferenceField(User, dbref=False)


class PlayerWorldView(Resource):
    @login_required
    def get(self):
        """
        Return the contents of the world the player is currently in.
        """
        # Get the current player and their world.
        user = current_user

        # If this user does not have a player, create one.
        player = Player.objects(user=user.id).first()
        if player is None:
            player = Player(name=current_user.email,
                            user=current_user.id)
            player.save()

        # Retrieve the world that this player is currently in.
        if player.world is None:
            player.world = World.objects.first()
            player.save()
            if player.world is None:
                abort(404, message="Player world does not exist.")
        world = World.objects.with_id(player.world.id)

        return jsonify({"world": loads(world.to_json()),
                        "entities": loads(Entity.objects(world=world.id)
                                          .to_json())})
api.add_resource(PlayerWorldView, '/world')


class WorldList(Resource):
    def get(self):
        """
        Return the list of all available worlds.
        """
        return jsonify({"worlds": loads(World.objects.only("name").to_json())})
api.add_resource(WorldList, '/admin/world')


class WorldView(Resource):
    def get(self, name):
        """
        Return the contents of an entire world.
        """
        if name is None:
            jsonify(World.objects.to_json())

        world = World.objects(name=name).first()
        if world is None:
            abort(404, message="World '{}' does not exist.".format(name))

        return jsonify({"world": loads(world.to_json()),
                        "entities": loads(Entity.objects(world=world.id)
                                          .to_json())})

    def put(self, name):
        """
        Create a world with the given parameters.
        """
        try:
            request.json['name'] = name
            obj = World(**request.json)
            obj.save()
            return obj.to_json(), 201
        except ValidationError, e:
            abort(400, message=repr(e))
api.add_resource(WorldView, '/admin/world/<name>')


# TODO: add admin authentication to arbitrarily modify objects.
class EntityView(Resource):
    def get(self, name):
        obj = Entity.objects(name=name).first()
        if obj is not None:
            return obj.to_json()
        abort(404, message="Entity '{}' does not exist.".format(name))

    def patch(self, name):
        try:
            obj = Entity.objects(name=name).first()
            update_fields = {'set__'+key: value
                             for (key, value) in request.json.iteritems()}
            obj.update(**update_fields)
            obj.save()
            return obj.to_json(), 201
        except (InvalidQueryError, OperationError, ValidationError), e:
            abort(400, message=repr(e))

    def delete(self, name):
        Entity.objects(name=name).delete()
        return '', 204

    def put(self, name):
        try:
            request.json['name'] = name
            obj = Entity(**request.json)
            obj.save()
            return obj.to_json(), 201
        except ValidationError, e:
            abort(400, message=repr(e))
api.add_resource(EntityView, '/admin/entity/<name>')
