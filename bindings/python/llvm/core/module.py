#===- module.py - Python Object Bindings ---------------------*- python -*--===#
#
#                     The LLVM Compiler Infrastructure
#
# This file is distributed under the University of Illinois Open Source
# License. See LICENSE.TXT for details.
#
#===------------------------------------------------------------------------===#

import tempfile
import ctypes

from ctypes import string_at

from ..common import LLVMObject
from ..common import LLVMEnum

from ..common import get_library
from ..common import c_object_p

from llvm.core.value import Value
from .context import Context

from .memorybuffer import MemoryBuffer

import value

lib = get_library()


@lib.c_name("LLVMModuleRef")
class Module(LLVMObject):
    """Represents the top-level structure of an llvm program in an opaque object."""
    def __init__(self, name=None, context=None, ptr=None):
        """
        Create a new module.

        Args:
            - name (str): Name of the new module.
            - context (:class:`llvm.core.context.Context`): Context to create module in, defaults to the global context.

        """
        if ptr is None:
            if name is None:
                raise ValueError("Module must have name")
            if context is None:
                context = Context.GetGlobalContext()

            ptr = lib.LLVMModuleCreateWithNameInContext(name, context)

        LLVMObject.__init__(self, ptr=ptr)

    @staticmethod
    def from_bitcode_buffer(contents, context=None):
        """
        Create a new module by reading bitcode from the specified memorybuffer.

        Args:
            - path (:class:`llvm.core.memorybuffer.MemoryBuffer`): Path to the file to read bitcode from.
            - context (:class:`llvm.core.context.Context`): Context to create module in, defaults to the global context.
        """
        if context is None:
            context = Context.GetGlobalContext()
        ptr = c_object_p()
        err = ctypes.c_char_p()
        r = lib.LLVMParseBitcodeInContext(context, contents, ctypes.byref(ptr), ctypes.byref(err))
        if r:
            raise ValueError("Error loading bitcode: %s" % err.value)
        m = Module(ptr=ptr)
        m.take_ownership(contents)
        return m

    @staticmethod
    def from_bitcode_file(path, context=None):
        """
        Create a new module by reading bitcode from a file.

        Args:
            - path (str): Path to the file to read bitcode from.
            - context (:class:`llvm.core.context.Context`): Context to create module in, defaults to the global context.
        """
        contents = MemoryBuffer(filename=path)
        return Module.from_bitcode_buffer(contents, context)

    def __dispose__(self):
        lib.LLVMDisposeModule(self)

    @property
    def target(self):
        """Obtain or set the target triple for this module"""
        return string_at(lib.LLVMGetTarget(self))
    @target.setter
    def target(self, tgt):
        lib.LLVMSetTarget(self, tgt)

    @property
    def data_layout(self):
        """Obtain or set the data layout for this module."""
        return string_at(lib.LLVMGetDataLayout(self))

    @data_layout.setter
    def data_layout(self, tgt):
        lib.LLVMSetDataLayout(self, tgt)

    datalayout = data_layout ## XXX

    @property
    def context(self):
        """Return the Context this module was created in.
        """
        return Context._from_ptr(lib.LLVMGetModuleContext(self))

    def dump(self):
        """Dump the module to standard error.

        .. note::

           This method does a raw dump to the stderr fd, bypassing
           sys.stderr.
        """
        lib.LLVMDumpModule(self)

    def verify(self):
        """Run sanity check on module.
        """
        msg = ctypes.c_char_p()
        r = lib.LLVMVerifyModule(self, VerifierFailureAction.ReturnStatus, ctypes.byref(msg))
        if r:
            raise ValueError(msg.value)
        return True

    def to_assembly(self):
        """Return the IR for this module as a human readable string"""
        tmp = tempfile.NamedTemporaryFile()

        err = ctypes.c_char_p()

        r = lib.LLVMPrintModuleToFile(self, tmp.name, ctypes.byref(err))
        if r:
            raise RuntimeError(err.value)
        return tmp.read()

    def write_bitcode(self, fil):
        """Write the bitcode for this module to specified file.

        Args:
           fil (object): A filelike object with a `fileno` method.

        """
        r = lib.LLVMWriteBitcodeToFD(self, fil.fileno(), 0, 1)
        if r != 0:
            raise IOError("Error writing to file: %d", r)

    def to_bitcode(self):
        """Return the bitcode for this module"""
        tmp=tempfile.TemporaryFile()
        self.write_bitcode(tmp)
        tmp.seek(0)
        return tmp.read()

    class __function_iterator(object):
        def __init__(self, module, reverse=False):
            self.module = module
            self.reverse = reverse
            if self.reverse:
                self.function = self.module.last
            else:
                self.function = self.module.first
        
        def __iter__(self):
            return self
        
        def next(self):
            if not isinstance(self.function, value.Function):
                raise StopIteration("")
            result = self.function
            if self.reverse:
                self.function = self.function.prev
            else:
                self.function = self.function.next
            return result
    
    def __iter__(self):
        return Module.__function_iterator(self)

    def __reversed__(self):
        return Module.__function_iterator(self, reverse=True)

    @property
    def first(self):
        return value.Value._create_from_ptr(lib.LLVMGetFirstFunction(self))

    @property
    def last(self):
        return value.Value._create_from_ptr(lib.LLVMGetLastFunction(self))

    def print_module_to_file(self, filename):
        out = ctypes.c_char_p(None)
        # Result is inverted so 0 means everything was ok.
        result = lib.LLVMPrintModuleToFile(self, filename, ctypes.byref(out))        
        if result:
            raise RuntimeError("LLVM Error: %s" % out.value)

    def add_function(self, functype, name):
        """
        Add a new function to the module.

        Args:
            - functype (:class:`llvm.core.types.FunctionType`): Type of the new function.
            - name (str): Name of the new function.

        Returns:
            :class:`llvm.core.value.Function` -- the newly created function.
        """
        return value.Value._create_from_ptr(lib.LLVMAddFunction(self, name, functype))

    def get_function(self, name):
        return value.Value._create_from_ptr(lib.LLVMGetNamedFunction(self, name))

    def add_global_variable(self, vartype, name):
        """
        Add a new global variable to the module.

        Args:
            - vartype (:class:`llvm.core.types.Type`): Type of the global variable.
            - name (str): Name of the global variable

        Returns:
            :class:`llvm.core.value.GlobalVariable` -- the new global variable.

        """
        return value.Value._create_from_ptr(lib.LLVMAddGlobal(self, vartype, name))

@lib.c_enum("LLVMVerifierFailureAction", "LLVM", "Action")
class VerifierFailureAction(LLVMEnum):
    pass
