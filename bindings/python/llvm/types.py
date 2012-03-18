#===- types.py - Python LLVM Bindings ------------------------*- python -*--===#
#
#                     The LLVM Compiler Infrastructure
#
# This file is distributed under the University of Illinois Open Source
# License. See LICENSE.TXT for details.
#
#===------------------------------------------------------------------------===#

r"""
This module defines classes which represent types in LLVM's IR.

Classes in this module effectively map to LLVM C++ classes in the llvm::Type
class hierarchy.
"""

from ctypes import POINTER
from ctypes import byref
from ctypes import c_char_p
from ctypes import c_int
from ctypes import c_uint

from . import enumerations
from .common import CachedProperty
from .common import LLVMObject
from .common import c_object_p
from .common import get_library
from .core import Context

__all__ = [
    'lib',
    'TypeKind',
    'Type',
    'IntegerType',
    'FunctionType',
    'StructType',
    'ArrayType',
    'PointerType',
    'VectorType',
    'TypeFactory',
]

lib = get_library()

class TypeKind(object):
    """Represents a TypeKind enumeration."""

    _value_map = {}

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return 'TypeKind.%s' % self.name

    @staticmethod
    def from_value(value):
        """Obtain a TypeKind instance from a numeric value."""
        result = TypeKind._value_map.get(value, None)

        if result is None:
            raise ValueError('Unknown TypeKind: %d' % value)

        return result

    @staticmethod
    def register(name, value):
        """Registers a TypeKind enumeration.

        This is called at module load time. You should not need to call this
        externally.
        """
        if value in TypeKind._value_map:
            raise ValueError('TypeKind value already registered: %d' % value)

        kind = TypeKind(name, value)
        TypeKind._value_map[value] = kind
        setattr(TypeKind, name, kind)

class Type(LLVMObject):
    """Represents a primitive type. """
    def __init__(self, ptr, context, module=None):
        assert isinstance(context, Context)

        LLVMObject.__init__(self, ptr)

        self._set_ref('context', context)

    @CachedProperty
    def kind(self):
        """The TypeKind of this Type."""
        value = lib.LLVMGetTypeKind(self)

        return TypeKind.from_value(value)

    @CachedProperty
    def sized(self):
        """Whether the type is sized."""
        return lib.LLVMTypeIsSized(self)

    @CachedProperty
    def context(self):
        """The Context to which this Type is attached."""
        return self._get_ref('context')

class IntegerType(Type):
    """Represents an integer Type."""

    @CachedProperty
    def width(self):
        """The width of the integer, in bits."""
        return lib.LLVMGetIntTypeWidth(self)

class FunctionType(Type):
    """Represents a function Type."""

    @CachedProperty
    def is_variadic(self):
        """Boolean indicating whether the function is variadic."""
        return lib.LLVMIsFunctionVarArg(self)

    @CachedProperty
    def return_type(self):
        """The Type of the value returned by this function."""
        ptr = lib.LLVMGetReturnType(self)

        return Type(ptr, context=self._get_ref('context'))

    @property
    def parameter_count(self):
        return lib.LLVMCountParamTypes(self)

    def get_parameters(self):
        """The parameters to the function.

        This is a generator for Type instances.
        """

        count = self.parameter_count
        arr = (c_object_p * count)()
        ref = byref(arr[0])
        lib.LLVMGetParamTypes(self, ref)
        for ptr in arr:
            yield Type(ptr, context=self._get_ref('context'))

class StructType(Type):
    """Represents a structure Type."""

    @CachedProperty
    def name(self):
        """The str name of this structure."""
        return lib.LLVMGetStructName(self).value

    def set_elements(self, elements, packed=False):
        """Set the structure contents to a list of Types.

        elements is a list of Type instances that compose the structure.
        packed indicates whether this is a packed structure.
        """
        raise Exception('TODO Implement')

    def get_elements(self):
        """The Types in this structure.

        This is a generator for Type instances.
        """
        count = lib.LLVMCountStructElementTypes(self)
        arr = (c_object_p * count)()
        ref = byref(arr[0])
        lib.LLVMGetStructElementTypes(self, ref)
        for ptr in arr:
            yield Type(ptr, context=self._get_ref('context'))

    @property
    def is_packed(self):
        return lib.LLVMIsPackedStruct(self)

    @CachedProperty
    def is_opaque(self):
        return lib.LLVMIsOpaqueStruct(self)

