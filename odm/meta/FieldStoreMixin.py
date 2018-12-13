class FieldStoreMixin:
    @classmethod
    def _get_declared_class_mongo_attrs(cls):
        from odm.type import MongoType  # moved this import line here to avoid that metaclass conflict because
        # MongoObject.py imports from here (and we import from its __init__ which in turns imports from MongoObject.py)
        # which would result in odm.meta.FieldStoreMixin not being registered as a class yet but as a module
        # (since we weren't done importing it yet)
        # But now that we only import it when we use it we allow the import of this meta module to complete
        return [(attr, val) for attr, val in vars(cls).items() if isinstance(val, MongoType)]
