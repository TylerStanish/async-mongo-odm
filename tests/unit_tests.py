import asyncio
import unittest


class Tests(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.get_event_loop()

    def test_uses_correct_event_loop(self):
        pass

    def test_sets_columns_to_None_after_metaclass_registration(self):
        raise NotImplementedError

    def test_unique_indexes_created(self):
        raise NotImplementedError

    def test_class_col_mappings(self):
        raise NotImplementedError
