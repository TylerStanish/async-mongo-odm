import unittest
from unittest.mock import patch, Mock

from odm.type import MongoId, MongoString, MongoNumber
from tests.utils import AsyncMock
from tests.utils.SetupTemplates import setup_user_and_address


class EngineTest(unittest.TestCase):

    def setUp(self):
        setup_user_and_address(self)

    @patch('motor.motor_asyncio.AsyncIOMotorCollection.create_index')
    def test_creates_unique_indexes(self, create_index):
        class Payment(self.engine.Document):
            __collection_name__ = 'payments'
            _id = MongoId()
            unique_field = MongoString(unique=True)

        create_index.assert_called_with('unique_field', unique=True)

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
