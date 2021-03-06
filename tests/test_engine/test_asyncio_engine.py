import asyncio
import unittest
from unittest.mock import patch, Mock

from bson import ObjectId

from odm.engine import Engine
from odm.type import MongoString, MongoId, MongoNumber
from tests.utils import AsyncMock


class AsyncioEngineTest(unittest.TestCase):

    def setUp(self):
        self.engine = Engine.new_asyncio_engine('db_name')

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
            insert_one.return_value = AsyncMock(return_value=Mock(inserted_id=ObjectId('5c19d2fe7aca19816f57b285')))

            class Payment(self.engine.Document):
                __collection_name__ = 'payments'
                _id = MongoId()
                amount = MongoNumber()

            payment = Payment(amount=30)
            await self.engine.save(payment)
            self.assertEqual(payment._id, '5c19d2fe7aca19816f57b285')

        asyncio.get_event_loop().run_until_complete(wrapper_test())
