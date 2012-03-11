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

def TypeKind(object):
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

class Module(LLVMObject):
    """Represents an LLVM module.

    Modules are an interface to the LLVM Intermediate Representation. They
    contain global variables, functions, library/module dependencies, a symbol
    table, and target characteristics.

    See also llvm::Module::Module.

    TODO support NamedMetadataOperands
    """

    def __init__(self, name=None, context=None):
        """Construct a new module instance.

        It is possible to create empty modules or to build modules from
        existing sources. In all cases, you have the option of supplying an
        llvm.core.Context to which to associate the module. If no context is
        provided, the global context will be used.

        If name is provided, an empty module with the specified str id will be
        created.
        """

        if context is None:
            context = Context(use_global=True)

        if name is None:
            raise Exception('You must supply a name to create a module.')

        ptr = None

        if name:
            ptr = lib.LLVMModuleCreateWithNameInContext(name, context,
                    disposer=lib.LLVMDisposeModule)

        LLVMObject.__init__(self, ptr)
        self._set_ref('context', context)

    @property
    def context(self):
        """The Context to which this module is associated."""
        return self._get_ref('context')

    @property
    def layout(self):
        """The data layout string for this module's platform."""
        return lib.LLVMGetDataLayout(self)

    @layout.setter
    def layout(self, value):
        lib.LLVMSetDataLayout(self, value)

    @property
    def target(self):
        """The target triple for this module."""
        return lib.LLVMGetTarget(self)

    @target.setter
    def target(self, value):
        lib.LLVMSetTarget(self, value)

    @property
    def inline_assembly(self):
        # For whatever reason the C API doesn't expose this. We need to define
        # the property so the setter works.
        raise Exception('Not implemented.')

    @inline_assembly.setter
    def inline_assembly(self, value):
        """Set the module-scope inline assembly blocks."""
        lib.LLVMSetModuleInlineAsm(self, value)

    def dump(self):
        """Dump a representation of the module to stderr (for debugger)."""
        lib.LLVMDumpModule(self)

    def get_type(self, name):
        """Return the Type with the specified name.

        Returns a Type on success or None if no Type with that name exists.
        """
        assert isinstance(name, str)

        ptr = lib.LLVMGetTypeByName(self, name)
        if not ptr:
            return None

        return Type(ptr, module=self, context=self._get_ref('context'))

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
    def int_width(self):
        """For integer types, the width of the integer, in bits."""
        return lib.LLVMGetIntTypeWidth(self)

    @CachedProperty
    def context(self):
        """The Context to which this Type is attached."""
        return self._get_ref('context')

    @CachedProperty
    def is_vararg(self):
        return lib.LLVMIsFunctionVarArg(self)

    @CachedProperty
    def return_type(self):
        ptr = lib.LLVMGetReturnType(self)

        return Type(ptr, context=self._get_ref('context'))

    def get_parameters(self):
        """The parameters to the function.

        This is a generator for Type instances.
        """

        count = lib.LLVMCountParamTypes(self)
        arr = (c_object_p * count)()
        ref = byref(arr[0])
        lib.LLVMGetParamTypes(self, ref)
        for ptr in arr:
            yield Type(ptr, context=self._get_ref('context'))

    @CachedProperty
    def struct_name(self):
        return lib.LLVMGetStructName(self).value

    def set_struct_body(self, elements, packed=False):
        raise Exception('TODO Implement')

    def get_struct_elements(self):
        """The Types in a struct type.

        This is a generator for Type instances.
        """
        count = lib.LLVMCountStructElementTypes(self)
        arr = (c_object_p * count)()
        ref = byref(arr[0])
        lib.LLVMGetStructElementTypes(self, ref)
        for ptr in arr:
            yield Type(ptr, context=self._get_ref('context'))

    @CachedProperty
    def is_packed_struct(self):
        return lib.LLVMIsPackedStruct(self)

    @CachedProperty
    def is_opaque_struct(self):
        return lib.LLVMIsOpaqueStruct(self)

    @CachedProperty
    def array_type(self):
        count = lib.LLVMGetArrayLength(self)
        ptr = lib.LLVMGetArrayType(self, count)

        return Type(ptr, context=self._get_ref('context'))

    @CachedProperty
    def pointer_type(self):
        space = lib.LLVMGetPointerAddressSpace(self)
        ptr = lib.LLVMPointerType(self, space)

        return Type(ptr, context=self._get_ref('context'))

    @CachedProperty
    def vector_type(self):
        size = lib.LLVMGetVectorSize(self)
        ptr = lib.LLVMVectorType(self, size)

        return Type(ptr, context=self._get_ref('context'))


