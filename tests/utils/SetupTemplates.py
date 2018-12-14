import asyncio
import tornado.ioloop

from odm.engine import Engine
from odm.type import MongoObject, MongoString, MongoNumber, MongoId


def generate_classes(self):
    class Address(MongoObject):
        street = MongoString()
        city = MongoString(default='Something city')
        zip = MongoNumber(nullable=False)
        country_code = MongoNumber(serialize=False)


    class User(self.engine.Document):
        __collection_name__ = 'testing_users'
        _id = MongoId()
        name = MongoString(nullable=False)
        email = MongoString(default='default_email@gmail.com')
        address = Address()
        age = MongoNumber(serialize=False)


    self.Address = Address
    self.User = User


def setup_user_and_address_asyncio(self):
    self.loop = asyncio.get_event_loop()
    self.engine = Engine.new_asyncio_engine('the_db_name', loop=self.loop)

    generate_classes(self)


def setup_user_and_address_tornado(self):
    self.loop = tornado.ioloop.IOLoop.current()
    self.engine = Engine.new_tornado_engine(db_name='the_db_name', loop=self.loop)

    generate_classes(self)
