from .base import TestBase
from llvm.core.context import Context, GlobalContext

class TestContext(TestBase):
    def test_create(self):
        c = Context()
        del c

    def test_global(self):
        c = GlobalContext()
        self.assertTrue(isinstance(c, Context))
        del c

    def test_global_singelton(self):
        c1 = GlobalContext()
        c2 = GlobalContext()
        self.assertTrue(c1 is c2)
