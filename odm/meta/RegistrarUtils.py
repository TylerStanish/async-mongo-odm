from odm.type import MongoType


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

    # add the fields dict {'JSON key value': 'Type/Class of that key'} for later use/reference
    engine.class_field_mappings[registrar_cls] = fields
