#===- core.py - Python LLVM Bindings -------------------------*- python -*--===#
#
#                     The LLVM Compiler Infrastructure
#
# This file is distributed under the University of Illinois Open Source
# License. See LICENSE.TXT for details.
#
#===------------------------------------------------------------------------===#

from .common import CachedProperty
from .common import LLVMObject
from .common import c_object_p
from .common import get_library

from . import enumerations

from ctypes import POINTER
from ctypes import byref
from ctypes import c_bool
from ctypes import c_char_p
from ctypes import c_int
from ctypes import c_uint

__all__ = [
    "lib",
    "MemoryBuffer",
]

lib = get_library()

class OpCode(object):
    """Represents an individual OpCode enumeration."""

    _value_map = {}

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return 'OpCode.%s' % self.name

    @staticmethod
    def from_value(value):
        """Obtain an OpCode instance from a numeric value."""
        result = OpCode._value_map.get(value, None)

        if result is None:
            raise ValueError('Unknown OpCode: %d' % value)

        return result

    @staticmethod
    def register(name, value):
        """Registers a new OpCode enumeration.

        This is called by this module for each enumeration defined in
        enumerations. You should not need to call this outside this module.
        """
        if value in OpCode._value_map:
            raise ValueError('OpCode value already registered: %d' % value)

        opcode = OpCode(name, value)
        OpCode._value_map[value] = opcode
        setattr(OpCode, name, opcode)

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

class Attribute(object):
    def from_param(self):
        raise Exception('TODO implement.')

class Context(LLVMObject):
    """LLVM state manager.

    A Context is used by LLVM to hold state. The existence of these objects
    will most likely be transparent to most consumers of the Python bindings.
    However, they are exposed for advanced users to use, if needed.
    """

    def __init__(self, use_global=False):
        """Create or obtain a Context.

        By default, a new context is created. If use_global is True, the global
        context will be returned.
        """
        self._is_global = use_global

        ptr = None

        if use_global:
            ptr = lib.LLVMGetGlobalContext()
        else:
            ptr = lib.LLVMContextCreate()

        LLVMObject.__init__(self, ptr, disposer=lib.LLVMContextDispose)

        # Don't destroy the global context in __del__. Instead, let it persist
        # indefinitely.
        if use_global:
            self._self_owned = False

class MemoryBuffer(LLVMObject):
    """Represents an opaque memory buffer."""

    def __init__(self, filename=None):
        """Create a new memory buffer.

        Currently, we support creating from the contents of a file at the
        specified filename.
        """
        if filename is None:
            raise Exception("filename argument must be defined")

        memory = c_object_p()
        out = c_char_p(None)

        result = lib.LLVMCreateMemoryBufferWithContentsOfFile(filename,
                byref(memory), byref(out))

        if result:
            raise Exception("Could not create memory buffer: %s" % out.value)

        LLVMObject.__init__(self, memory, disposer=lib.LLVMDisposeMemoryBuffer)

