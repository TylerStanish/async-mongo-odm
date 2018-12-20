import unittest

from odm.utils.CaseUtils import camel_to_snake, snake_to_camel


class TestCaseUtils(unittest.TestCase):

    def test_camel_to_snake(self):
        self.assertEqual(camel_to_snake('camelCase'), 'camel_case')
        self.assertEqual(camel_to_snake(''), '')

    def test_camel_to_snake_for_id(self):
        self.assertEqual(camel_to_snake('_id'), '_id')

    def test_camel_to_snake_with_already_snake(self):
        self.assertEqual(camel_to_snake('already_in_camel'), 'already_in_camel')

    def test_snake_to_camel(self):
        self.assertEqual(snake_to_camel('snake_case'), 'snakeCase')
        self.assertEqual(snake_to_camel(''), '')
        self.assertEqual(snake_to_camel('c'), 'c')

    def test_snake_to_camel_for_id(self):
        self.assertEqual(snake_to_camel('_id'), '_id')

    def test_snake_to_camel_with_already_camel(self):
        self.assertEqual(snake_to_camel('camelCase'), 'camelCase')
