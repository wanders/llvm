from llvm.core.module import Module
from llvm.core.context import Context
from llvm.core.types import TypeFactory
from llvm.core.value import Constant
from llvm.core.memorybuffer import MemoryBuffer
from llvm.core.builder import Builder


from .base import TestBase, captured_stderr

import ctypes

class TestModuleAttrs(TestBase):
    def test_module_instantiate(self):
        m = Module("m")
        self.assertTrue(m is not None)
        self.assertTrue(isinstance(m, Module))

    def test_module_dump(self):
        m = Module("somemodule")
        with captured_stderr() as T:
            m.dump()

        self.assertTrue("; ModuleID = 'somemodule'" in T.data)

    def test_module_irstr(self):
        m = Module("irstr")
        self.assertTrue("; ModuleID = 'irstr'" in m.to_assembly())

    def test_module_target_and_datalayout(self):
        m = Module('test')

        self.assertTrue(hasattr(m, "target"))

        m.target = 'mytgt'
        self.assertEquals(m.target, 'mytgt')

        self.assertTrue(hasattr(m, "data_layout"))

        m.data_layout = 'a'
        self.assertEquals(m.data_layout, 'a')


    def test_module_instantiate_in_context(self):
        c = Context()
        m = Module("m", c)
        mc = m.context
        self.assertTrue(mc is c)


    def test_module_instantiate_in_context_broken(self):
        with self.assertRaises(ctypes.ArgumentError):
            Module("m", "imnotacontext")


    def test_module_from_bitcode(self):
        bc = "thisisinvalidbitcode"
        try:
            Module.from_bitcode_buffer(MemoryBuffer(contents=bc))
        except ValueError as e:
            assert e.message.endswith("Invalid bitcode signature")
            return

        assert 0 == "This should not be reached"

    def test_module_add_gv(self):
        m = Module("add_gv")
        tf = TypeFactory()
        m.add_global_variable(tf.int(), "myglobal")
        self.assertTrue("@myglobal = external global i32" in m.to_assembly())

    def test_module_verify_broken(self):
        m = Module("broken_verify")
        tf = TypeFactory()
        ft = tf.function(tf.int32(), [])
        f = m.add_function(ft, "test_module_verify_broken")
        bb = f.append_basic_block("entry")
        builder = Builder(bb)
        builder.ret(Constant(tf.int8(), 10))

        with self.assertRaises(ValueError) as e:
            m.verify()

        assert e.exception.message.startswith("Function return type does not match operand type of return inst")
