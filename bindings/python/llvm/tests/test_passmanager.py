from llvm.core.module import Module
from llvm.core.context import Context
from llvm.core.types import TypeFactory
from llvm.core.value import Constant
from llvm.passmanager import ModulePassManager, PassManagerBuilder
from llvm.core.builder import Builder


from .base import TestBase

class TestModulePassManager(TestBase):
    def test_mpm_instantiate(self):
        mpm = ModulePassManager()
        assert mpm is not None

    def test_mpm_run_empty(self):
        mpm = ModulePassManager()
        m = Module("foo")

        mpm.run(m)


    def test_mpm_run_dead_decl(self):
        m = Module("foo")

        tf = TypeFactory()
        ft = tf.function(tf.int32(), [])
        f = m.add_function(ft, "unused_prototype")
        r1 = m.to_assembly()

        mpm = ModulePassManager()
        mpm.run(m)
        r2 = m.to_assembly()

        mpm.add_strip_dead_prototypes_pass()
        mpm.run(m)
        r3 = m.to_assembly()

        assert "unused_prototype" in r1
        assert "unused_prototype" in r2
        assert "unused_prototype" not in r3

