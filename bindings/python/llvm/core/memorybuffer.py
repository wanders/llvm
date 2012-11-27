#===- memorybuffer.py - Python LLVM Bindings -----------------*- python -*--===#
#
#                     The LLVM Compiler Infrastructure
#
# This file is distributed under the University of Illinois Open Source
# License. See LICENSE.TXT for details.
#
#===------------------------------------------------------------------------===#

from ..common import LLVMObject
from ..common import c_object_p
from ..common import get_library

from ctypes import byref
from ctypes import c_char_p

from tempfile import NamedTemporaryFile

lib = get_library()

@lib.c_name("LLVMMemoryBufferRef")
class MemoryBuffer(LLVMObject):
    """Represents an opaque memory buffer."""

    def __init__(self, filename=None, contents=None):
        """Create a new memory buffer.

        If `filename` argument is specified the memory buffer will
        contain the contents of that file. If `contents`, which should
        be a string, is specified the memory buffer will contain that
        data.
        """
        if filename is None and contents is None:
            raise TypeError("filename or contents argument must be defined")

        if contents is not None:
            tmp = NamedTemporaryFile()
            tmp.write(contents)
            tmp.flush()
            filename = tmp.name

        memory = c_object_p()
        out = c_char_p(None)

        result = lib.LLVMCreateMemoryBufferWithContentsOfFile(filename,
                byref(memory), byref(out))

        if result:
            raise RuntimeError("Could not create memory buffer: %s" % out.value)

        LLVMObject.__init__(self, memory)

    def __dispose__(self):
        lib.LLVMDisposeMemoryBuffer(self)

    def __len__(self):
        return lib.LLVMGetBufferSize(self)
