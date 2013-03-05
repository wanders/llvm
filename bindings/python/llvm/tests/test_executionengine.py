from llvm.core.module import Module
from llvm.core.value import Constant
from llvm.core.types import TypeFactory
from llvm.core.builder import Builder
from llvm.executionengine import ExecutionEngine, GenericValue


from .base import TestBase

class TestExecutionEngine(TestBase):

    def setUp(self):
        self.tfact = TypeFactory()
        self.Ti = self.tfact.int()
        self.m = Module('test')


    def test_instantiate(self):
        ee = ExecutionEngine(self.m)

        self.assertTrue(ee is not None)


    def test_global(self):
        g = self.m.add_global_variable(self.Ti, "someglobal")
        g.initializer = Constant(self.Ti, 0x12345678)

        ee = ExecutionEngine(self.m)

        p = ee.get_pointer_to_global(g)

        import ctypes
        p_i = ctypes.cast(p, ctypes.POINTER(ctypes.c_int))

        # TODO! Figure out this byteorder crap
        self.assertTrue(p_i.contents.value in (0x12345678, 0x78563412))

    def test_global_from_retval(self):
        typ = self.Ti

        g = self.m.add_global_variable(typ, "someglobal")
        g.initializer = Constant(typ, 0x12345678)

        ft = self.tfact.function(self.tfact.pointer(typ), [])
        f = self.m.add_function(ft, "eetest_ret_global")
        bb = f.append_basic_block("entry")
        builder = Builder(bb)
        builder.ret(g)

        self.m.verify()

        ee = ExecutionEngine(self.m)

        resval = ee.run_function(f)


        self.assertEquals(resval.as_pointer(), ee.get_pointer_to_global(g))

        import ctypes
        p_i = ctypes.cast(resval.as_pointer(), ctypes.POINTER(ctypes.c_int))

        # TODO! Figure out this byteorder crap
        self.assertTrue(p_i.contents.value in (0x12345678, 0x78563412))


    def test_global_define_on_outside(self):
        typ = self.Ti

        g = self.m.add_global_variable(typ, "someglobal")

        ft = self.tfact.function(typ, [])
        f = self.m.add_function(ft, "eetest_ret_global")
        bb = f.append_basic_block("entry")
        builder = Builder(bb)
        val = builder.load(g)
        builder.ret(val)

        self.m.verify()

        import ctypes

        someglobal = ctypes.c_int(100)

        me = Module("empty")
        ee = ExecutionEngine(me)

        ee.set_pointer_to_global(g, ctypes.byref(someglobal))

        ee.add_module(self.m)

        resval = ee.run_function(f)
        self.assertEquals(resval.as_int(), 100)

        someglobal.value = 1000

        resval = ee.run_function(f)
        self.assertEquals(resval.as_int(), 1000)

    def test_runfunc(self):
        typ = self.Ti

        ft = self.tfact.function(typ, [typ])
        f = self.m.add_function(ft, "eetest_add10")
        bb = f.append_basic_block("entry")
        builder = Builder(bb)
        f.args[0].name = "op"
        r = builder.add(f.args[0], Constant(typ, 10), "sum")
        builder.ret(r)

        ee = ExecutionEngine(self.m)

        argval = GenericValue.int(typ, 30)

        resval = ee.run_function(f, argval)

        self.assertEquals(resval.as_int(), 40)

    def test_create_python_proxy(self):
        typ = self.Ti

        ft = self.tfact.function(typ, [typ])
        f = self.m.add_function(ft, "eetest_add10")
        bb = f.append_basic_block("entry")
        builder = Builder(bb)
        f.args[0].name = "op"
        r = builder.add(f.args[0], Constant(typ, 10), "sum")
        builder.ret(r)

        ee = ExecutionEngine(self.m)

        pyfunc = ee.create_pyfunc(f)

        self.assertEquals(pyfunc(100), 110)
