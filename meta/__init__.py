from odm.type import MongoType


def create_property(cls, attr_name: str, default=None) -> None:
    """
    Creates a property for the given :param: attr_name
    :param cls: The object to set the property on
    :param attr_name: A str that has the name of the attribute to set a property on
    :param default: The default value for the property value
    :return: None
    """

    def getter(self):
        return getattr(self, '_' + attr_name)
    getter = property(getter)  # basically decorate

    def setter(self, value):
        setattr(self, '_' + attr_name, value)
    setter = getter.setter(setter)  # basically decorate

    setattr(cls, '_' + attr_name, default)
    setattr(cls, attr_name, getter)
    setattr(cls, '_set_' + attr_name, setter)


def is_attr_mongo_type(obj, attr: str):
    return isinstance(getattr(obj, attr), MongoType)


class Registrar(type):
    """
    Metaclass that registers documents to fill the ODM
    """

    def __init__(cls, name, bases, namespace):
        super().__init__(cls)
        print('here in __init__ of registrar', name, bases)

        columns = []
        for var in list(vars(cls).keys()):  # copy .keys() so we don't get RuntimeError: dict changed size in iteration
            if isinstance(getattr(cls, var), MongoType):
                # create the properties on all of the fields recognized as MongoType
                columns.append(var)
                create_property(cls, var)
                # we can only add properties to the class! So we can't have this below

            elif var == '__collection_name__':
                print('the collection name is: ' + getattr(cls, var))

        def __init__(self, **kwargs):
            """
            The new monkey-patched constructor for the subclass that has this metaclass

            :param self: The regular 'self' that is given on object instantiation
            :param kwargs: The keyword args that are passed to be populated onto the attributes of 'self'
            :return: None
            """
            for key, val in kwargs.items():
                if key in columns:
                    # set the property to the value provided
                    setattr(self, '_' + key, val)
                else:
                    # otherwise we don't recognize it as a MongoType column so just set it on the object
                    setattr(self, key, val)

        nl = '\n'
        __init__.__doc__ = f'Constructor for document.\n {f":param {col}{nl}" for col in columns}'
        cls.__init__ = __init__
