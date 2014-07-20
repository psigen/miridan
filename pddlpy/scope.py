import collections
# TODO: does this class need locking?


class Scope(collections.MutableMapping):
    """
    Scope is a mutable dict of variables that are made available
    to predicates and actions when used inside a 'with' context.
    """
    root = {}

    def __init__(self, *args, **kwargs):
        self._parent = None

        self._store = dict()
        self._store.update(dict(*args, **kwargs))

        self._joint_store = dict()
        self._joint_store.update(self._store)

        self.__initialized = True

    def __getitem__(self, key):
        return self._joint_store[self.__keytransform__(key)]

    def __setitem__(self, key, value):
        self._store[self.__keytransform__(key)] = value
        self._joint_store[self.__keytransform__(key)] = value

    def __delitem__(self, key):
        del self._store[self.__keytransform__(key)]
        del self._joint_store[self.__keytransform__(key)]

    def __iter__(self):
        return iter(self._joint_store)

    def __len__(self):
        return len(self._joint_store)

    def __keytransform__(self, key):
        return key

    def __enter__(self):
        # Create a chain of Domain objects.
        self.__dict__['_parent'] = Scope.root
        Scope.root = self

        # Inherit keys from parent domain.
        if self._parent is not None:
            self._joint_store.clear()
            self._joint_store.update(self._parent)
            self._joint_store.update(self._store)

    def __exit__(self, type, value, traceback):
        # Uninherit keys from parent domain.
        if self._parent is not None:
            self._joint_store.clear()
            self._joint_store.update(self._store)

        # Unchain domain objects.
        Scope.root = self._parent
        self.__dict__['_parent'] = None

    def __getattr__(self, item):
        try:
            return self.__getitem__(item)
        except KeyError:
            raise AttributeError(item)

    def __setattr__(self, item, value):
        if '_Domain__initialized' in self.__dict__:
            self.__setitem__(item, value)
        else:
            dict.__setattr__(self, item, value)

    def __repr__(self):
        return "{cls}({dict})".format(cls=self.__class__.__name__,
                                      dict=self._joint_store)

    def __str__(self):
        if not self._parent:
            inherited_keys = {}
        else:
            inherited_keys = {k: v for (k, v) in
                              self._parent._joint_store.iteritems()
                              if k not in self._store}

        return "{cls}(local={store}, inherited={parent_store})" \
               .format(cls=self.__class__.__name__,
                       store=self._store,
                       parent_store=inherited_keys)
