from .base import TestBase
from llvm.core.types import TypeFactory
from llvm.core.types import Type, IntType, FunctionType, TypeKind
from llvm.core.context import Context
from llvm.core.context import GlobalContext
#, TypeKind

class TestType(TestBase):

    def setUp(self):
        self.tfact = TypeFactory()

    def tearDown(self):
        self.tfact = None

    def test_instantiate_inttype(self):
        t = self.tfact.int()
        self.assertTrue(t is not None)
        self.assertTrue(isinstance(t, IntType))

    def test_inttype_kind(self):
        t = self.tfact.int()
        self.assertEquals(t.kind, TypeKind.Integer)

    def test_inttype_in_global_context(self):
        t = self.tfact.int(32)
        self.assertTrue(t.context is GlobalContext())

    def test_inttype_in_context(self):
        c = Context()
        t = TypeFactory(c).int(32)
        tc = t.context
        self.assertTrue(tc is c)

    def test_inttype_is_singelton_in_same_context(self):
        # this is a property of the llvm internals, but testing it
        # here makes sure proper unaliasing is done in python
        c = Context()
        t = TypeFactory(c).int(32)
        t2 = TypeFactory(c).int(32)
        t3 = self.tfact.int(32)

        assert t is t2
        assert t3 is not t2

    def test_inttype_width(self):
        t1 = self.tfact.int(1)
        assert t1.width == 1

        t7 = self.tfact.int(7)
        assert t7.width == 7

    def test_kind_enum(self):
        k = TypeKind.Integer
        self.assertTrue(isinstance(k, int))
        self.assertEquals(str(k), "TypeKind.Integer")

    def test_instantiate_voidtype(self):
        t = self.tfact.void()
        self.assertTrue(t is not None)
        self.assertTrue(isinstance(t, Type))

    def test_is_sized(self):
        t1 = self.tfact.int()
        self.assertTrue(t1.is_sized)

        t2 = self.tfact.void()
        self.assertTrue(not t2.is_sized)

    def test_function_type(self):
        Ti = self.tfact.int()
        Tf = self.tfact.float()
        func = self.tfact.function(Ti, [Ti, Tf])

        self.assertTrue(func is not None)
        self.assertTrue(isinstance(func, FunctionType))
        self.assertTrue(func.return_type is Ti)
        self.assertEquals(len(func.param_types), 2)
        # using 'is' makes sure proper unaliasing is done.
        self.assertTrue(func.param_types[0] is Ti)
        self.assertTrue(func.param_types[1] is Tf)

    def test_struct_type(self):
        Ti = self.tfact.int()
        Tf = self.tfact.float()
        Td = self.tfact.double()
        st = self.tfact.struct([Ti, Ti, Tf, Td])

        assert st is not None
        assert len(st.element_types) == 4
        assert st.element_types[0] is Ti
        assert st.element_types[1] is Ti
        assert st.element_types[2] is Tf
        assert st.element_types[3] is Td
        assert st.is_packed == False
        assert st.is_opaque == False

    def test_packed_struct(self):
        Ti = self.tfact.int()
        st = self.tfact.struct([Ti], True)
        assert st.is_packed == True
        assert st.is_opaque == False


    def test_opaque_struct(self):
        Ti = self.tfact.int()
        Th = self.tfact.half()

        st = self.tfact.named_struct("somestruct")
        assert st.is_opaque == True
        assert len(st.element_types) == 0
        assert st.name == "somestruct"

        st.set_body([Ti, Th], False)
        assert st.is_opaque == False
        assert len(st.element_types) == 2
        assert st.element_types[0] is Ti
        assert st.element_types[1] is Th
        assert st.__class__.__name__ == "StructType"


    def test_pointer_type(self):
        Ti = self.tfact.int()
        p = self.tfact.pointer(Ti)

        assert p is not None
        assert p.element_type is Ti
        assert p.address_space == 0

    def test_array_type(self):
        Tf = self.tfact.float()
        a = self.tfact.array(Tf, 20)

        assert a is not None
        assert a.element_type is Tf
        assert a.length == 20

    def test_vector_type(self):
        Td = self.tfact.double()
        v = self.tfact.vector(Td, 4)

        assert v is not None
        assert v.element_type is Td
        assert v.size == 4

    def test_mmx_instantiate(self):
        mmx = self.tfact.x86mmx()
        assert mmx is not None

    def test_float_types_instantiate(self):
        h = self.tfact.half()
        f = self.tfact.float()
        d = self.tfact.double()
        f128 = self.tfact.fp128()
        ppc = self.tfact.ppcfp128()
        f80 = self.tfact.x86fp80()

        assert h is not None
        assert f is not None
        assert d is not None
        assert f128 is not None
        assert ppc is not None
        assert f80 is not None
