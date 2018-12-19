import unittest
from unittest.mock import patch, Mock

from odm.type import MongoString, MongoId
from tests.utils import AsyncMock
from tests.utils.SetupTemplates import setup_user_and_address_tornado


class TornadoEngineTest(unittest.TestCase):

    def setUp(self):
        setup_user_and_address_tornado(self)

    @patch('motor.motor_tornado.MotorCollection.create_index')
    def test_creates_unique_indexes(self, create_index):
        class Payment(self.engine.Document):
            __collection_name__ = 'payments'
            _id = MongoId()
            unique_field = MongoString(unique=True)


        create_index.assert_called_with('unique_field', unique=True)

    @patch('motor.motor_tornado.MotorCollection.insert_one')
    def test_sets_id_on_saved_object(self, insert_one):
        async def wrapper_test():
            insert_one.return_value = AsyncMock(return_value=Mock(inserted_id='the_id'))

            user = self.User(name='hello person', address=self.Address.new(zip=12345))
            await self.engine.save(user)
            self.assertIsNotNone(user._id)
            self.assertEqual(user._id, 'the_id')

        self.loop.run_sync(wrapper_test)
