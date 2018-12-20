import unittest
from unittest.mock import patch, Mock

from odm.engine import Engine
from odm.type import MongoString, MongoId, MongoNumber
from tests.utils import AsyncMock


class TornadoEngineTest(unittest.TestCase):

    def setUp(self):
        import tornado.ioloop
        self.loop = tornado.ioloop.IOLoop.current()
        self.engine = Engine.new_tornado_engine('db_name', loop=self.loop)

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

            class Payment(self.engine.Document):
                __collection_name__ = 'payments'
                _id = MongoId()
                amount = MongoNumber()

            payment = Payment(amount=30)
            await self.engine.save(payment)
            self.assertEqual(payment._id, 'the_id')

        self.loop.run_sync(wrapper_test)
