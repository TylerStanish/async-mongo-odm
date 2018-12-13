from odm.type import MongoType, MongoString


class FieldStoreMixin:
    @classmethod
    def _get_declared_class_mongo_attrs(cls):
        return [(attr, val) for attr, val in vars(cls).items() if isinstance(val, MongoType)]


def _init_registrar(engine, registrar_cls):
    fields = {}
    collection_name = ''
    for field_name, value in list(vars(registrar_cls).items()):
        if isinstance(value, MongoType):
            # create the properties on all of the fields recognized as MongoType
            fields[field_name] = value

        elif value.__class__ in list(engine.class_field_mappings.keys()):  # an already registered subclass exists
            fields[field_name] = value

        elif field_name == '__collection_name__':
            print('the collection name is: ' + value)
            collection_name = value

    if collection_name:  # if the user wants to create a collection for this Document
        for field_name, val in fields.items():
            if hasattr(val, '_unique') and val._unique:
                collection = getattr(getattr(engine.client, engine.db_name), collection_name)
                collection.create_index(field_name, unique=True)

            setattr(registrar_cls, field_name, getattr(val, '_default'))  # initialize that field to the default set

    # add the fields dict {'JSON key value': 'Type/Class of that key'} for later use/reference
    engine.class_field_mappings[registrar_cls] = fields

    def __init__(self, **kwargs):
        """
        The new monkey-patched constructor for the subclass that extends from Document and
        thus has the Registrar metaclass.

        :param self: The regular 'self' that is given on object instantiation
        :param kwargs: The keyword args that are passed to be populated onto the attributes of 'self'
        :return: An object extending Document
        """
        fields_covered = {key: False for key in fields.keys()}

        for field_name, val in kwargs.items():
            fields_covered[field_name] = True

            if field_name in fields.keys():
                if isinstance(val, dict):
                    # find the type of this 'field_name' from the class_field_mappings and then call the
                    # constructor of that class with the unpacked 'val' here
                    nested_obj = engine.class_field_mappings[self.__class__][field_name].__class__(**val)
                    setattr(self, field_name, nested_obj)
                else:
                    # type check
                    if not isinstance(val, fields[field_name]._python_type):
                        raise TypeError(f'Invalid type for kwarg {field_name}')

                    # None check
                    if not fields[field_name]._nullable and val is None:
                        raise TypeError(f'Got None for {field_name} but {field_name} is not nullable')

                    setattr(self, field_name, val)
            else:
                # just set it even though we don't recognize it as a MongoType field
                setattr(self, field_name, val)

        # final nullability check
        for field_name, contained in fields_covered.items():
            if contained is False and not fields[field_name]._nullable:
                raise TypeError(f'Missing argument for {field_name} but {field_name} is not nullable')

    registrar_cls.__init__ = __init__
