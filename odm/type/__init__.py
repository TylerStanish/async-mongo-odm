import numbers


class MongoType:
    def __init__(self, unique=False, serialize=True, default=None, nullable=True, **kwargs):
        self._unique = unique
        self._serialize = serialize
        self._default = default
        self._nullable = nullable
        for key, val in kwargs.items():
            setattr(self, key, val)


class MongoId(MongoType):
    _python_type = str


class MongoString(MongoType):
    _python_type = str


class MongoNumber(MongoType):
    _python_type = numbers.Number


class MongoDict(MongoType):
    """
    Use this when you don't care about "static" typing, that is, you don't care about declaring your fields beforehand
    and just want it to be a dict when retrieving from/saving to the database and/or don't care about validation
    """
    _python_type = dict


class MongoObject(MongoType):
    """
    Extend this when you know ahead of time what fields the nested object will have
    """
    @property
    def _python_type(self):
        return self.__class__

    @classmethod
    def _get_declared_class_mongo_attrs(cls):
        return [(attr, val) for attr, val in vars(cls).items() if isinstance(val, MongoType)]

    @classmethod
    def new(cls, **kwargs):
        # preferably do some validation, like check if all nullable=False fields are populated, type checking, etc.
        # TODO type-checking
        obj = cls()
        for attr, val in cls._get_declared_class_mongo_attrs():
            arg_val = kwargs.get(attr)
            if not val._nullable and arg_val is None:
                raise ValueError(f'Got null argument for {attr} but {attr} is not nullable')
            setattr(obj, attr, arg_val)
        return obj

    @classmethod
    def from_dict(cls, d: dict):
        return cls.new(**d)

    def as_dict(self):
        """

        :return: A dict of the declared class fields and their 'self' object values
        """
        return {key: getattr(self, key) for key, val in self._get_declared_class_mongo_attrs()}
