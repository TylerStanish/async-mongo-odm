import unittest

from tests.utils.SetupTemplates import setup_user_and_address_asyncio, setup_user_and_address_tornado


class TypeTest(unittest.TestCase):
    def setUp(self):
        setup_user_and_address_tornado(self)

    def test_type_checks_MongoObject_construction(self):
        with self.assertRaises(TypeError):
            self.Address.new(street='bla', city='jkl', zip='12345')

    def test_null_check_MongoObject(self):
        with self.assertRaises(TypeError):
            self.Address.new(street='the street', city='the city')

    def test_default_value_used_MongoObject(self):
        addr = self.Address.new(street='Something street', zip=12345)
        self.assertEqual('Something city', addr.city)


