import json
import unittest
from unittest.mock import patch, Mock

from bson import ObjectId

from odm.type import MongoNumber, MongoId, MongoString, MongoObject
from tests.utils import AsyncMock
from tests.utils.SetupTemplates import setup_user_and_address_asyncio, setup_user_and_address_tornado

"""
TODO set the defaults in the constructor, not on the class variables!
"""


class Tests(unittest.TestCase):
    def setUp(self):
        setup_user_and_address_asyncio(self)

    def test_type_checks_Document_construction(self):
        with self.assertRaises(TypeError) as cm:
            self.User(name=34)

        self.assertIn('Got type', str(cm.exception))
        self.assertIn('must be of type', str(cm.exception))
        self.assertNotIn('for default field', str(cm.exception))

    def test_null_check_Document(self):
        with self.assertRaises(TypeError) as cm:
            self.User()

        self.assertIn('Got null argument for', str(cm.exception))
        self.assertNotIn('for default field', str(cm.exception))

    def test_default_value_used_Document(self):
        user = self.User(name='Pablo', address=self.Address.new(zip=12345))
        self.assertEqual(user.email, 'default_email@gmail.com')

    def test_Document_does_not_serialize_unwanted_fields(self):
        user = self.User(name='Name', address=self.Address.new(zip=45678), age=43)
        self.assertFalse('age' in user.as_dict().keys())

    def test_Document_as_dict(self):
        user = self.User(email='theemail', name='thename', address=self.Address.new(zip=57382, country_code=3))
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
        with self.assertRaises(TypeError) as cm:
            self.User.from_json('{"age": 38, "address": {"city": "Chicago", "state": "IL"}}')

        self.assertIn('Got null argument for', str(cm.exception))

    def test_Document_from_dict_raises_when_missing_not_nullable_field(self):
        with self.assertRaises(TypeError) as cm:
            self.User.from_dict({"age": 38, "address": {"city": "Chicago", "state": "IL"}})

        self.assertIn('Got null argument for name', str(cm.exception))

    def test_Document_type_checks_from_dict(self):
        with self.assertRaises(TypeError) as cm:
            self.User.from_dict({
                'name': 'Tina',
                'email': 'person@bla.com',
                'age': '38',
                'address': {
                    'city': 'Chicago',
                    'street': 'Street',
                    'zip': 45923,
                    'country_code': 45
                }
            })

        self.assertEqual('Got type str for age but age must be of type Number', str(cm.exception))

    def test_Document_type_check_provided_default_argument(self):
        with self.assertRaises(TypeError) as cm:
            class Profile(self.engine.Document):
                _id = MongoId()
                info = MongoString(default=42)  # now that I think about it, we can check the default value in the
                # constructor of the MongoType to see if it matches?

        self.assertEqual('Got type int for default kwarg but must be of type str', str(cm.exception))

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
        self.assertEqual(user.age, 38)
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
        # above we don't have 'age': 38 because the age field is configured serialize=False on the User document class

    def test_Document_resistant_to_class_field_modification(self):
        self.User.name = MongoNumber()
        user = self.User(name='hello', address=self.Address.new(zip=12345))
        # the logic here is that we don't want class field modifications to affect how we check for types.
        # We know that it is resistant if the above line doesn't raise an error since it accepts str as name even
        # though we just modified it to a MongoNumber

    def test_subclassing(self):
        class AdminUser(self.User):
            email = MongoString(default='admin@website.com')

        user = AdminUser(name='Pablo', address=self.Address.new(zip=12345))
        self.assertEqual(user.name, 'Pablo')
        self.assertEqual(user.email, 'admin@website.com')

    def test_instantiates_MongoObject_with_default_values_rather_than_None(self):
        class Team(MongoObject):
            name = MongoString(default='The noobz')
            other_field = MongoString()

        class Game(self.engine.Document):
            _id = MongoId()
            team = Team()

        game = Game()
        self.assertEqual(game.team.name, 'The noobz')
        self.assertEqual(game.team.other_field, None)

    def test_can_add_extra_vars_to_Document_constructor(self):
        class Rand(self.engine.Document):
            _id = MongoId()

        rand = Rand(hello='there')
        self.assertEqual(rand.hello, 'there')

    @patch('motor.motor_asyncio.AsyncIOMotorCollection.find_one')
    def test_find_one(self, find_one):
        async def wrapper_test():
            find_one.return_value = AsyncMock(return_value={
                '_id': ObjectId('5c1406457aca19811fa07773'),
                'name': 'Tina',
                'email': 'person@bla.com',
                'age': 38,
                'address': {
                    'city': 'Chicago',
                    'street': 'Street',
                    'zip': 45923,
                    'country_code': 45
                }
            })
            user = await self.User.find_one({})
            self.assertDictEqual(user.as_dict(), {
                '_id': '5c1406457aca19811fa07773',
                'name': 'Tina',
                'email': 'person@bla.com',
                'address': {
                    'city': 'Chicago',
                    'street': 'Street',
                    'zip': 45923,
                }
            })

        self.loop.run_until_complete(wrapper_test())

    @patch('motor.motor_asyncio.AsyncIOMotorCollection.find_one')
    def test_find_one_backward_compatibility(self, find_one):
        async def wrapper_test():
            find_one.return_value = AsyncMock(return_value={
                '_id': ObjectId('5c1406457aca19811fa07773'),
                'name': 'Tina',
                'email': 'person@bla.com',
                'age': 38,
                'address': {
                    'city': 'Chicago',
                    'street': 'Street',
                    'zip': 45923,
                    'country_code': 45
                },
                'other_old_value_for_legacy': 42
            })
            user = await self.User.find_one({'dummy': 'data', 'mocking': 'instead'})
            self.assertDictEqual(user.as_dict(), {
                '_id': '5c1406457aca19811fa07773',
                'name': 'Tina',
                'email': 'person@bla.com',
                'address': {
                    'city': 'Chicago',
                    'street': 'Street',
                    'zip': 45923,
                }
            })

        self.loop.run_until_complete(wrapper_test())
