from .base import TestBase

from ..core import Module

class TestModule(TestBase):
    def test_construct_global(self):
        Module('foobar')

    def test_layout(self):
        m = Module('foo')
        self.assertEqual(m.layout, '')

        m.layout = 'test'
        self.assertEqual(m.layout, 'test')

    def test_target(self):
        m = Module('foo')
        self.assertEqual(m.target, '')

        m.target = 'i686-apple-darwin9'
        self.assertEqual(m.target, 'i686-apple-darwin9')
