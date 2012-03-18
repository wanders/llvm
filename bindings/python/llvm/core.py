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

def register_library(library):
    """Register C APIs with ctypes library instance.

    This list is pretty long. We define APIs in alphabetical order for
    sanity.
    """
    library.LLVMContextCreate.restype = c_object_p

    library.LLVMContextDispose.argtypes = [Context]

    library.LLVMCreateMemoryBufferWithContentsOfFile.argtypes = [c_char_p,
            POINTER(c_object_p), POINTER(c_char_p)]
    library.LLVMCreateMemoryBufferWithContentsOfFile.restype = bool

    library.LLVMDisposeMemoryBuffer.argtypes = [MemoryBuffer]

    library.LLVMGetGlobalContext.restype = c_object_p

register_library(lib)
