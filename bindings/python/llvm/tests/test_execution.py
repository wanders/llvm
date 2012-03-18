from .base import TestBase

from ..execution import ExecutionEngine
from ..modules import Module
from ..values import Function

class TestExecutionEngine(TestBase):
    def test_instantiate(self):
        module = Module(name='test')

        engine = ExecutionEngine(module)

    def test_add_module(self):
        foo = Module(name='foo')
        bar = Module(name='bar')
        baz = Module(name='baz')

        engine = ExecutionEngine(foo)
        engine.add_module(bar)
        engine.add_module(baz)

    def test_remove_module(self):
        foo = Module(name='foo')
        bar = Module(name='bar')
        baz = Module(name='baz')

        engine = ExecutionEngine(foo)
        engine.add_module(bar)
        engine.add_module(baz)

        foo_ptr = foo._ptr
        owned_count = len(engine._owned_objects)
        engine.remove_module(foo)

        self.assertNotEqual(foo._ptr, foo_ptr)
        self.assertEqual(len(engine._owned_objects), owned_count - 1)

    def test_run_static_constructors(self):
        module = Module(name='foo')

        # TODO add static constructors and destructors to module.

        engine = ExecutionEngine(module)

        engine.run_static_constructors()
        engine.run_static_destructors()

    def test_main_missing_main(self):
        module = Module(name='foo')
        engine = ExecutionEngine(module)

        with self.assertRaises(Exception):
            engine.run_main()

    def test_find_function_missing(self):
        module = Module(name='foo')
        engine = ExecutionEngine(module)

        self.assertIsNone(engine.find_function('main'))

    def test_find_function_success(self):
        filename = self.get_resource_filename('helloworld.ll')

        # TODO need API to read LLVM Assembly!
        return
        #module = Module(bitcode_filename=filename)

        #fn = module.find_function('main')
        #self.assertIsInstance(fn, Function)
