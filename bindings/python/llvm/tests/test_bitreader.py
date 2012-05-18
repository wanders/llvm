from .base import TestBase
from ..core import OpCode
from ..core import MemoryBuffer
from ..core import PassRegistry
from ..core import Context
from ..core import Module

class TestBitReader(TestBase):

    def test_parse_bitcode(self):
        source = self.get_test_bc()
        m = Module.from_bitcode_buffer(MemoryBuffer(filename=source))
        print m.target
        print m.datalayout
