#===- types.py - Python Object Bindings ----------------------*- python -*--===#
#
#                     The LLVM Compiler Infrastructure
#
# This file is distributed under the University of Illinois Open Source
# License. See LICENSE.TXT for details.
#
#===------------------------------------------------------------------------===#

from ctypes import string_at

from ..common import LLVMObject
from ..common import LLVMEnum

from ..common import get_library, create_c_object_p_array, create_empty_c_object_p_array

from .context import Context, GlobalContext

lib = get_library()

@lib.c_enum("LLVMTypeKind", "LLVM", "TypeKind")
class TypeKind(LLVMEnum):
    _INCLUDE_NUM = False

@lib.c_name("LLVMTypeRef")
class Type(LLVMObject):
    """Base class of all Type objects in LLVM

The subclasses of the Type class gives access to information about the
different types in the LLVM IR. These classes should not be
instantiated by the user of the Python bindings, instead use the
`TypeFactory`

"""

    def __init__(self, ptr):
        # this class should never be instantiated,
        # only subclasses
        assert self.__class__ != Type
        LLVMObject.__init__(self, ptr)

    @property
    def kind(self):
        """The `TypeKind` of this Type"""
        return lib.LLVMGetTypeKind(self)

    @property
    def is_sized(self):
        """Whether this type has a size"""
        return bool(lib.LLVMTypeIsSized(self))

    @property
    def context(self):
        """The context this Type was allocated in"""
        return Context._from_ptr(lib.LLVMGetTypeContext(self))

    @staticmethod
    def _create_from_ptr(ptr):
        class DummyType(Type):
            def __init__(self):
                self._as_parameter_ = ptr

        kind = lib.LLVMGetTypeKind(DummyType())
        cls = {TypeKind.Void: VoidType,
               TypeKind.Half: HalfType,
               TypeKind.Float: FloatType,
               TypeKind.Double: DoubleType,
               TypeKind.X86_FP80: X86_FP80Type,
               TypeKind.FP128: FP128Type,
               TypeKind.PPC_FP128: PPC_FP128Type,
               TypeKind.Label: LabelType,
               TypeKind.Integer: IntType,
               TypeKind.Function: FunctionType,
               TypeKind.Struct: StructType,
               TypeKind.Array: ArrayType,
               TypeKind.Pointer: PointerType,
               TypeKind.Vector: VectorType,
               TypeKind.Metadata: MetadataType,
               TypeKind.X86_MMX: X86_MMXType}[kind]

        return cls._from_ptr(ptr)

class IntType(Type):
    @property
    def width(self):
        """The width of the integer type, in bits."""
        return lib.LLVMGetIntTypeWidth(self)

class VoidType(Type):
    pass
class LabelType(Type):
    pass

class FunctionType(Type):
    @property
    def return_type(self):
        """The type of the return value of the function"""
        return Type._create_from_ptr(lib.LLVMGetReturnType(self))

    @property
    def param_types(self):
        """Returns a list containing the types of the parameters to the function"""
        p = create_empty_c_object_p_array(lib.LLVMCountParamTypes(self))
        lib.LLVMGetParamTypes(self, p)
        return map(Type._create_from_ptr, p)

class StructType(Type):
    def set_body(self, element_types, packed=False):
        ell = create_c_object_p_array(element_types, Type)
        lib.LLVMStructSetBody(self, ell, len(element_types), packed)

    @property
    def name(self):
        return string_at(lib.LLVMGetStructName(self))

    @property
    def element_types(self):
        e = create_empty_c_object_p_array(lib.LLVMCountStructElementTypes(self))
        lib.LLVMGetStructElementTypes(self, e)
        return map(Type._create_from_ptr, e)

    @property
    def is_opaque(self):
        return bool(lib.LLVMIsOpaqueStruct(self))

    @property
    def is_packed(self):
        return bool(lib.LLVMIsPackedStruct(self))

class ArrayishType(Type):
    @property
    def element_type(self):
        return Type._create_from_ptr(lib.LLVMGetElementType(self))

class ArrayType(ArrayishType):
    @property
    def length(self):
        return lib.LLVMGetArrayLength(self)

class VectorType(ArrayishType):
    @property
    def size(self):
        return lib.LLVMGetVectorSize(self)

class PointerType(ArrayishType):
    @property
    def address_space(self):
        return lib.LLVMGetPointerAddressSpace(self)

class FloatishType(Type):
    pass
class HalfType(FloatishType):
    pass
class FloatType(FloatishType):
    pass
class DoubleType(FloatishType):
    pass
class X86_FP80Type(FloatishType):
    pass
class FP128Type(FloatishType):
    pass
class PPC_FP128Type(FloatishType):
    pass
class MetadataType(Type):
    pass
class X86_MMXType(Type):
    pass


class TypeFactory(object):
    """Factory for creating Type objects.
    """
    def __init__(self, context=None):
        """Create a new TypeFactory.

        The types will be allocated in `context` or the global
        context if no context was specified.

        """
        if context is None:
            context = GlobalContext()
        self.context = context

    def _make_type(self, func, *args):
        return Type._create_from_ptr(func(self.context, *args))

    def int1(self):
        return self._make_type(lib.LLVMInt1TypeInContext)

    def int8(self):
        return self._make_type(lib.LLVMInt8TypeInContext)

    def int16(self):
        return self._make_type(lib.LLVMInt16TypeInContext)

    def int32(self):
        return self._make_type(lib.LLVMInt32TypeInContext)

    def int64(self):
        return self._make_type(lib.LLVMInt64TypeInContext)

    def int(self, bits=32):
        return self._make_type(lib.LLVMIntTypeInContext, bits)

    def half(self):
        return self._make_type(lib.LLVMHalfTypeInContext)

    def float(self):
        return self._make_type(lib.LLVMFloatTypeInContext)

    def double(self):
        return self._make_type(lib.LLVMDoubleTypeInContext)

    def x86fp80(self):
        return self._make_type(lib.LLVMX86FP80TypeInContext)

    def fp128(self):
        return self._make_type(lib.LLVMFP128TypeInContext)

    def ppcfp128(self):
        return self._make_type(lib.LLVMPPCFP128TypeInContext)

    def named_struct(self, name):
        return self._make_type(lib.LLVMStructCreateNamed, name)

    def void(self):
        return self._make_type(lib.LLVMVoidTypeInContext)

    def label(self):
        return self._make_type(lib.LLVMLabelTypeInContext)

    def x86mmx(self):
        return self._make_type(lib.LLVMX86MMXTypeInContext)

    def function(self, rettype, argtypes, isvararg=False):
        arglist = create_c_object_p_array(argtypes, Type)
        return Type._create_from_ptr(lib.LLVMFunctionType(rettype, arglist, len(arglist), isvararg))

    def struct(self, element_types, packed=False):
        ell = create_c_object_p_array(element_types, Type)
        return Type._create_from_ptr(lib.LLVMStructTypeInContext(self.context, ell, len(element_types), packed))

    def array(self, element_type, count):
        return Type._create_from_ptr(lib.LLVMArrayType(element_type, count))

    def vector(self, element_type, count):
        return Type._create_from_ptr(lib.LLVMVectorType(element_type, count))

    def pointer(self, element_type, address_space = 0):
        return Type._create_from_ptr(lib.LLVMPointerType(element_type, address_space))

