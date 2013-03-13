from .base import TestBase

from llvm.debuginfo import DebugLoader, StructType

class TestDebugLoader(TestBase):
    def test_empty_is_empty(self):
        m = self.clang("", flags=["-g"])
        dl = DebugLoader(m)

        assert len(dl.enum_types) == 0
        assert len(dl.retained_types) == 0
        assert len(dl.subprograms) == 0
        assert len(dl.global_variables) == 0

    def test_struct(self):
        m = self.clang("""
                       struct X {int a; char *b; long c[10];};
                       struct X thestruct1, thestruct2;
                       """, flags=["-g"])
        dl = DebugLoader(m)

        assert len(dl.subprograms) == 0

        assert dl['thestruct1'].name == "thestruct1"
        assert dl['thestruct2'].name == "thestruct2"
        assert isinstance(dl['thestruct1'].type, StructType)
        assert dl['thestruct1'].type.name == "X"
        assert len(dl['thestruct1'].type.members) == 3
        assert dl['thestruct1'].type.members[0].name == "a"
        assert dl['thestruct1'].type.members[1].name == "b"
        assert dl['thestruct1'].type.members[2].name == "c"
        assert len(dl['thestruct1'].type.members[2].parent.members) == 1
        assert dl['thestruct1'].type.members[2].parent.members[0].low.value == 0
        assert dl['thestruct1'].type.members[2].parent.members[0].high.value == 10
        assert dl['thestruct1'].type.members[2].parent.parent.name == "long int"

