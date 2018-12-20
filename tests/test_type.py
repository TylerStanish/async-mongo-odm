import unittest

from odm.engine import Engine
from odm.type import MongoId, MongoString, MongoObject, MongoNumber


class TestType(unittest.TestCase):
    def setUp(self):
        self.engine = Engine.new_asyncio_engine('the-db-name')

    def test_Document_with_MongoObject_as_dict(self):
        class Address(MongoObject):
            street = MongoString()
            house_number = MongoNumber()

        class User(self.engine.Document):
            _id = MongoId()
            name = MongoString()
            address = Address()

        user = User(name='Tammy', address=Address.new(street='Circle street', house_number=42))
        self.assertEqual(user.as_dict(), {
            '_id': None,
            'name': 'Tammy',
            'address': {
                'street': 'Circle street',
                'houseNumber': 42
            }
        })

    def test_Document_with_MongoObject_as_dict_with_serialize_false(self):
        class Address(MongoObject):
            street = MongoString()
            house_number = MongoNumber(serialize=False)

        class User(self.engine.Document):
            _id = MongoId(serialize=False)
            name = MongoString()
            address = Address()


        user = User(name='Tammy', address=Address.new(street='Circle street', house_number=42))
        self.assertEqual(user.as_dict(), {
            'name': 'Tammy',
            'address': {
                'street': 'Circle street'
            }
        })
