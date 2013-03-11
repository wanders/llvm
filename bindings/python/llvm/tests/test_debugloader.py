from .base import TestBase

from llvm.debuginfo import DebugLoader, StructType

SRC = """
struct X {
 int a;
 char *b;
 long c[10];
};

struct X thestruct1;
struct X thestruct2;
"""

class TestDebugLoader(TestBase):
    def test_simple_struct(self):
        m = self.clang(SRC)
        dl = DebugLoader(m)

        assert dl['thestruct1'].name == "thestruct1"
        assert dl['thestruct2'].name == "thestruct2"
        assert isinstance(dl['thestruct1'].type, StructType)
        assert dl['thestruct1'].type.name == "X"
        assert len(dl['thestruct1'].type.members) == 3
        assert dl['thestruct1'].type.members[0].name == "a"
        assert dl['thestruct1'].type.members[1].name == "b"
        assert dl['thestruct1'].type.members[2].name == "c"


