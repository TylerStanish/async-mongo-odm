from odm.type.MongoType import MongoType


class MongoDict(MongoType):
    """
    Use this when you don't care about "static" typing, that is, you don't care about declaring your fields beforehand
    and just want it to be a dict when retrieving from/saving to the database and/or don't care about validation
    """
    _python_type = dict
