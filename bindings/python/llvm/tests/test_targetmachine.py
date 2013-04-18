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

    def test_targetdata(self):
        x = "e-p:64:64:64-i1:8:8-i8:8:8-i16:16:16-i32:32:32-i64:64:64-f32:32:32-f64:64:64-v64:64:64-v128:128:128-a0:0:64-s0:64:64-f80:128:128-n8:16:32:64-S128"
        td = llvm.targetmachine.TargetData(x)

        assert td.byteorder == llvm.targetmachine.ByteOrdering.LittleEndian
