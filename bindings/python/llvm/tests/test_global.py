from llvm.core.value import Constant
from llvm.core.module import Module
from llvm.core.types import TypeFactory

from .base import TestBase

class TestModuleGlobals(TestBase):

    def setUp(self):
        self.tfact = TypeFactory()
        self.Ti = self.tfact.int(32)
        self.m = Module('test')

    def assertIRContains(self, needle):
        self.assert_(needle in self.m.to_assembly())

    def test_global_simple(self):
        self.m.add_global_variable(self.Ti, 'myglobal')

        self.assertIRContains('@myglobal = external global i32')

    def test_global_simple(self):
        self.m.add_global_variable(self.Ti, 'myglobal')
        self.m.add_global_variable(self.Ti, 'myglobal')

        print self.m.to_assembly()

        self.assertIRContains('@myglobal1 = external global i32')

    def test_global_find(self):
        g1 = self.m.add_global_variable(self.Ti, 'myglobal')
        g2 = self.m.get_global_variable_named('myglobal')

        self.assertTrue(g1 is g2)

    def test_global_find_fail(self):
        g = self.m.get_global_variable_named('nonexist')

        self.assertTrue(g is None)

    def test_global_initializer(self):
        g = self.m.add_global_variable(self.Ti, 'myglobal')

        g.initializer = Constant(self.Ti, 1000)

        self.assertIRContains('@myglobal = global i32 1000')

    def test_global_thread_local(self):
        g = self.m.add_global_variable(self.Ti, 'myglobal')

        g.initializer = Constant(self.Ti, 123)

        self.assertFalse(g.thread_local)

        g.thread_local = True

        self.assertTrue(g.thread_local)

        self.assertIRContains('@myglobal = thread_local global i32 123')

    def test_global_section(self):
        g = self.m.add_global_variable(self.Ti, 'myglobal')

        assert g.section == ""

        g.section = ".data.foo"

        assert g.section == ".data.foo"

        self.assertIRContains('@myglobal = external global i32, section ".data.foo"')

    def test_global_constant(self):
        g = self.m.add_global_variable(self.Ti, 'myglobal')

        g.initializer = Constant(self.Ti, 456)

        self.assertFalse(g.constant)

        g.constant = True

        self.assertTrue(g.constant)

        self.assertIRContains('@myglobal = constant i32 456')

    def test_global_alias(self):
        g = self.m.add_global_variable(self.Ti, 'myglobal')

        self.m.add_alias(g, 'myalias')

        self.assertIRContains("@myalias = alias i32* @myglobal")

    def test_function_alias(self):
        ft = self.tfact.function(self.Ti, [self.Ti, self.Ti])
        f = self.m.add_function(ft, "myfunc")

        self.m.add_alias(f, 'myalias')

        self.assertIRContains("@myalias = alias i32 (i32, i32)* @myfunc")

    def test_global_iterator(self):
        g1 = self.m.add_global_variable(self.Ti, 'myglobal1')
        g2 = self.m.add_global_variable(self.Ti, 'myglobal2')
        g3 = self.m.add_global_variable(self.Ti, 'myglobal3')

        gbls = list(self.m.global_variables)
        assert len(gbls) == 3
        assert g1 in gbls
        assert g2 in gbls
        assert g3 in gbls

