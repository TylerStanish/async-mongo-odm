class FieldStoreMixin:
    """
    This class represents a class that can hold Mongo fields. Currently, Document and MongoObject extend this class

    TODO add in as_dict method???
    """
    @classmethod
    def _get_declared_class_mongo_attrs(cls):
        from odm.type import MongoType  # moved this import line here to avoid that metaclass conflict because
        # MongoObject.py imports from here (and we import from its __init__ which in turns imports from MongoObject.py)
        # which would result in odm.meta.FieldStoreMixin not being registered as a class yet but as a module
        # (since we weren't done importing it yet)
        # But now that we only import it when we use it we allow the import of this meta module to complete
        return [(attr, val) for attr, val in vars(cls).items() if isinstance(val, MongoType)]

    @classmethod
    def validate_and_construct(cls, obj, kwargs):
        for attr, val in cls._get_declared_class_mongo_attrs():
            arg_val = kwargs.get(attr)

            if not val._nullable and not val._default and arg_val is None:
                raise TypeError(f'Got null argument for {attr} but {attr} is not nullable')

            if not issubclass(type(arg_val), val._python_type) and not val._nullable:
                raise TypeError(f'Got type {type(arg_val)} for {attr} but {attr} must be of type {val._python_type}')

            # check if the default value provided is the proper type as well
            if val._default and not (issubclass(type(val._default), val._python_type)):
                raise TypeError(
                    f'Got type {type(val._default)} for default field {attr} but must be of type {val._python_type}'
                )

            if val._default and arg_val is None:
                setattr(obj, attr, val._default)
            else:
                setattr(obj, attr, arg_val)

