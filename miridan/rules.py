"""
Defines rule domains for the game.
"""
import inspect
from pddlpy import Predicate, Action, Domain
from miridan.users import User
from miridan.world import Entity, Player, World, message


class IsEqual(Predicate):
    def __call__(self, obj1, obj2):
        return obj1 == obj2

    def __str__(self):
        return "{} must be same as {}".format(self.args['obj1'],
                                              self.args['obj2'])


class IsHeavy(Predicate):
    def __call__(self, obj):
        obj = Entity.objects.with_id(obj)
        return obj is not None and obj.mass > 10.0

    def __str__(self):
        obj = Entity.objects.with_id(self.args['obj'])
        return "{} must be heavy".format(obj.name)


class IsHeld(Predicate):
    def __call__(self, player, obj):
        player = Player.objects.with_id(player)
        obj = Entity.objects.with_id(obj)
        return (player is not None
                and obj is not None
                and obj.container == player)

    def __str__(self):
        player = Player.objects.with_id(self.args['player'])
        obj = Entity.objects.with_id(self.args['obj'])
        return "{} must be held by {}".format(obj.name, player.name)


class IsMyPlayer(Predicate):
    def __call__(self, player):
        player = Player.objects.with_id(player)
        return player is not None and player.user.id == User.current().id

    def __str__(self):
        player = Player.objects.with_id(self.args['player'])
        return "{} must be your player".format(player.name)


class IsObject(Predicate):
    def __call__(self, obj):
        obj = Entity.objects.with_id(obj)
        return obj is not None

    def __str__(self):
        obj = Entity.objects.with_id(self.args['obj'])
        return "{} must be your player".format(obj.name)


class Teleport(Action):
    def __call__(self, player):
        player = Player.objects.with_id(player)
        world = World.objects.first()

        player.container = world
        player.save()

        message("{player} teleported to {world}."
                .format(player=player.name, world=world.name))

    def pre(self, player):
        return IsMyPlayer(player=player)


class PickUp(Action):
    def __call__(self, player, obj):
        obj = Entity.objects.with_id(obj)
        player = Player.objects.with_id(player)

        obj.location = None
        obj.container = player
        obj.save()

        message("{player} is picking up {obj}."
                .format(player=player.name, obj=obj.name))

    def pre(self, player, obj):
        return (IsObject(obj=obj)
                & ~IsHeld(player=player, obj=obj)
                & ~IsHeavy(obj=obj)
                & ~IsEqual(obj1=player, obj2=obj)
                & IsMyPlayer(player=player))

    def post(self, player, obj):
        return IsHeld(player=player, obj=obj)


class Drop(Action):
    def __call__(self, player, obj):
        obj = Entity.objects.with_id(obj)
        player = Player.objects.with_id(player)

        obj.location = None
        obj.container = player.container
        obj.save()

        message("{player} is dropping {obj}."
                .format(player=player.name, obj=obj.name))

    def pre(self, player, obj):
        return (IsObject(obj=obj)
                & IsHeld(player=player, obj=obj)
                & IsMyPlayer(player=player))

    def post(self, player, obj):
        return ~IsHeld(player=player, obj=obj)


def load_predicates():
    """
    Load all the predicates into a dictionary.
    """
    table = {}
    g = globals().copy()
    for name, obj in g.iteritems():
        if inspect.isclass(obj) and issubclass(obj, Predicate):
            table[name] = obj
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


GAME_DOMAIN = Domain(name='Game',
                     actions=load_actions(),
                     predicates=load_predicates())
