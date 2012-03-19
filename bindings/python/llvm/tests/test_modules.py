from unittest import skip

from .base import TestBase
from ..core import MemoryBuffer
from ..modules import Module

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

    def test_parse_assembly_file(self):
        filename = self.get_resource_filename('helloworld.ll')

        m = Module(assembly_filename=filename)

    def test_parse_assembly_invalid_file(self):
        with self.assertRaises(Exception):
            Module(assembly_filename='DOESNOTEXIST.ll')

    @skip('Segfaults for some unknown reason.')
    def test_parse_assembly_str(self):
        s = 'declare i32 @puts(i8* nocapture) nounwind\n'

        Module(assembly_buffer=s)

    @skip('Segfaults for some unknown reason.')
    def test_parse_assembly_memory_buffer(self):
        filename = self.get_resource_filename('helloworld.ll')
        mb = MemoryBuffer(filename=filename)
        Module(assembly_buffer=mb)
