import asyncio
import unittest
from unittest.mock import patch, Mock

from odm.engine import Engine
from odm.type import MongoId, MongoString, MongoObject, MongoNumber
from tests.utils import AsyncMock


class Tests(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.get_event_loop()
        self.engine = Engine.new_asyncio_engine('the_db_name', loop=self.loop)


        class Address(MongoObject):
            street = MongoString()
            city = MongoString(default='Something city')
            zip = MongoNumber(nullable=False)

        class User(self.engine.Document):
            __collection_name__ = 'testing_users'
            _id = MongoId()
            name = MongoString(nullable=False)
            email = MongoString(default='default_email@gmail.com')
            address = Address()


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
            'address': self.Address()
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
        raise NotImplementedError

    def test_default_value_used_Document(self):
        user = self.User(name='Pablo')
        self.assertEqual(user.email, 'default_email@gmail.com')

    def test_default_value_used_MongoObject(self):
        addr = self.Address.new(street='Something street', zip=12345)
        self.assertEqual(addr.city, 'Something city')

    def test_does_not_serialize_unwanted_fields(self):
        raise NotImplementedError

    def test_document_as_dict(self):
        raise NotImplementedError

    def test_document_from_json(self):
        raise NotImplementedError

    def test_document_from_dict(self):
        raise NotImplementedError