class Value(LLVMObject):
    def __init__(self, ptr, context):
        LLVMObject.__init__(self, ptr)

        self._set_ref('context', context)

    @CachedProperty
    def type(self):
        ptr = lib.LLVMTypeOf(self)

        return Type(ptr, context=self._get_ref('context'))

    @property
    def name(self):
        return lib.LLVMGetValueName(self).value

    @name.setter
    def name(self, value):
        lib.LLVMSetValueName(self, value)

def register_library(library):
    """Register C APIs with ctypes library instance.

    This list is pretty long. We define APIs in alphabetical order for
    sanity.
    """

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

    library.LLVMDisposeMemoryBuffer.argtypes = [MemoryBuffer]

    library.LLVMDisposeModule.argtypes = [Module]

    library.LLVMDoubleTypeInContext.argtypes = [Context]
    library.LLVMDoubleTypeInContext.result = c_object_p

    library.LLVMDumpModule.argtypes = [Module]

    library.LLVMFloatTypeInContext.argtypes = [Context]
    library.LLVMFloatTypeInContext.result = c_object_p

    library.LLVMFP128TypeInContext.argtypes = [Context]
    library.LLVMFP128TypeInContext.result = c_object_p

    library.LLVMFunctionType.argtypes = [Type, POINTER(c_object_p), c_uint,
            c_int]
    library.LLVMFunctionType.restype = c_object_p

    library.LLVMGetArrayLength.argtypes = [Type]
    library.LLVMGetArrayLength.restype = c_uint

    library.LLVMGetDataLayout.argtypes = [Module]
    library.LLVMGetDataLayout.restype = c_char_p

    library.LLVMGetElementType.argtypes = [Type]
    library.LLVMGetElementType.restype = c_object_p

    library.LLVMGetGlobalContext.restype = c_object_p

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

    library.LLVMGetTarget.argtypes = [Module]
    library.LLVMGetTarget.restype = c_char_p

    library.LLVMGetTypeByName.argtypes = [Module, c_char_p]
    library.LLVMGetTypeByName.restype = c_object_p

    library.LLVMGetTypeKind.argtypes = [Type]
    library.LLVMGetTypeKind.restype = c_int

    library.LLVMGetValueName.argtypes = [Value]
    library.LLVMGetValueName.restype = c_char_p

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
    library.LLVMIsFunctionVarArg.restype = c_bool

    library.LLVMIsOpaqueStruct.argtypes = [Type]
    library.LLVMIsOpaqueStruct.restype = c_bool

    library.LLVMIsPackedStruct.argtypes = [Type]
    library.LLVMIsPackedStruct.restype = c_bool

    library.LLVMLabelTypeInContext.argtypes = [Context]
    library.LLVMLabelTypeInContext.result = c_object_p

    library.LLVMModuleCreateWithNameInContext.argtypes = [c_char_p, Context]
    library.LLVMModuleCreateWithNameInContext.restype = c_object_p

    library.LLVMPPCFP128TypeInContext.argtypes = [Context]
    library.LLVMPPCFP128TypeInContext.result = c_object_p

    library.LLVMPointerType.argtypes = [Type, c_uint]
    library.LLVMPointerType.restype = c_object_p

    library.LLVMSetDataLayout.argtypes = [Module, c_char_p]

    library.LLVMSetModuleInlineAsm.argtypes = [Module, c_char_p]

    library.LLVMSetTarget.argtypes = [Module, c_char_p]

    library.LLVMSetValueName.argtypes = [Value, c_char_p]

    library.LLVMStructCreateNamed.argtypes = [Context, c_char_p]
    library.LLVMStructCreateNamed.restype = c_object_p

    library.LLVMStructSetBody.argtypes = [Type, POINTER(c_object_p), c_uint,
            c_int]

    library.LLVMStructTypeInContext.argtypes = [Context, POINTER(c_object_p),
            c_uint, c_int]
    library.LLVMStructTypeInContext.result = c_object_p

    library.LLVMTypeOf.argtypes = [Value]
    library.LLVMTypeOf.restype = c_object_p

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

register_library(lib)
register_enumerations()