class ArrayType(Type):
    """Represents an array Type."""

    @CachedProperty
    def element_count(self):
        return lib.LLVMGetArrayLength(self)

    @CachedProperty
    def element_type(self):
        ptr = lib.LLVMArrayType(self, self.element_count)

        return Type(ptr, context=self._get_ref('context'))

class PointerType(Type):
    """Represents a pointer Type."""

    @CachedProperty
    def element_type(self):
        space = lib.LLVMGetPointerAddressSpace(self)
        ptr = lib.LLVMPointerType(self, space)

        return Type(ptr, context=self._get_ref('context'))

class VectorType(Type):
    """Represents a vector Type."""

    @CachedProperty
    def element_count(self):
        return lib.LLVMGetVectorSize(self)

    @CachedProperty
    def element_type(self):
        ptr = lib.LLVMVectorType(self, self.element_count)

        return Type(ptr, context=self._get_ref('context'))

class TypeFactory(LLVMObject):
    """A factory for Type instances.

    This serves as a convenience class to generate Type instances.

    Each TypeFactory is associated with a Context. TypeFactory instances
    typically exist transparently or are hung off other class instances, such
    as Context or Module. You probably don't need to be instantiating these
    outside of the LLVM package.

    This class is really just a collection of related functions. These could
    each be a standalone function and could be exported as part of the module.
    However, the class keeps things organized. And, the existence of the class
    is usually abstracted anyway, so it isn't such a big deal.
    """
    def __init__(self, ctx):
        """Create a new TypeFactory from a Context."""

        assert isinstance(ctx, Context)

        LLVMObject.__init__(self)

        self._set_ref('context', ctx)

    def _make_type(self, func, arg=None):
        context = self._get_ref('context')

        ptr = None
        if arg is not None:
            ptr = func(context, arg)
        else:
            ptr = func(context)

        return Type(ptr, context=context)

    def int1(self):
        return self._make_type(lib.LLVMInt1TypeInContext)

    def int8(self):
        return self._make_type(lib.LLVMInt8TypeInContext)

    def int16(self):
        return self._make_type(lib.LLVMInt16TypeInContext)

    def int32(self):
        return self._make_type(lib.LLMVInt32TypeInContext)

    def int64(self):
        return self._make_type(lib.LLVMInt64TypeInContext)

    def int(self, bits):
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

    def struct(self, types, packed):
        context = self._get_ref('context')

        arr = (Type * len(types))(types)
        ref = byref(arr[0])

        ptr = lib.LLVMStructTypeInContext(context, ref, c_uint(len(types)),
                                          bool(packed))

        return Type(ptr, context=context)

    def named_struct(self, name):
        return self._make_type(lib.LLVMStructCreateNamed, name)

    def void(self):
        return self._make_type(lib.LLVMVoidTypeInContext)

    def label(self):
        return self._make_type(lib.LLVMLabelTypeInContext)

    def x86mmx(self):
        return self._make_type(lib.LLVMX86MMXTypeInContext)

    def function(self, return_type, param_types, is_vararg=False):
        arr = (Type * len(param_types))(param_types)
        ref = byref(arr[0])

        ptr = lib.LLVMFunctionType(return_type, ref, c_uint(len(param_types)),
                                   c_int(is_vararg))

        # Not sure what the C API does about a context. It probably gets them
        # from the passed Type instances. Whatever happens, we need to
        # associate.
        return Type(ptr, context=self._get_ref('context'))

