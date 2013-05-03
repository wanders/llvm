#===- executionengine.py - Python Object Bindings ------------*- python -*--===#
#
#                     The LLVM Compiler Infrastructure
#
# This file is distributed under the University of Illinois Open Source
# License. See LICENSE.TXT for details.
#
#===------------------------------------------------------------------------===#


from .common import c_object_p
from .common import LLVMObject
from .common import get_library
from .common import create_c_object_p_array

from .core import types

import ctypes

lib = get_library()

_initialized = False
def _ensure_native_target_initialized():
    global _initialized
    if not _initialized:
        lib.LLVMInitializeNativeTarget()
        _initialized = True



@lib.c_name("LLVMGenericValueRef")
class GenericValue(LLVMObject):
    @staticmethod
    def int(typ, val, signed=True):
        return GenericValue._from_ptr(lib.LLVMCreateGenericValueOfInt(typ, val, signed))

    @staticmethod
    def pointer(ptr):
        return GenericValue._from_ptr(lib.LLVMCreateGenericValueOfPointer(ptr))

    @staticmethod
    def float(typ, f):
        return GenericValue._from_ptr(lib.LLVMCreateGenericValueOfPointer(typ, f))

    def as_int(self, signed=True):
        return lib.LLVMGenericValueToInt(self, signed)

    def as_pointer(self):
        return lib.LLVMGenericValueToPointer(self)

    def as_float(typ, self):
        return lib.LLVMGenericValueToFloat(typ, self)

    def __dispose__(self):
        lib.LLVMDisposeGenericValue(self)

def _create_ee(module):
    ptr = ctypes.cast(ctypes.c_void_p(0), c_object_p)
    err = ctypes.c_char_p()
    if lib.LLVMCreateExecutionEngineForModule(ctypes.byref(ptr), module, ctypes.byref(err)):
        raise RuntimeError(err.value)
    return ptr

@lib.c_name("LLVMExecutionEngineRef")
class ExecutionEngine(LLVMObject):
    """Create a new executionengine for executing (interpreting or
    jit) functions in a module.

    This allows running functions in the module as well as access
    to global variables in the module.

    Args:
        - module (:class:`llvm.core.module.Module`): The module this executionengine can execute functions in.

    """
    def __init__(self, module):
        _ensure_native_target_initialized()

        ptr = _create_ee(module)
        LLVMObject.__init__(self, ptr=ptr)

        self.take_ownership(module)

    def __dispose__(self):
        lib.LLVMDisposeExecutionEngine(self)

    def add_module(self, module):
        self.take_ownership(module)
        return lib.LLVMAddModule(self, module)

    def get_pointer_to_global(self, g):
        return lib.LLVMGetPointerToGlobal(self, g)

    def set_pointer_to_global(self, g, ptr):
        lib.LLVMAddGlobalMapping(self, g, ptr)

    def run_static_constructors(self):
        lib.LLVMRunStaticConstructors(self)

    def run_static_destructors(self):
        lib.LLVMRunStaticDestructors(self)

    def run_function(self, function, *args):
        """Run specified function.

        Function is executed with the specified arguments, which are
        given as `:class:GenericValue` and must match the
        corresponding argument types.

        Args:
            - function (:class:`llvm.core.values.Function`): The function to execute.
            - args (list of :class:`GenericValue`): Arguments to the function.

        """
        argarr = create_c_object_p_array(args, GenericValue)
        return GenericValue._from_ptr(lib.LLVMRunFunction(self, function, len(args), argarr))

    def get_pointer_to_function(self, function):
        return lib.LLVMGetPointerToFunction(self, function)

    def create_pyfunc(self, function):
        """Create a python function that executes specified function in the LLVM ir.

        Returns a python function that acts as a proxy for the
        specified LLVM function and automatically converts values to
        and from `:class:GenericValue`.

        Args:
            - function (:class:`llvm.core.values.Function`): The function to create proxy for.

        .. note::

           Currently only integer argument types and return type is supported.
        """
        ptypes = function.type.element_type.param_types
        rtype = function.type.element_type.return_type

        argconverters = []
        for ptype in ptypes:
            if isinstance(ptype, types.IntType):
                conv = lambda a: GenericValue.int(ptype, a)
            else:
                raise TypeError("Unsupported argument type")
            argconverters.append(conv)

        if isinstance(rtype, types.IntType):
            retconverter = lambda a: a.as_int()
        else:
            raise TypeError("Unsupported returntype")

        def _(*args):
            gvargs = []
            for conv, arg in zip(argconverters, args):
                gvargs.append(conv(arg))

            rv = self.run_function(function, *gvargs)
            return retconverter(rv)
        _.__name__ = function.name
        return _