class TypeFactory(LLVMObject):
    """A factory for Type instances.

    This serves as a convenience class to generate Type instances.

    Each TypeFactory is associated with a Context. Typically you don't create
    a TypeFactory directly. Instead, it is usually hung off another type, like
    a Context or Module.
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
                                          c_bool(packed))

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
        ptr = lib.LLVMGetArrayType(self, self.element_count)

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

class GlobalValue(Value):
    """Represents a global Value."""

    @CachedProperty
    def parent(self):
        """The parent Module of this GlobalValue."""
        return self._get_ref('module')

    @CachedProperty
    def is_declaration(self):
        """Boolean indicating whether this is a declaration."""
        return lib.LLVMIsDeclaration(self)

    @property
    def linkage(self):
        """The LinkageType of this value."""
        raise Exception('TODO implement.')

    @linkage.setter
    def linkage(self, value):
        raise Exception('TODO implement.')

    @property
    def section(self):
        raise Exception('TODO implement.')

    @section.setter
    def section(self, value):
        raise Exception('TODO implement.')

    @property
    def visibility(self):
        raise Exception('TODO implement.')

    @visibility.setter
    def visibility(self, value):
        raise Exception('TODO implement.')

    @property
    def alignment(self):
        raise Exception('TODO implement.')

    @alignment.setter
    def alignment(self, value):
        raise Exception('TODO implement.')

    @property
    def initializer(self):
        raise Exception('TODO implement.')

    @initializer.setter
    def initializer(self, value):
        raise Exception('TODO implement.')

    @property
    def is_thread_local(self):
        raise Exception('TODO implement.')

    @is_thread_local.setter
    def is_thread_local(self, value):
        raise Exception('TODO implement.')

    @property
    def is_global_constant(self):
        raise Exception('TODO implement.')

    @is_global_constant.setter
    def is_global_constant(self, value):
        raise Exception('TODO implement.')

    def delete(self):
        """Delete this global value from its containing module."""
        self._get_ref('module').delete_global(self)

class FunctionValue(Value):
    @property
    def id(self):
        raise Exception('TODO implement.')

    def _get_calling_convention(self):
        raise Exception('TODO implement.')

    def _set_calling_convention(self, value):
        raise Exception('TODO implement.')

    calling_convention = property(_get_calling_convention,
            _set_calling_convention)

    def _get_gc(self):
        raise Exception('TODO implement.')

    def _set_gc(self, value):
        raise Exception('TODO implement.')

    gc = property(_get_gc, _set_gc)

    def delete(self):
        """Delete this function from its containing Module."""
        raise Exception('TODO implement.')

    @property
    def attribute(self):
        raise Exception('TODO implement.')

    def add_attribute(self, attribute):
        raise Exception('TODO implement.')

    def remove_attribute(self, attribute):
        raise Exception('TODO implement.')

    def get_parameters(self):
        ptr = lib.LLVMGetFirstParam(self)
        value = None
        while ptr:
            value = ArgumentValue(ptr, module=self._get_ref('module'))

            yield value

            ptr = lib.LLVMGetNextParam(value)

class ArgumentValue(Value):
    def add_attribute(self, attribute):
        raise Exception('TODO implement.')

    def remove_attribute(self, attribute):
        raise Exception('TODO implement.')

    def get_attribute(self, value):
        raise Exception('TODO implement.')

def register_library(library):
    """Register C APIs with ctypes library instance.

    This list is pretty long. We define APIs in alphabetical order for
    sanity.
    """
    library.LLVMAddAttribute.argtypes = [ArgumentValue, Attribute]

    library.LLVMAddFunctionAttr.argtypes = [FunctionValue, Attribute]

    library.LLVMArrayType.argtypes = [Type, c_uint]
    library.LLVMArrayType.restype = c_object_p

    library.LLVMContextCreate.restype = c_object_p

    library.LLVMContextDispose.argtypes = [Context]

    library.LLVMCountParamTypes.argtypes = [Type]
    library.LLVMCountParamTypes.restype = c_uint

    library.LLVMCountStructElementTypes.argtypes = [Type]
    library.LLVMCountStructElementTypes.restype = c_uint

    library.LLVMCreateMemoryBufferWithContentsOfFile.argtypes = [c_char_p,
            POINTER(c_object_p), POINTER(c_char_p)]
    library.LLVMCreateMemoryBufferWithContentsOfFile.restype = bool

    library.LLVMDeleteFunction.argtypes = [Value]

    library.LLVMDeleteGlobal.argtypes = [Value]

    library.LLVMDisposeMemoryBuffer.argtypes = [MemoryBuffer]

    library.LLVMDoubleTypeInContext.argtypes = [Context]
    library.LLVMDoubleTypeInContext.result = c_object_p

    library.LLVMFloatTypeInContext.argtypes = [Context]
    library.LLVMFloatTypeInContext.result = c_object_p

    library.LLVMFP128TypeInContext.argtypes = [Context]
    library.LLVMFP128TypeInContext.result = c_object_p

    library.LLVMFunctionType.argtypes = [Type, POINTER(c_object_p), c_uint,
            c_int]
    library.LLVMFunctionType.restype = c_object_p

    library.LLVMGetAlignment.argtypes = [GlobalValue]
    library.LLVMGetAlignment.restype = c_uint

    library.LLVMGetArrayLength.argtypes = [Type]
    library.LLVMGetArrayLength.restype = c_uint

    library.LLVMGetAttribute.argtypes = [ArgumentValue]
    library.LLVMGetAttribute.restype = c_int

    library.LLVMGetElementType.argtypes = [Type]
    library.LLVMGetElementType.restype = c_object_p

    library.LLVMGetFirstParam.argtypes = [FunctionValue]
    library.LLVMGetFirstParam.restype = c_object_p

    library.LLVMGetFunctionAttr.argtypes = [FunctionValue]
    library.LLVMGetFunctionAttr.restype = c_int

    library.LLVMGetFunctionCallConv.argtypes = [FunctionValue]
    library.LLVMGetFunctionCallConv.restype = c_uint

    library.LLVMGetGC.argtypes = [FunctionValue]
    library.LLVMGetGC.restype = c_char_p

    library.LLVMGetGlobalContext.restype = c_object_p

    library.LLVMGetInitializer.argtypes = [GlobalValue]
    library.LLVMGetInitializer.restype = c_object_p

    library.LLVMGetIntTypeWidth.argtypes = [Type]
    library.LLVMGetIntTypeWidth.restype = c_uint

    library.LLVMGetIntrinsicID.argtypes = [FunctionValue]
    library.LLVMGetIntrinsicID.restype = c_uint

    library.LLVMGetLinkage.argtypes = [GlobalValue]
    library.LLVMGetLinkage.restype = c_int

    library.LLVMGetNextFunction.argtypes = [Value]
    library.LLVMGetNextFunction.restype = c_object_p

    library.LLVMGetNextGlobal.argtypes = [Value]
    library.LLVMGetNextGlobal.restype = c_object_p

    library.LLVMGetNextParam.argtypes = [Value]
    library.LLVMGetNextParam.restype = c_object_p

    library.LLVMGetParamTypes.argtypes = [Type, POINTER(c_object_p)]

    library.LLVMGetPointerAddressSpace.argtypes = [Type]
    library.LLVMGetPointerAddressSpace.restype = c_uint

    library.LLVMGetReturnType.argtypes = [Type]
    library.LLVMGetReturnType.restype = c_object_p

    library.LLVMGetSection.argtypes = [GlobalValue]
    library.LLVMGetSection.restype = c_char_p

    library.LLVMGetStructElementTypes.argtypes = [Type, POINTER(c_object_p)]

    library.LLVMGetStructName.argtypes = [Type]
    library.LLVMGetStructName.restype = c_char_p

    library.LLVMGetTypeKind.argtypes = [Type]
    library.LLVMGetTypeKind.restype = c_int

    library.LLVMGetVectorSize.argtypes = [Type]
    library.LLVMGetVectorSize.restype = c_uint

    library.LLVMGetVisibility.argtypes = [GlobalValue]
    library.LLVMGetVisibility.restype = c_int

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

    library.LLVMIsDeclaration.argtypes = [GlobalValue]
    library.LLVMIsDeclaration.restype = c_bool

    library.LLVMIsFunctionVarArg.argtypes = [Type]
    library.LLVMIsFunctionVarArg.restype = c_bool

    library.LLVMIsGlobalConstant.argtypes = [GlobalValue]
    library.LLVMIsGlobalConstant.restype = c_bool

    library.LLVMIsOpaqueStruct.argtypes = [Type]
    library.LLVMIsOpaqueStruct.restype = c_bool

    library.LLVMIsPackedStruct.argtypes = [Type]
    library.LLVMIsPackedStruct.restype = c_bool

    library.LLVMIsThreadLocal.argtypes = [GlobalValue]
    library.LLVMIsThreadLocal.restype = c_bool

    library.LLVMLabelTypeInContext.argtypes = [Context]
    library.LLVMLabelTypeInContext.result = c_object_p

    library.LLVMPPCFP128TypeInContext.argtypes = [Context]
    library.LLVMPPCFP128TypeInContext.result = c_object_p

    library.LLVMPointerType.argtypes = [Type, c_uint]
    library.LLVMPointerType.restype = c_object_p

    library.LLVMRemoveAttribute.argtypes = [ArgumentValue, Attribute]

    library.LLVMRemoveFunctionAttr.argtypes = [FunctionValue, Attribute]

    library.LLVMSetAlignment.argtypes = [GlobalValue, c_uint]

    library.LLVMSetFunctionCallConv.argtypes = [FunctionValue, c_uint]

    library.LLVMSetGC.argtypes = [FunctionValue, c_char_p]

    library.LLVMSetGlobalConstant.argtypes = [GlobalValue]

    library.LLVMSetInitializer.argtypes = [GlobalValue, ConstantValue]

    library.LLVMSetLinkage.argtypes = [GlobalValue, c_int]

    library.LLVMSetSection.argtypes = [GlobalValue, c_char_p]

    library.LLVMSetThreadLocal.argtypes = [GlobalValue]

    library.LLVMSetVisibility.argtypes = [GlobalValue, c_int]

    library.LLVMStructCreateNamed.argtypes = [Context, c_char_p]
    library.LLVMStructCreateNamed.restype = c_object_p

    library.LLVMStructSetBody.argtypes = [Type, POINTER(c_object_p), c_uint,
            c_int]

    library.LLVMStructTypeInContext.argtypes = [Context, POINTER(c_object_p),
            c_uint, c_int]
    library.LLVMStructTypeInContext.result = c_object_p

    library.LLVMTypeIsSized.argtypes = [Type]
    library.LLVMTypeIsSized.restype = c_bool

    library.LLVMVectorType.argtypes = [Type, c_uint]
    library.LLVMVectorType.restype = c_object_p

    library.LLVMVoidTypeInContext.argtypes = [Context]
    library.LLVMVoidTypeInContext.result = c_object_p

    library.LLVMX86FP80TypeInContext.argtypes = [Context]
    library.LLVMX86FP80TypeInContext.result = c_object_p

    library.LLVMX86MMXTypeInContext.argtypes = [Context]
    library.LLVMX86MMXTypeInContext.result = c_object_p

def register_enumerations():
    for name, value in enumerations.OpCodes:
        OpCode.register(name, value)

    for name, value in enumerations.TypeKinds:
        TypeKind.register(name, value)

register_library(lib)
register_enumerations()
