import unittest

from odm.type import MongoId, MongoString, MongoNumber
from tests.utils.SetupTemplates import setup_user_and_address_asyncio, setup_user_and_address_tornado


class EngineTest(unittest.TestCase):

    def setUp(self):
        setup_user_and_address_tornado(self)

    def test_class_field_mappings_get_created(self):
        mappings = self.engine.class_field_mappings[self.User]
        self.assertDictEqual(mappings, {
            '_id': MongoId(),
            'name': MongoString(nullable=False),
            'email': MongoString(default='default_email@gmail.com'),
            'address': self.Address(),
            'age': MongoNumber(serialize=False)
        })
