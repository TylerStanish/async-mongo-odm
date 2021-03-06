import asyncio
import unittest
from unittest.mock import patch, Mock

from bson import ObjectId

from odm.engine import Engine
from odm.type import MongoId, MongoString, MongoObject, MongoNumber, MongoForeignKey, MongoList
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

    @patch('motor.motor_asyncio.AsyncIOMotorCollection.insert_one')
    def test_Document_with_ForeignKey_serializes_as_string_after_saving(self, insert_one):
        insert_one.return_value = AsyncMock(return_value=Mock(inserted_id=ObjectId('5c19d2fe7aca19816f57b285')))

        async def wrapper_test():
            class User(self.engine.Document):
                __collection_name__ = 'users'
                _id = MongoId()
                name = MongoString()
                address = MongoForeignKey()

            user = User(address='5c19ce717aca19800a01af9d')
            await self.engine.save(user)
            self.assertEqual(user.as_dict(), {
                '_id': '5c19d2fe7aca19816f57b285',
                'name': None,
                'address': '5c19ce717aca19800a01af9d'
            })

        asyncio.get_event_loop().run_until_complete(wrapper_test())

    def test_Document_with_ForeignKey_serializes_as_ObjectId_when_persisting(self):

        class User(self.engine.Document):
            __collection_name__ = 'users'
            _id = MongoId()
            name = MongoString(default='Tammy')
            address = MongoForeignKey()

        user = User(address='5c19ce717aca19800a01af9d')
        self.assertEqual(user.as_dict(persisting=True), {
            '_id': None,
            'name': 'Tammy',
            'address': ObjectId('5c19ce717aca19800a01af9d')
        })

    def test_Document_as_dict_with_list(self):
        class User(self.engine.Document):
            __collection_name__ = 'users'
            _id = MongoId(serialize=False)
            name = MongoString()
            favorite_colors = MongoList(containing_type=str)

        user = User(name='Pablo', favorite_colors=['blue', 'orange'])
        self.assertListEqual(user.favorite_colors, ['blue', 'orange'])
        self.assertDictEqual(user.as_dict(), {
            'name': 'Pablo',
            'favoriteColors': ['blue', 'orange']
        })

    def test_Document_as_dict_with_list_containing_MongoObjects(self):
        class Address(MongoObject):
            street = MongoString()
            house_number = MongoNumber()

        class User(self.engine.Document):
            __collection_name__ = 'users'
            _id = MongoId(serialize=False)
            name = MongoString()
            addresses = MongoList(containing_type=Address)

        user = User(name='Pablo', addresses=[
            Address.new(street='Elm street', house_number=1),
            Address.new(street='Oak street', house_number=2)
        ])
        self.assertDictEqual(user.as_dict(), {
            'name': 'Pablo',
            'addresses': [
                {
                    'street': 'Elm street',
                    'houseNumber': 1
                },
                {
                    'street': 'Oak street',
                    'houseNumber': 2
                }
            ]
        })
        user1 = User(name='Tammy')
        user1.addresses = [
            Address.new(street='Elm street', house_number=1),
            Address.new(street='Oak street', house_number=2)
        ]
        self.assertDictEqual(user1.as_dict(), {
            'name': 'Tammy',
            'addresses': [
                {
                    'street': 'Elm street',
                    'houseNumber': 1
                },
                {
                    'street': 'Oak street',
                    'houseNumber': 2
                }
            ]
        })

    def test_Document_as_dict_with_list_raises_TypeError_when_serializing_wrong_type_in_list(self):
        with self.assertRaises(TypeError) as cm:
            class User(self.engine.Document):
                __collection_name__ = 'users'
                _id = MongoId(serialize=False)
                name = MongoString()
                favorite_colors = MongoList(containing_type=str)

            user = User(name='Pablo', favorite_colors=['green', 'blue', 24])
            user.as_dict()

        self.assertEqual('Got type int in MongoList declared as having type str', str(cm.exception))

    def test_Document_as_dict_with_list_raises_TypeError_when_serializing_wrong_type_in_list_MongoObject_entry(self):
        with self.assertRaises(TypeError) as cm:
            class Address(MongoObject):
                street = MongoString()
                house_number = MongoNumber()

            class User(self.engine.Document):
                __collection_name__ = 'users'
                _id = MongoId(serialize=False)
                name = MongoString()
                addresses = MongoList(containing_type=Address)

            user = User(name='Pablo')
            user.addresses = [
                Address.new(street=24, house_number=1)
            ]
            user.as_dict()

        self.assertEqual('Got type int for street but street must be of type str', str(cm.exception))

    def test_Document_as_dict_with_list_raises_TypeError_when_serializing_wrong_MongoObject_type_in_list(self):
        with self.assertRaises(TypeError) as cm:
            class Address(MongoObject):
                street = MongoString()
                house_number = MongoNumber()

            class Payment(MongoObject):
                amount = MongoNumber()

            class User(self.engine.Document):
                __collection_name__ = 'users'
                _id = MongoId(serialize=False)
                name = MongoString()
                addresses = MongoList(containing_type=Address)

            user = User(name='Pablo')
            user.addresses = [
                Payment.new(amount=20.0)
            ]
            user.as_dict()

        self.assertEqual('Got type Payment in MongoList declared as having type Address', str(cm.exception))
