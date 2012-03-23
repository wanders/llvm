from .base import TestBase
from llvm.core import OpCode
from llvm.core.memorybuffer import MemoryBuffer
from llvm.core import PassRegistry
from llvm.core import Context
from llvm.core import Module

class TestBitReader(TestBase):

    def test_parse_bitcode(self):
        source = self.get_test_bc()
        m = Module.from_bitcode_buffer(MemoryBuffer(filename=source))
        print m.target
        print m.datalayout
