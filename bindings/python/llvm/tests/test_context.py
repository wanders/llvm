from .base import TestBase
from llvm.core.context import Context

class TestContext(TestBase):
    def test_create(self):
        c = Context()
        del c

    def test_global(self):
        c = Context.GetGlobalContext()
        self.assertTrue(isinstance(c, Context))
        del c

    def test_global_singelton(self):
        c1 = Context.GetGlobalContext()
        c2 = Context.GetGlobalContext()
        self.assertTrue(c1 is c2)
