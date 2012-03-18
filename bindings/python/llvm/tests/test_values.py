from .base import TestBase
from ..values import OpCode

class TestOpcode(TestBase):
    def test_opcode(self):
        self.assertTrue(hasattr(OpCode, 'Ret'))
        self.assertTrue(isinstance(OpCode.Ret, OpCode))
        self.assertEqual(OpCode.Ret.value, 1)

        op = OpCode.from_value(1)
        self.assertTrue(isinstance(op, OpCode))
        self.assertEqual(op, OpCode.Ret)

