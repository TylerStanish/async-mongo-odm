import unittest

from odm.engine import Engine
from odm.type import MongoId, MongoString


class TestDocument(unittest.TestCase):
    def setUp(self):
        self.engine = Engine.new_asyncio_engine('the-db-name')

    def test_Document_as_dict(self):
        class User(self.engine.Document):
            _id = MongoId()
            name = MongoString()

        user = User(name='Pablo')
        self.assertDictEqual(user.as_dict(), {
            '_id': None,
            'name': 'Pablo'
        })

    def test_Document_serialization(self):
        class User(self.engine.Document):
            _id = MongoId(serialize=False)
            name = MongoString()

        user = User(name='Pablo')
        self.assertDictEqual(user.as_dict(), {
            'name': 'Pablo'
        })

    def test_Document_as_dict_camel_case(self):
        class User(self.engine.Document):
            _id = MongoId(serialize=False)
            first_name = MongoString()
            last_name = MongoString()

        user = User(first_name='John', last_name='Doe')
        self.assertDictEqual(user.as_dict(), {
            'firstName': 'John',
            'lastName': 'Doe'
        })

    def test_Document_serialize_as(self):
        class User(self.engine.Document):
            _id = MongoId(serialize=False)
            name = MongoString(serialize_as='theName')

        user = User(name='Pablo')
        self.assertDictEqual(user.as_dict(), {
            'theName': 'Pablo'
        })

    def test_Document_from_dict(self):
        class User(self.engine.Document):
            _id = MongoId()
            name = MongoString()

        user = User.from_dict({'name': 'Pablo'})
        self.assertEqual(user.name, 'Pablo')

    def test_Document_from_dict_with_serialize_as(self):
        class User(self.engine.Document):
            _id = MongoId()
            name = MongoString(serialize_as='theName')

        user = User.from_dict({'theName': 'Pablo'})
        self.assertEqual(user.name, 'Pablo')

    def test_Document_from_dict_converts_camel_to_snake(self):
        class User(self.engine.Document):
            _id = MongoId()
            name = MongoString()

        user = User.from_dict({'name': 'Pablo', 'randomVal': 123})
        self.assertEqual(user.random_val, 123)
