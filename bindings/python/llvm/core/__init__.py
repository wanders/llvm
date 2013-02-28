#===- core.py - Python LLVM Bindings -------------------------*- python -*--===#
#
#                     The LLVM Compiler Infrastructure
#
# This file is distributed under the University of Illinois Open Source
# License. See LICENSE.TXT for details.
#
#===------------------------------------------------------------------------===#

from ..common import LLVMEnum
from ..common import LLVMObject
from ..common import get_library
from ..common import c_object_p

from .context import Context

from ctypes import byref
from ctypes import c_char_p
from ctypes import c_uint
from ctypes import string_at

__all__ = [
    "lib",
    "OpCode",
    "MemoryBuffer",
    "Value",
    "Function",
    "BasicBlock",
    "Instruction",
    "PassRegistry"
]

lib = get_library()


@lib.c_enum("LLVMOpcode", "LLVM", "")
class OpCode(LLVMEnum):
    """Represents an individual OpCode enumeration."""


@lib.c_name("LLVMPassRegistryRef")
class PassRegistry(LLVMObject):
    """Represents an opaque pass registry object."""

    def __init__(self):
        LLVMObject.__init__(self,
                            lib.LLVMGetGlobalPassRegistry())


def initialize_llvm():
    c = Context.GetGlobalContext()
    p = PassRegistry()
    lib.LLVMInitializeCore(p)
    lib.LLVMInitializeTransformUtils(p)
    lib.LLVMInitializeScalarOpts(p)
    lib.LLVMInitializeObjCARCOpts(p)
    lib.LLVMInitializeVectorization(p)
    lib.LLVMInitializeInstCombine(p)
    lib.LLVMInitializeIPO(p)
    lib.LLVMInitializeInstrumentation(p)
    lib.LLVMInitializeAnalysis(p)
    lib.LLVMInitializeIPA(p)
    lib.LLVMInitializeCodeGen(p)
    lib.LLVMInitializeTarget(p)


# hmmm? this means we don't go lazy
initialize_llvm()
