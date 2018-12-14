import asyncio
import json
import unittest
from unittest.mock import patch, Mock

from odm.engine import Engine
from odm.type import MongoId, MongoString, MongoObject, MongoNumber
from tests.utils import AsyncMock


"""
TODO set the defaults in the constructor, not on the class variables!
"""


class Tests(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.get_event_loop()
        self.engine = Engine.new_asyncio_engine('the_db_name', loop=self.loop)


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

    @patch('motor.motor_asyncio.AsyncIOMotorCollection.insert_one')
    def test_sets_id_on_saved_object(self, insert_one):
        async def wrapper_test():
            insert_one.return_value = AsyncMock(return_value=Mock(inserted_id='the_id'))

            user = self.User(name='hello person')
            await self.engine.save(user)
            self.assertIsNotNone(user._id)
            self.assertEqual(user._id, 'the_id')

        self.loop.run_until_complete(wrapper_test())

    def test_class_field_mappings_get_created(self):
        mappings = self.engine.class_field_mappings[self.User]
        self.assertDictEqual(mappings, {
            '_id': MongoId(),
            'name': MongoString(nullable=False),
            'email': MongoString(default='default_email@gmail.com'),
            'address': self.Address(),
            'age': MongoNumber(serialize=False)
        })

    def test_type_checks_Document_construction(self):
        with self.assertRaises(TypeError):
            self.User(name=34)

    def test_type_checks_MongoObject_construction(self):
        with self.assertRaises(TypeError):
            self.Address.new(street='bla', city='jkl', zip='12345')

    def test_null_check_Document(self):
        with self.assertRaises(TypeError):
            self.User()

    def test_null_check_MongoObject(self):
        with self.assertRaises(TypeError):
            self.Address.new(street='the street', city='the city')

    @patch('motor.motor_asyncio.AsyncIOMotorCollection.create_index')
    def test_creates_unique_indexes(self, create_index):
        class Payment(self.engine.Document):
            __collection_name__ = 'payments'
            _id = MongoId()
            unique_field = MongoString(unique=True)

        create_index.assert_called()

    def test_default_value_used_Document(self):
        user = self.User(name='Pablo')
        self.assertEqual(user.email, 'default_email@gmail.com')

    def test_default_value_used_MongoObject(self):
        addr = self.Address.new(street='Something street', zip=12345)
        self.assertEqual(addr.city, 'Something city')

    def test_Document_does_not_serialize_unwanted_fields(self):
        user = self.User(name='Name', address=self.Address.new(zip=45678), age=43)
        self.assertFalse('age' in user.as_dict().keys())

    def test_Document_as_dict(self):
        user = self.User(email='theemail', name='thename')
        user.address = self.Address.new(zip=57382, country_code=3)
        res = user.as_dict()
        self.assertDictEqual(res, {
            '_id': None,
            'email': 'theemail',
            'name': 'thename',
            'address': {
                'street': None,
                'city': 'Something city',
                'zip': 57382
            }
        })

    def test_Document_from_json_raises_when_missing_not_nullable_field(self):
        with self.assertRaises(TypeError):
            self.User.from_json('{"age": 38, "address": {"city": "Chicago", "state": "IL"}}')

    def test_Document_from_dict_raises_when_missing_not_nullable_field(self):
        with self.assertRaises(TypeError):
            self.User.from_json({"age": 38, "address": {"city": "Chicago", "state": "IL"}})

    def test_Document_from_json(self):
        d = {
            'name': 'Tina',
            'email': 'person@bla.com',
            'age': 38,
            'address': {
                'city': 'Chicago',
                'street': 'Street',
                'zip': 45923,
                'country_code': 45
            }
        }
        user = self.User.from_json(json.dumps(d))
        self.assertDictEqual(user.as_dict(), {
            '_id': None,
            'name': 'Tina',
            'email': 'person@bla.com',
            'address': {
                'city': 'Chicago',
                'street': 'Street',
                'zip': 45923
            }
        })

    def test_Document_from_dict(self):
        d = {
            'name': 'Tina',
            'email': 'person@bla.com',
            'age': 38,
            'address': {
                'city': 'Chicago',
                'street': 'Street',
                'zip': 45923,
                'country_code': 45
            }
        }
        user = self.User.from_dict(d)
        self.assertDictEqual(user.as_dict(), {
            '_id': None,
            'name': 'Tina',
            'email': 'person@bla.com',
            'address': {
                'city': 'Chicago',
                'street': 'Street',
                'zip': 45923
            }
        })
