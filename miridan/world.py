from miridan import db
from miridan import api
from miridan import app
from miridan.users import User

from flask import request, jsonify
from flask.ext.security import login_required
from flask.ext.restful import Resource, abort
from flask.ext.mongoengine import ValidationError
from mongoengine.errors import InvalidQueryError, OperationError


def message(msg, user=None):
    """
    Sends a string message to the engine log.
    """
    Log(user=User.current().id, message=msg).save()


class Log(db.Document):
    meta = {'max_documents': 1000}
    user = db.ReferenceField(User, dbref=False)
    message = db.StringField(max_length=255)


class LogView(Resource):
    def get(self):
        logs = [{"user": log.user.email,
                 "message": log.message}
                for log in Log.objects]
        return jsonify({"logs": logs})
api.add_resource(LogView, '/log')


class Entity(db.Document):
    meta = {'allow_inheritance': True}
    location = db.PointField()
    name = db.StringField()
    mass = db.FloatField(min_value=0.0, default=0.0)
    description = db.StringField()
    # TODO: This should really be a URL instead of string.
    image = db.StringField(default='/static/images/placeholder0.png')
    container = db.ReferenceField('self', dbref=False,
                                  reverse_delete_rule='NULLIFY')

    def to_dict(self):
        return {
            "_id": str(self.id),
            "name": self.name,
            "image": self.image,
            "description": self.description,
            "container": "none" if self.container is None
                         else str(self.container.id)
        }


class World(Entity):
    pass


class Player(Entity):
    user = db.ReferenceField(User, dbref=False)


@app.before_first_request
def create_default_world():
    world = World(name='Worldy')
    world.save()

    Entity(name='beans', container=world.id).save()


class PlayerWorldView(Resource):
    @login_required
    def get(self):
        """
        Return the contents of the world the player is currently in.
        """
        # Get the current player and their world.
        user = User.current()

        # If this user does not have a player, create one.
        player = Player.objects(user=user.id).first()
        if player is None:
            player = Player(name=user.email,
                            user=user.id)
            player.save()

        # Retrieve the world that this player is currently in.
        if player.container is None:
            player.container = World.objects.first()
            player.save()
            if player.container is None:
                abort(404, message="Player world does not exist.")
        world = Entity.objects.with_id(player.container.id)

        return jsonify({"world": world.to_dict(),
                        "entities": [e.to_dict() for e in
                                     Entity.objects(container=world.id)]})
api.add_resource(PlayerWorldView, '/world')


class PlayerInventoryView(Resource):
    @login_required
    def get(self):
        """
        Return the contents of the world the player is currently in.
        """
        # Get the current player and their world.
        user = User.current()

        # If this user does not have a player, create one.
        player = Player.objects(user=user.id).first()
        if player is None:
            abort(404, message="Player '{}' does not exist."
                               .format(user.id))

        # Retrieve the objects the player currently has.
        return jsonify({"entities": [e.to_dict() for e in
                                     Entity.objects(container=player.id)]})
api.add_resource(PlayerInventoryView, '/inventory')


class WorldList(Resource):
    def get(self):
        """
        Return the list of all available worlds.
        """
        return jsonify({"worlds": [w.name for w in World.objects]})
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

        return jsonify({"world": world.to_dict(),
                        "entities": [e.to_dict() for e in
                                     Entity.objects(container=world.id)]})

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
            return jsonify(obj.to_dict())
        abort(404, message="Entity '{}' does not exist.".format(name))

    def patch(self, name):
        try:
            obj = Entity.objects.with_id(name)
            if obj is None:
                abort(404, message="Entity '{}' does not exist."
                                   .format(obj))

            update_fields = {'set__'+key: value
                             for (key, value) in request.json.iteritems()}
            if update_fields:
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
