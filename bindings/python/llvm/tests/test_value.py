from llvm.core.module import Module
from llvm.core.types import TypeFactory
from llvm.core.value import Value, Function, Argument, Constant
#from llvm.core.metadata import MetaDataFactory

from .base import TestBase


class TestValue(TestBase):
    def test_function_simple(self):
        m = Module("m")
        tfact = TypeFactory()
        Ti = tfact.int()
        Tf = tfact.function(Ti, [Ti, Ti])

        f = m.add_function(Tf, "myfunc")

        assert isinstance(f, Value)
        assert isinstance(f, Function)

    def test_function_args(self):
        m = Module("m")
        tfact = TypeFactory()
        Ti = tfact.int()
        Tf = tfact.function(Ti, [Ti, Ti])

        f = m.add_function(Tf, "myfunc")

        assert len(f.args) == 2
        assert isinstance(f.args[0], Argument)
        assert isinstance(f.args[1], Argument)

        assert f.args[0].type is Ti

    def test_function_module(self):
        m = Module("m")
        tfact = TypeFactory()
        Ti = tfact.int()
        Tf = tfact.function(Ti, [Ti, Ti])

        f = m.add_function(Tf, "myfunc")

        assert f.module is m

    def test_function_arg_names(self):
        m = Module("m")
        tfact = TypeFactory()
        Ti = tfact.int()
        Tf = tfact.function(Ti, [Ti, Ti])

        f = m.add_function(Tf, "myfunc")

        assert len(f.args) == 2

        f.args[0].name = "a1"
        f.args[1].name = "a2"

        assert f.args[0].name == "a1"
        assert f.args[1].name == "a2"
        """
    def test_metadata(self):
        mf = MetaDataFactory()
        m = Module("t")
        tfact = TypeFactory()
        Ti = tfact.int()
        v = Constant(Ti, 123456)

        mn = mf.node(v, v)
        m.add_metadata_operand("t", mn)

        assert 'metadata !{i32 123456, i32 123456}' in m.to_assembly()
        assert v.is_constant() is True

        gmd = m.get_metadata("t")

        assert len(gmd) == 1
        assert gmd[0] is mn

    def test_metadata_string(self):
        mf = MetaDataFactory()
        m = Module("t")
        tfact = TypeFactory()
        Ti = tfact.int()
        v = Constant(Ti, 234)

        ms = mf.string("foo")
        mn = mf.node(v, ms)
        m.add_metadata_operand("t", mn)

        assert ms.value == "foo"
        assert ms == "foo"
        assert str(ms) == "foo"

        assert len(mn.operands) == 2

        assert mn[0] is v
        assert mn[1] is ms

        assert 'metadata !{i32 234, metadata !"foo"}' in m.to_assembly()

        gmd = m.get_metadata("t")

        assert len(gmd) == 1
        assert gmd[0] is mn
"""
    def test_undef(self):
        tfact = TypeFactory()
        Ti = tfact.int()
        v = Constant.undef(Ti)

        assert v.is_undef() is True
        assert v.is_null() is False
        assert v.is_constant() is True

    def test_null(self):
        tfact = TypeFactory()
        Tip = tfact.pointer(tfact.int())
        v = Constant.null(Tip)

        assert v.is_undef() is False
        assert v.is_null() is True
        assert v.is_constant() is True

