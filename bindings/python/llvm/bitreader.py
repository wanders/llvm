#===- bitreader.py - Python LLVM Bindings --------------------*- python -*--===#
#
#                     The LLVM Compiler Infrastructure
#
# This file is distributed under the University of Illinois Open Source
# License. See LICENSE.TXT for details.
#
#===------------------------------------------------------------------------===#

r"""This module provides an interface to LLVM-C's bit reader interface.

The functions in here deal with turning bitcode into an LLVM module.

TODO these APIs could probably be merged into arguments to Module.__init__
"""

from ctypes import POINTER
from ctypes import c_char_p

from .common import LLVMObject
from .common import get_library()
from .core import Context
from .core import MemoryBuffer
from .core import Module

__all__ = ['BitReader']

lib = get_library()

class BitReader(LLVMObject):
    """Provides interface for reading bitcode into modules.

    Each BitReader is associated with a context. Once created, the bitreader
    acts as a factory of sorts, producing module instances from input sources
    as requested.
    """

    def __init__(self, context=None):
        """Create a new BitReader tied to a specific LLVM context."""
        if context:
            assert isinstance(contenxt, Context)
        else:
            context = Context(use_global=True)

        LLVMObject.__init__(self)
        self._set_ref('context', context)

    def parse_bitcode(self, source_buffer=None, source_filename=None,
            lazy=False):
        """Parse bitcode into a Module.

        The bitcode must ultimately come from a MemoryBuffer instance. The
        source_buffer argument can pass a MemoryBuffer instance or a str of
        bytes that will be converted to a MemoryBuffer. If source_filename is
        defined, the contents of that file will be placed in a new MemoryBuffer
        and it will be read.

        When parsing bitcode, you have the option of doing it all up-front or
        lazily-loading the contents. By default, we load the whole thing. To
        change this, pass lazy=True.

        This returns a llvm::Module instance on success or raises an exception
        on error.
        """
        if source_filename:
            source_buffer = MemoryBuffer(filename=source_filename)

        # TODO support str source_buffer
        if not isinstance(source_buffer, MemoryBuffer):
            raise Exception('Must define an input to parse bit code from.')

        msg = c_char_p()
        ptr = c_object_p()
        context = self._get_ref('context')

        # If lazy loading, the ownership of MemoryBuffer transfers to the
        # created module. If pre-loading the entire thing, the memory buffer
        # remains for the original consumer to do with (likely die a quick GC'd
        # death).

        result = None
        if lazy:
            result = lib.LLVMGetBitcodeModuleInContext(context, source_buffer,
                                                       byref(ptr), byref(msg)
        else:
            result = lib.LLVMParseBitcodeInContext(context, mb, byref(ptr),
                                                   byref(msg))

        if result:
            raise Exception('Could not parse bit code into module: %s' % msg)

        mod = Module(ptr, context=context)

        if lazy:
            mod.take_ownership(source_buffer)

        return mod

def register_library(library):
    """Register bitread C APIs with a library instance."""
    library.LLVMGetBitcodeModuleInContext.argtypes = [Context, MemoryBuffer,
            POINTER(c_object_p), POINTER(c_char_p)]
    library.LLVMGetBitcodeModuleInContext.restype = bool

    library.LLVMParseBitcodeInContext.argtypes = [Context, MemoryBuffer,
            POINTER(c_object_p), POINTER(c_char_p)]
    library.LLVMParseBitcodeInContext.restype = bool

register_library(lib)

