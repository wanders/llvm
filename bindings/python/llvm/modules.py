#===- modules.py - Python LLVM Bindings ----------------------*- python -*--===#
#
#                     The LLVM Compiler Infrastructure
#
# This file is distributed under the University of Illinois Open Source
# License. See LICENSE.TXT for details.
#
#===------------------------------------------------------------------------===#

from ctypes import POINTER
from ctypes import byref
from ctypes import c_char_p
from ctypes import c_int
from ctypes import c_uint

from .common import LLVMObject
from .common import c_object_p
from .common import get_library
from .core import Context
from .core import MemoryBuffer
from .types import FunctionType
from .types import Type
from .values import Value

__all__ = [
    'lib',
    'Module',
]

lib = get_library()

class Module(LLVMObject):
    """Represents an LLVM module.

    Modules are an interface to the LLVM Intermediate Representation. They
    contain global variables, functions, library/module dependencies, a symbol
    table, and target characteristics.

    See also llvm::Module::Module.

    TODO support NamedMetadataOperands
    """

    def __init__(self, name=None, ptr=None, bitcode_filename=None,
                 bitcode_buffer=None, bitcode_lazy_load=False, context=None):
        """Construct a new module instance.

        Modules can be created one of several ways. The specific way depends
        on the arguments to this function. In all cases, a Context instance
        to which the module will be attached may be defined via the context
        argument. If this argument is None (the default), the global context
        will be used.

        If name is a str, an empty module with the specified str name will be
        created.

        If bitcode_filename is a str, the Module will be constructed from
        bitcode in the filename specified.

        If bitcode_buffer is a llvm.core.MemoryBuffer, the Module will be
        read from that MemoryBuffer instance.

        If ptr is a c_object_p, a Module will be created from this pointer.
        Please note that consumers outside of the llvm package shouldn't
        be dealing with raw pointers so they shouldn't be passing this
        argument.

        If loading the Module from bitcode, the default behavior is to parse
        the entire bitcode source. To change to lazy loading, set
        bitcode_lazy_load to True.

        If multiple input sources are defined, behavior is undefined: only
        define one source for your Module!
        """
        if context is None:
            context = Context(use_global=True)

        if ptr:
            LLVMObject.__init__(self, ptr, disposer=lib.LLVMDisposeModule)
            self._set_ref('context', context)
            return

        if name:
            ptr = lib.LLVMModuleCreateWithNameInContext(name, context)
            LLVMObject.__init__(self, ptr, disposer=lib.LLVMDisposeModule)
            self._set_ref('context', context)
            return

        if bitcode_filename:
            bitcode_buffer = MemoryBuffer(filename=bitcode_filename)

        if bitcode_buffer:
            msg = c_char_p()
            ptr = c_object_p()

            result = None

            if bitcode_lazy_load:
                result = lib.LLVMGetBitcodeModuleInContext(context,
                        bitcode_buffer, byref(ptr), byref(msg))
            else:
                result = lib.LLVMParseBitcodeInContext(context, bitcode_buffer,
                        byref(ptr), byref(msg))

            if result:
                raise Exception('Could not parse bitcode into Module: %s' %
                        msg.value)

            LLVMObject.__init__(self, ptr, disposer=lib.LLVMDisposeModule)

            if bitcode_lazy_load:
                self.take_ownership(bitcode_buffer)

            self._set_ref('context', context)
            return

        raise Exception('Insufficient arguments to create Module.')

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

    def add_global(self, ty, name, address_space=None):
        """Add a global Type to the Module with the specified name.

        Returns a Value.
        """
        assert isinstance(ty, Type)
        assert isinstance(name, str)

        ptr = None
        if address_space:
            ptr = lib.LLVMAddGlobalInAddressSpace(self, ty, name, address_space)
        else:
            ptr = lib.LLVMAddGlobal(self, ty, name)

        return Value(ptr, module=self)

    def get_global(self, name):
        """Get a global Value by name."""

        ptr = lib.LLVMGetNamedGlobal(self, name)
        return Value(ptr, module=self)

    def get_globals(self):
        """Get all globals in this module.

        This is a generator of Value instances.
        """

        ptr = lib.LLVMGetFirstGlobal(self)
        g = None
        while ptr:
            g = Value(ptr, module=self)
            yield g

            ptr = lib.LLVMGetNextGlobal(g)

    def delete_global(self, value):
        """Delete a global Value from this Module."""
        lib.LLVMDeleteGlobal(value)

    def add_alias(self, ty, alias, name):
        raise Exception('TODO implement.')

    def add_function(self, func, name):
        """Add a function to this Module under a specified name."""

        assert isinstance(func, FunctionType)
        assert isinstance(name, str)

        ptr = lib.LLVMAddFunction(self, name, func)
        return Value(ptr, module=self)

    def get_function(self, name):
        """Get a function by its str name."""

        assert isinstance(name, str)

        ptr = lib.LLVMGetNamedFunction(self, name)
        return Value(ptr, module=self)

    def get_functions(self):
        """Obtain all functions in this Module.

        This is a generator for Value instances.
        """
        ptr = lib.LLVMGetFirstFunction(self)
        f = None
        while ptr:
            f = Value(ptr, module=self)
            yield f

            ptr = lib.LLVMGetNextFunction(f)

    def delete_function(self, value):
        """Delete a function Value from this Module."""
        assert isinstance(value, Value)

        lib.LLVMDeletionFunction(value)

    def write(self, filename=None, fh=None):
        """Write the module bit code.
        This can be used to write the contents of the module to a file or to an
        open file handle. If both arguments are defined, behavior is undefined.
        """

        if filename is None and fh is None:
            raise Exception('An argument must be defined to control writing.')

        result = None

        if fh:
            if not isinstance(fh, file):
                raise Exception('fh argument must be a file object.')

            result = lib.LLVMWriteBitcodeToFH(self, fh.fileno())

        if filename:
            result = lib.LLVMWriteBitcodeToFile(self, filename)

        if result:
            raise Exception('Error when writing bit code for module.')

