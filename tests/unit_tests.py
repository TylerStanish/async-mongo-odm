import asyncio
import unittest
from unittest.mock import patch, Mock

from odm.engine import Engine
from odm.type import MongoId, MongoString
from tests.utils import AsyncMock


class Tests(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.get_event_loop()
        self.engine = Engine('the_db_name')


        class User(self.engine.Document):
            __collection_name__ = 'testing_users'
            _id = MongoId()
            name = MongoString()


        self.User = User

    @patch('motor.motor_asyncio.AsyncIOMotorCollection.insert_one')
    def test_sets_id_on_saved_object(self, insert_one):
        async def wrapper_test():
            insert_one.return_value = AsyncMock(return_value=Mock(inserted_id='the_id'))

            engine = Engine('the_db_name')
            user = self.User(name='hello person')
            await engine.save(user)
            self.assertIsNotNone(user._id)
            self.assertEqual(user._id, 'the_id')

        self.loop.run_until_complete(wrapper_test())

    def test_class_field_mappings_get_created(self):
        mappings = self.engine.class_field_mappings[self.User]
        self.assertDictEqual(mappings, {'_id': MongoId(), 'name': MongoString()})

    def test_type_checks_object_construction(self):
        raise NotImplementedError

    def test_type_checks_MongoObject_construction(self):
        raise NotImplementedError


