from miridan import db
from miridan import api
from miridan import app
from miridan.users import User

from flask import request, jsonify, send_file
from flask.ext.security import login_required
from flask.ext.restful import Resource, abort
from flask.ext.mongoengine import ValidationError
import urllib2
import io
from mongoengine.errors import InvalidQueryError, OperationError


VIEW_RADIUS = 20


class Entity(db.Document):
    meta = {'allow_inheritance': True}
    location = db.PointField()
    name = db.StringField(primary_key=True)
    mass = db.FloatField(min_value=0.0, default=0.0)
    description = db.StringField()
    image = db.ImageField()
    container = db.ReferenceField('self', dbref=False,
                                  reverse_delete_rule='NULLIFY')

    def to_dict(self):
        return {
            "name": self.name,
            "image": self.image_url,
            "description": self.description
        }

    @property
    def image_url(self):
        return '/entity/{}/image'.format(self.name)

    def load_image_from_url(self, url):
        image_file = io.BytesIO(urllib2.urlopen(url).read())
        if image_file:
            self.image.delete()
            self.image.put(image_file)


class World(Entity):
    pass


class Player(Entity):
    user = db.ReferenceField(User, dbref=False)


@app.before_first_request
def create_default_world():
    World(name='Worldy').save()


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
        world = World.objects.with_id(player.container.id)

        return jsonify({"world": world.to_dict(),
                        "entities": [e.to_dict() for e in
                                     Entity.objects(container=world.id)]})
api.add_resource(PlayerWorldView, '/world')


class PlayerEntityImageView(Resource):
    @login_required
    def get(self, name):
        """
        Return the image associated with a given entity.
        """
        # TODO: verify that the player should see this image at all.
        obj = Entity.objects.with_id(name)
        if obj is None:
            abort(404, message="Entity '{}' does not exist.".format(name))
        #return send_file(obj.image, mimetype=obj.image.content_type)
        return send_file(obj.image, mimetype='image/png')
api.add_resource(PlayerEntityImageView, '/entity/<name>/image')


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
            obj = Entity.objects(name=name).first()
            if obj is None:
                abort(404, message="Entity '{}' does not exist."
                                   .format(obj))

            if 'image' in request.json:
                obj.load_image_from_url(request.json['image'])
                del request.json['image']

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

            image_url = None
            if 'image' in request.json:
                image_url = request.json['image']
                del request.json['image']

            obj = Entity(**request.json)

            if image_url is not None:
                obj.load_image_from_url(image_url)

            obj.save()
            return obj.to_json(), 201
        except ValidationError, e:
            abort(400, message=repr(e))
api.add_resource(EntityView, '/admin/entity/<name>')