def register_library(library):
    library.LLVMAddAlias.argtypes = [Module, Type, Value, c_char_p]
    library.LLVMAddAlias.restype = c_object_p

    library.LLVMAddFunction.argtypes = [Module, c_char_p, FunctionType]
    library.LLVMAddFunction.restype = c_object_p

    library.LLVMAddGlobalInAddressSpace.argtypes = [Module, Type, c_char_p,
            c_uint]
    library.LLVMAddGlobalInAddressSpace.restype = c_object_p

    library.LLVMAddGlobal.argtypes = [Module, Type, c_char_p]
    library.LLVMAddGlobal.restype = c_object_p

    library.LLVMDisposeModule.argtypes = [Module]

    library.LLVMDumpModule.argtypes = [Module]

    library.LLVMGetBitcodeModuleInContext.argtypes = [Context, MemoryBuffer,
            POINTER(c_object_p), POINTER(c_char_p)]
    library.LLVMGetBitcodeModuleInContext.restype = bool

    library.LLVMGetDataLayout.argtypes = [Module]
    library.LLVMGetDataLayout.restype = c_char_p

    library.LLVMGetFirstFunction.argtypes = [Module]
    library.LLVMGetFirstFunction.restype = c_object_p

    library.LLVMGetFirstGlobal.argtypes = [Module]
    library.LLVMGetFirstGlobal.restype = c_object_p

    library.LLVMGetNamedFunction.argtypes = [Module, c_char_p]
    library.LLVMGetNamedFunction.restype = c_object_p

    library.LLVMGetNamedGlobal.argtypes = [Module, c_char_p]
    library.LLVMGetNamedGlobal.restype = c_object_p

    library.LLVMGetTarget.argtypes = [Module]
    library.LLVMGetTarget.restype = c_char_p

    library.LLVMGetTypeByName.argtypes = [Module, c_char_p]
    library.LLVMGetTypeByName.restype = c_object_p

    library.LLVMModuleCreateWithNameInContext.argtypes = [c_char_p, Context]
    library.LLVMModuleCreateWithNameInContext.restype = c_object_p

    library.LLVMParseBitcodeInContext.argtypes = [Context, MemoryBuffer,
            POINTER(c_object_p), POINTER(c_char_p)]
    library.LLVMParseBitcodeInContext.restype = bool

    library.LLVMSetModuleInlineAsm.argtypes = [Module, c_char_p]

    library.LLVMSetDataLayout.argtypes = [Module, c_char_p]

    library.LLVMSetTarget.argtypes = [Module, c_char_p]

    library.LLVMWriteBitcodeToFD.argtypes = [Module, c_int, c_int, c_int]
    library.LLVMWriteBitcodeToFD.restype = c_int

    library.LLVMWriteBitcodeToFile.argtypes = [Module, c_char_p]
    library.LLVMWriteBitcodeToFile.restype = c_int

register_library(lib)
