import inspect


def vars_including_superclasses(cls):
    d = dict()
    mro_list = list(inspect.getmro(cls))
    mro_list.reverse()
    for clazz in mro_list:
        # will get vars starting with object, and then all of the superclasses until the current cls
        d = {**d, **vars(clazz)}  # overwrite the dict with the vars in the latest subclass
    return d


class FieldStoreMixin:
    """
    This class represents a class that can hold Mongo fields. Currently, Document and MongoObject extend this class

    TODO add in as_dict method???
    """
    @classmethod
    def _get_declared_class_mongo_attrs(cls, engine=None):
        from odm.type import MongoType  # moved this import line here to avoid that metaclass conflict because
        # MongoObject.py imports from here (and we import from its __init__ which in turns imports from MongoObject.py)
        # which would result in odm.meta.FieldStoreMixin not being registered as a class yet but as a module
        # (since we weren't done importing it yet)
        # But now that we only import it when we use it we allow the import of this meta module to complete
        if engine:
            return [(attr, val) for attr, val in engine.class_field_mappings[cls].items()]

        return [(attr, val) for attr, val in vars_including_superclasses(cls).items() if isinstance(val, MongoType)]

    @classmethod
    def validate_and_construct(cls, obj, kwargs, engine=None):
        from odm.type import MongoObject, MongoId
        for class_attr, class_attr_value in cls._get_declared_class_mongo_attrs(engine):
            arg_val = kwargs.get(class_attr)

            if not class_attr_value._nullable and not class_attr_value._default and arg_val is None:
                raise TypeError(f'Got null argument for {class_attr} but {class_attr} is not nullable')

            if not issubclass(type(arg_val), class_attr_value._python_type) and not isinstance(class_attr_value, MongoId):  # and not class_attr_value._nullable:
                if class_attr_value._nullable and arg_val is None:
                    if class_attr_value._default:
                        setattr(obj, class_attr, class_attr_value._default)
                    else:
                        if isinstance(class_attr_value, MongoObject):
                            setattr(obj, class_attr, class_attr_value.new())
                        else:
                            setattr(obj, class_attr, None)
                    continue
                if isinstance(class_attr_value, MongoObject) and isinstance(arg_val, dict):
                    setattr(obj, class_attr, class_attr_value.from_dict(arg_val))
                    continue
                raise TypeError(
                    f'Got type {type(arg_val).__name__} for {class_attr} '
                    f'but {class_attr} must be of type {class_attr_value._python_type.__name__}')

            if class_attr_value._default and arg_val is None:
                setattr(obj, class_attr, class_attr_value._default)
            else:
                setattr(obj, class_attr, arg_val)

