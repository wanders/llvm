from .base import TestBase
from ..core import MemoryBuffer

class TestCore(TestBase):
    def test_memory_buffer_create_from_file(self):
        source = self.get_test_binary()

        MemoryBuffer(filename=source)
