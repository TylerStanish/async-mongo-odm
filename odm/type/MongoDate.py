import datetime

from odm.type import MongoType


class MongoDate(MongoType):
    """
    This library only has a MongoDate and not a MongoTimestamp, because according to the MongoDB docs:

    "The BSON timestamp type is for internal MongoDB use.
    For most cases, in application development, you will want to use the BSON date type."

    Also, PyMongo does not encode datetime.date or datetime.time instances.

    Basically, it (PyMongo) only supports datetime.datetime instances so use this for all dates and times, or create
    your own types
    """
    _python_type = datetime.datetime
