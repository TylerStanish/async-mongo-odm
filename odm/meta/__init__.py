from odm.type import MongoType


def _init_registrar(self, cls, name, bases, namespace):
    print('here in __init__ of registrar', name, bases)

    columns = {}
    collection_name = ''
    for var in list(vars(cls).keys()):  # copy .keys() so we don't get RuntimeError: dict changed size in iteration
        class_var = getattr(cls, var)
        if isinstance(class_var, MongoType):
            # create the properties on all of the fields recognized as MongoType
            columns[var] = class_var

        elif class_var.__class__ in list(self.class_col_mappings.keys()):
            columns[var] = class_var

        elif var == '__collection_name__':
            print('the collection name is: ' + class_var)
            collection_name = class_var

    self.class_col_mappings[cls] = columns
    if collection_name:
        for field_name, val in self.class_col_mappings[cls].items():
            if hasattr(val, 'unique') and val.unique:
                collection = getattr(getattr(self.client, self.db_name), collection_name)
                collection.create_index(field_name, unique=True)

            setattr(cls, field_name, None)  # lastly initialize that field value None

    def __init__(self1, **kwargs):
        """
        The new monkey-patched constructor for the subclass that extends from Document and
        thus has the Registrar metaclass.

        :param self1: The regular 'self' that is given on object instantiation
        :param kwargs: The keyword args that are passed to be populated onto the attributes of 'self'
        :return: None
        """
        for key, val in kwargs.items():
            if key in columns.keys():
                if isinstance(val, dict):
                    # find the type of this 'key' from the class_col_mappings and then call the
                    # constructor of that class with the 'val' here
                    nested_obj = self.class_col_mappings[self1.__class__][key].__class__(**val)
                    setattr(self1, key, nested_obj)
                # set the property to the value provided
                else:
                    setattr(self1, key, val)
            else:
                # otherwise we don't recognize it as a MongoType column
                raise ValueError(f'Incorrect keyword argument "{key}"')

    cls.__init__ = __init__
