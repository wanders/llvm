import llvm.targetmachine

from .base import TestBase

class TestTargetMachine(TestBase):

    def test_targetlist(self):
        count = 0
        for t in llvm.targetmachine.list():
            count += 1
            assert isinstance(t.name, basestring)
            assert isinstance(t.description, basestring)
            assert isinstance(t.has_jit, bool)
            assert isinstance(t.has_target_machine, bool)
            assert isinstance(t.has_asm_backend, bool)

        self.assert_(count > 0)

