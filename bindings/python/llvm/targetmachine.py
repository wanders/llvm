#===- targetmachine.py - Python Object Bindings --------------*- python -*--===#
#
#                     The LLVM Compiler Infrastructure
#
# This file is distributed under the University of Illinois Open Source
# License. See LICENSE.TXT for details.
#
#===------------------------------------------------------------------------===#


from .common import c_object_p
from .common import LLVMObject
from .common import LLVMEnum
from .common import get_library
from .common import create_c_object_p_array

from .core import types

import ctypes

lib = get_library()


## maybe move to target.py..
@lib.c_name("LLVMTargetDataRef")
class TargetData(LLVMObject):
    def __init__(self, targetdata):
        """
        """
        ptr = lib.LLVMCreateTargetData(targetdata)
        LLVMObject.__init__(self, ptr=ptr)

    def __dispose__(self):
        lib.LLVMDisposeTargetData(self)

    @property
    def byteorder(self):
        return lib.LLVMByteOrder(self)
    @property
    def pointersize(self):
        return lib.LLVMPointerSize(self)
    @property
    def pointersizeforAS(self):
        return lib.LLVMPointerSizeForAS(self)
    @property
    def intptrtype(self):
        return lib.LLVMIntPtrType(self)
    @property
    def intptrtypeforAS(self):
        return lib.LLVMIntPtrTypeForAS(self)
    @property
    def sizeoftypeinbits(self):
        return lib.LLVMSizeOfTypeInBits(self)
    @property
    def storesizeoftype(self):
        return lib.LLVMStoreSizeOfType(self)
    @property
    def abisizeoftype(self):
        return lib.LLVMABISizeOfType(self)
    @property
    def ABIalignmentoftype(self):
        return lib.LLVMABIAlignmentOfType(self)
    @property
    def callframealignmentoftype(self):
        return lib.LLVMCallFrameAlignmentOfType(self)
    @property
    def preferredalignmentoftype(self):
        return lib.LLVMPreferredAlignmentOfType(self)
    @property
    def preferredalignmentofglobal(self):
        return lib.LLVMPreferredAlignmentOfGlobal(self)
    @property
    def elementatoffset(self):
        return lib.LLVMElementAtOffset(self)
    @property
    def offsetofelement(self):
        return lib.LLVMOffsetOfElement(self)



@lib.c_name("LLVMTargetRef")
class Target(LLVMObject):

    @property
    def name(self):
        """Name of the target"""
        return lib.LLVMGetTargetName(self)

    @property
    def description(self):
        """Targets description"""
        return lib.LLVMGetTargetDescription(self)

    @property
    def has_jit(self):
        """True if the target has a JIT"""
        return bool(lib.LLVMTargetHasJIT(self))

    @property
    def has_target_machine(self):
        """True if the target has a TargetMachine associated"""
        return bool(lib.LLVMTargetHasTargetMachine(self))

    @property
    def has_asm_backend(self):
        """True if the target as an ASM backend (required for emitting output)"""
        return bool(lib.LLVMTargetHasAsmBackend(self))


@lib.c_enum("LLVMByteOrdering", "LLVM", "")
class ByteOrdering(LLVMEnum):
    pass


def list():
    """
    List all available targets.
    """
    o = lib.LLVMGetFirstTarget()
    while o:
        t = Target(ptr=o)
        yield t
        o = lib.LLVMGetNextTarget(t)

