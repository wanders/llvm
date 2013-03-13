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
from .common import get_library
from .common import create_c_object_p_array

from .core import types

import ctypes

lib = get_library()


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


def list():
    """
    List all available targets.
    """
    o = lib.LLVMGetFirstTarget()
    while o:
        t = Target(ptr=o)
        yield t
        o = lib.LLVMGetNextTarget(t)

