import asyncio
import unittest
from unittest.mock import patch, Mock

from bson import ObjectId

from odm.engine import Engine
from odm.type import MongoId, MongoString, MongoObject, MongoNumber
from tests.utils import AsyncMock


class TestType(unittest.TestCase):
    def setUp(self):
        self.engine = Engine.new_asyncio_engine('the-db-name')

    def test_Document_with_MongoObject_as_dict(self):
        class Address(MongoObject):
            street = MongoString()
            house_number = MongoNumber()

        class User(self.engine.Document):
            __collection_name__ = 'users'
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
            __collection_name__ = 'users'
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

    def test_Document_with_MongoObject_as_dict_and_serialize_as(self):
        class Address(MongoObject):
            street = MongoString()
            house_number = MongoNumber(serialize_as='housenumber')

        class User(self.engine.Document):
            __collection_name__ = 'users'
            _id = MongoId()
            name = MongoString()
            address = Address(serialize_as='theaddress')

        user = User(name='Tammy', address=Address.new(street='Circle street', house_number=42))
        self.assertEqual(user.as_dict(), {
            '_id': None,
            'name': 'Tammy',
            'theaddress': {
                'street': 'Circle street',
                'housenumber': 42
            }
        })

    @patch('motor.motor_asyncio.AsyncIOMotorCollection.insert_one')
    def test_Document_with_MongoObject_as_dict_with_default(self, insert_one):
        insert_one.return_value = AsyncMock(return_value=Mock(inserted_id=ObjectId('5c19d2fe7aca19816f57b285')))

        async def wrapper_test():
            class Address(MongoObject):
                street = MongoString(default='Circle street')
                house_number = MongoNumber()

            class User(self.engine.Document):
                __collection_name__ = 'users'
                _id = MongoId()
                name = MongoString(default='Tammy')
                address = Address()

            user = User(address=Address.new(house_number=42))
            self.assertEqual(user.as_dict(), {
                '_id': None,
                'name': 'Tammy',
                'address': {
                    'street': 'Circle street',
                    'houseNumber': 42
                }
            })
            await self.engine.save(user)
            self.assertEqual(user.as_dict(), {
                '_id': '5c19d2fe7aca19816f57b285',
                'name': 'Tammy',
                'address': {
                    'street': 'Circle street',
                    'houseNumber': 42
                }
            })

        asyncio.get_event_loop().run_until_complete(wrapper_test())

    def test_Document_with_MongoObject_as_dict_with_nullable_False(self):
        class Address(MongoObject):
            street = MongoString()
            house_number = MongoNumber()

        class User(self.engine.Document):
            __collection_name__ = 'users'
            _id = MongoId()
            name = MongoString(nullable=False)
            address = Address()

        user = User(address=Address.new(street='Circle street', house_number=42))
        with self.assertRaises(TypeError) as cm:
            user.as_dict()

        self.assertEqual('Got null argument for name but name is not nullable', str(cm.exception))

    def test_Document_with_MongoObject_as_dict_with_nullable_False_in_nested_MongoObject(self):
        class Address(MongoObject):
            street = MongoString(nullable=False)
            house_number = MongoNumber()

        class User(self.engine.Document):
            __collection_name__ = 'users'
            _id = MongoId()
            name = MongoString()
            address = Address()

        user = User(name='Tammy', address=Address.new(house_number=42))
        with self.assertRaises(TypeError) as cm:
            user.as_dict()

        self.assertEqual('Got null argument for street but street is not nullable', str(cm.exception))

    def test_Document_with_MongoObject_as_dict_with_default_and_nullable_does_not_raise_TypeError(self):
        class Address(MongoObject):
            street = MongoString()
            house_number = MongoNumber()

        class User(self.engine.Document):
            __collection_name__ = 'users'
            _id = MongoId()
            name = MongoString(default='Tammy', nullable=False)
            address = Address()

        user = User(address=Address.new(street='Circle street', house_number=42))
        self.assertEqual(user.as_dict(), {
            '_id': None,
            'name': 'Tammy',
            'address': {
                'street': 'Circle street',
                'houseNumber': 42
            }
        })
