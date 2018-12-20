import inspect
from typing import List, Tuple

from bson import ObjectId

from odm.utils.CaseUtils import snake_to_camel, camel_to_snake


def vars_including_superclasses(cls):
    d = dict()
    mro_list = list(inspect.getmro(cls))
    mro_list.reverse()
    for clazz in mro_list:
        # will get vars starting with object, and then all of the superclasses until the current cls
        d = {**d, **vars(clazz)}  # overwrite the dict with the vars in the latest subclass
    return d


def find_attr_with_as_serialized_value(serialized_fields: list, as_serialized_val: str):
    for python_attr, potential_serialized_field in serialized_fields:
        if potential_serialized_field == as_serialized_val:
            return python_attr


class FieldStoreMixin:

    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)

        from odm.type import MongoType, MongoObject
        for attr, value in self._get_declared_class_mongo_attrs():
            if isinstance(getattr(self, attr), MongoType) and not isinstance(getattr(self, attr), MongoObject):
                setattr(self, attr, None)

    @classmethod
    def _get_declared_class_mongo_attrs(cls):
        from odm.type import MongoType  # moved this import line here to avoid that metaclass conflict because
        # MongoObject.py imports from here (and we import from its __init__ which in turns imports from MongoObject.py)
        # which would result in odm.meta.FieldStoreMixin not being registered as a class yet but as a module
        # (since we weren't done importing it yet)
        # But now that we only import it when we use it we allow the import of this meta module to complete

        return [(attr, val) for attr, val in vars_including_superclasses(cls).items() if isinstance(val, MongoType)]

    def validate(self, attr: str) -> None:
        """

        :raises: TypeError if the types do not match
        :param attr: The attribute to type check on self. This method assumes that key is declared as a MongoType
        :return: None
        """
        mongo_type_inst = getattr(self.__class__, attr)
        current_value = getattr(self, attr)
        if mongo_type_inst._nullable and current_value is None:
            return
        if not mongo_type_inst._nullable and not mongo_type_inst._default and current_value is None:
            raise TypeError(f'Got null argument for {attr} but {attr} is not nullable')
        if not issubclass(type(current_value), mongo_type_inst._python_type):
            raise TypeError(
                f'Got type {type(current_value).__name__} for {attr} but {attr} must be of type '
                f'{mongo_type_inst._python_type.__name__}'
            )

    def as_dict(self, keys_as_camel_case: bool = True, persisting=False):
        """
        Returns a dictionary representation of this object
        :raises TypeError: If the current object does not conform to the constraints declared in an engine.Document
        :return:
        """
        from odm.type import MongoObject, MongoForeignKey
        d = {}

        for attr, mongo_type_inst in self._get_declared_class_mongo_attrs():
            if mongo_type_inst._serialize or persisting:
                # set default if value is None and we are persisting, and of course only if there is a _default
                if mongo_type_inst._default and getattr(self, attr) is None:
                    setattr(self, attr, mongo_type_inst._default)
                self.validate(attr)

                curr_val_for_attr = getattr(self, attr)

                if mongo_type_inst._serialize_as:
                    if isinstance(curr_val_for_attr, MongoObject):
                        d[mongo_type_inst._serialize_as] = curr_val_for_attr.as_dict()
                    elif isinstance(mongo_type_inst, MongoForeignKey) and persisting:
                        d[mongo_type_inst._serialize_as] = ObjectId(curr_val_for_attr)
                    else:
                        d[mongo_type_inst._serialize_as] = curr_val_for_attr
                elif keys_as_camel_case:
                    if isinstance(curr_val_for_attr, MongoObject):
                        d[snake_to_camel(attr)] = curr_val_for_attr.as_dict()
                    elif isinstance(mongo_type_inst, MongoForeignKey) and persisting:
                        d[snake_to_camel(attr)] = ObjectId(curr_val_for_attr)
                    else:
                        d[snake_to_camel(attr)] = curr_val_for_attr
                else:
                    d[attr] = curr_val_for_attr

        return d

    @classmethod
    def _get_serialized_fields(cls) -> List[Tuple[str, str]]:
        """

        :return: Tuple where first value is the attribute of the python field and the second value is the
        potential serialized JSON key/attribute
        """
        serialized_fields = []
        for attr, mongo_inst in cls._get_declared_class_mongo_attrs():
            if not mongo_inst._serialize:
                continue
            if mongo_inst._serialize_as:
                serialized_fields.append((attr, mongo_inst._serialize_as))
            serialized_fields.append((attr, snake_to_camel(attr)))
            serialized_fields.append((attr, attr))

        return serialized_fields

    @classmethod
    def _clean_input_dict(cls, d: dict):
        kwargs = {}
        for key, val in d.items():
            set_kwarg = False
            for py_attr, potential_json_key in cls._get_serialized_fields():
                if key == potential_json_key:
                    kwargs[py_attr] = val
                    set_kwarg = True
                    break
            if not set_kwarg:
                kwargs[camel_to_snake(key)] = val

        return kwargs

    @classmethod
    def from_dict(cls, d: dict, _strict=True):
        return cls(**cls._clean_input_dict(d))