def register_library(library):
    library.LLVMArrayType.argtypes = [Type, c_uint]
    library.LLVMArrayType.restype = c_object_p

    library.LLVMCountParamTypes.argtypes = [Type]
    library.LLVMCountParamTypes.restype = c_uint

    library.LLVMCountStructElementTypes.argtypes = [Type]
    library.LLVMCountStructElementTypes.restype = c_uint

    library.LLVMDoubleTypeInContext.argtypes = [Context]
    library.LLVMDoubleTypeInContext.result = c_object_p

    library.LLVMFloatTypeInContext.argtypes = [Context]
    library.LLVMFloatTypeInContext.result = c_object_p

    library.LLVMFP128TypeInContext.argtypes = [Context]
    library.LLVMFP128TypeInContext.result = c_object_p

    library.LLVMFunctionType.argtypes = [Type, POINTER(c_object_p), c_uint,
            c_int]
    library.LLVMFunctionType.restype = c_object_p

    library.LLVMGetArrayLength.argtypes = [Type]
    library.LLVMGetArrayLength.restype = c_uint

    library.LLVMArrayType.argtypes = [Type, c_uint]
    library.LLVMArrayType.restype = c_object_p

    library.LLVMGetElementType.argtypes = [Type]
    library.LLVMGetElementType.restype = c_object_p

    library.LLVMGetIntTypeWidth.argtypes = [Type]
    library.LLVMGetIntTypeWidth.restype = c_uint

    library.LLVMGetParamTypes.argtypes = [Type, POINTER(c_object_p)]

    library.LLVMGetPointerAddressSpace.argtypes = [Type]
    library.LLVMGetPointerAddressSpace.restype = c_uint

    library.LLVMGetReturnType.argtypes = [Type]
    library.LLVMGetReturnType.restype = c_object_p

    library.LLVMGetStructElementTypes.argtypes = [Type, POINTER(c_object_p)]

    library.LLVMGetStructName.argtypes = [Type]
    library.LLVMGetStructName.restype = c_char_p

    library.LLVMGetTypeKind.argtypes = [Type]
    library.LLVMGetTypeKind.restype = c_int

    library.LLVMGetVectorSize.argtypes = [Type]
    library.LLVMGetVectorSize.restype = c_uint

    library.LLVMHalfTypeInContext.argtypes = [Context]
    library.LLVMHalfTypeInContext.result = c_object_p

    library.LLVMInt1TypeInContext.argtypes = [Context]
    library.LLVMInt1TypeInContext.result = c_object_p

    library.LLVMInt8TypeInContext.argtypes = [Context]
    library.LLVMInt8TypeInContext.result = c_object_p

    library.LLVMInt16TypeInContext.argtypes = [Context]
    library.LLVMInt16TypeInContext.result = c_object_p

    library.LLVMInt32TypeInContext.argtypes = [Context]
    library.LLVMInt32TypeInContext.result = c_object_p

    library.LLVMInt64TypeInContext.argtypes = [Context]
    library.LLVMInt64TypeInContext.result = c_object_p

    library.LLVMIntTypeInContext.argtypes = [Context, c_uint]
    library.LLVMIntTypeInContext.result = c_object_p

    library.LLVMIsFunctionVarArg.argtypes = [Type]
    library.LLVMIsFunctionVarArg.restype = bool

    library.LLVMIsOpaqueStruct.argtypes = [Type]
    library.LLVMIsOpaqueStruct.restype = bool

    library.LLVMIsPackedStruct.argtypes = [Type]
    library.LLVMIsPackedStruct.restype = bool

    library.LLVMLabelTypeInContext.argtypes = [Context]
    library.LLVMLabelTypeInContext.result = c_object_p

    library.LLVMPPCFP128TypeInContext.argtypes = [Context]
    library.LLVMPPCFP128TypeInContext.result = c_object_p

    library.LLVMPointerType.argtypes = [Type, c_uint]
    library.LLVMPointerType.restype = c_object_p

    library.LLVMStructCreateNamed.argtypes = [Context, c_char_p]
    library.LLVMStructCreateNamed.restype = c_object_p

    library.LLVMStructSetBody.argtypes = [Type, POINTER(c_object_p), c_uint,
            c_int]

    library.LLVMStructTypeInContext.argtypes = [Context, POINTER(c_object_p),
            c_uint, c_int]
    library.LLVMStructTypeInContext.result = c_object_p

    library.LLVMTypeIsSized.argtypes = [Type]
    library.LLVMTypeIsSized.restype = bool

    library.LLVMVectorType.argtypes = [Type, c_uint]
    library.LLVMVectorType.restype = c_object_p

    library.LLVMVoidTypeInContext.argtypes = [Context]
    library.LLVMVoidTypeInContext.result = c_object_p

    library.LLVMX86FP80TypeInContext.argtypes = [Context]
    library.LLVMX86FP80TypeInContext.result = c_object_p

    library.LLVMX86MMXTypeInContext.argtypes = [Context]
    library.LLVMX86MMXTypeInContext.result = c_object_p

register_library(lib)

for name, value in enumerations.TypeKinds:
    TypeKind.register(name, value)
