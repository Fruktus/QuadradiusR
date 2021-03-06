from unittest import TestCase
from unittest.mock import MagicMock

from quadradiusr_server.utils import can_pass_argument, import_class


class UtilsTest(TestCase):
    def test_can_pass_argument(self):
        def test1(a):
            pass

        def test2(a, *, b):
            pass

        def test3(a, *args):
            pass

        def test4(a, **kwargs):
            pass

        def test5(a, /, b, *, c):
            pass

        self.assertTrue(can_pass_argument(test1, 'a'))
        self.assertFalse(can_pass_argument(test1, 'b'))

        self.assertTrue(can_pass_argument(test2, 'a'))
        self.assertTrue(can_pass_argument(test2, 'b'))
        self.assertFalse(can_pass_argument(test2, 'c'))

        self.assertTrue(can_pass_argument(test3, 'a'))
        self.assertFalse(can_pass_argument(test3, 'b'))

        self.assertTrue(can_pass_argument(test4, 'a'))
        self.assertTrue(can_pass_argument(test4, 'b'))

        self.assertFalse(can_pass_argument(test5, 'a'))
        self.assertTrue(can_pass_argument(test5, 'b'))
        self.assertTrue(can_pass_argument(test5, 'c'))
        self.assertFalse(can_pass_argument(test5, 'd'))

    def test_import_class(self):
        self.assertEqual(TestCase, import_class('unittest.TestCase'))
        self.assertEqual(TestCase, import_class('unittest.TestCase', subtype_of=TestCase))
        self.assertEqual(MagicMock, import_class('unittest.mock.MagicMock'))
        with self.assertRaises(ValueError):
            import_class('unittest.TestCase', subtype_of=str)
