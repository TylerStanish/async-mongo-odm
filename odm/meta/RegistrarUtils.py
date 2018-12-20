def _init_registrar(engine, registrar_cls):
    """
    This is the method called whenever we want to do some initialization with a class that extends from engine.Document.
    So far this function only creates unique indexes on all the fields that are declared unique. Perhaps later there
    will be other initialization logic that needs to be done

    :param engine:
    :param registrar_cls:
    :return:
    """
    for field_name, val in registrar_cls._get_declared_class_mongo_attrs():
        if hasattr(val, '_unique') and val._unique:
            collection = getattr(getattr(engine.client, engine.db_name), registrar_cls.__collection_name__)
            collection.create_index(field_name, unique=True)
