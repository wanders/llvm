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

from ctypes import byref
from ctypes import c_char_p
from ctypes import c_uint
from ctypes import string_at

__all__ = [
    "lib",
    "OpCode",
    "MemoryBuffer",
    "Module",
    "Value",
    "Function",
    "BasicBlock",
    "Instruction",
    "Context",
    "PassRegistry"
]

lib = get_library()


@lib.c_enum("LLVMOpcode", "LLVM", "")
class OpCode(LLVMEnum):
    """Represents an individual OpCode enumeration."""

@lib.c_name("LLVMValueRef")
class Value(LLVMObject):
    
    def __init__(self, value):
        LLVMObject.__init__(self, value)

    @property
    def name(self):
        return string_at(lib.LLVMGetValueName(self))

    def dump(self):
        lib.LLVMDumpValue(self)
    
    def get_operand(self, i):
        return Value(lib.LLVMGetOperand(self, i))
    
    def set_operand(self, i, v):
        return lib.LLVMSetOperand(self, i, v)
    
    def __len__(self):
        return lib.LLVMGetNumOperands(self)

@lib.c_name("LLVMModuleRef")
class Module(LLVMObject):
    """Represents the top-level structure of an llvm program in an opaque object."""

    def __init__(self, module, name=None, context=None):
        LLVMObject.__init__(self, module)

    def __dispose__(self):
        lib.LLVMDisposeModule(self)

    @classmethod
    def CreateWithName(cls, module_id):
        m = Module(lib.LLVMModuleCreateWithName(module_id))
        c = Context.GetGlobalContext().take_ownership(m)
        return m

    @staticmethod
    def from_bitcode_buffer(contents, context=None):
        """
        Create a new module by reading bitcode from the specified memorybuffer.

        Args:
            - contents (:class:`llvm.core.memorybuffer.MemoryBuffer`): Memorybuffer to read bitcode from.
            - context (:class:`llvm.core.context.Context`): Context to create module in, defaults to the global context.
        """
        if context is None:
            context = Context.GetGlobalContext()
        ptr = c_object_p()
        err = c_char_p()
        r = lib.LLVMParseBitcodeInContext(context, contents, byref(ptr), byref(err))
        if r:
            raise ValueError("Error loading bitcode: %s" % err.value)
        m = Module(module=ptr)
        m.take_ownership(contents)
        return m

    @property
    def datalayout(self):
        return string_at(lib.LLVMGetDataLayout(self))

    @datalayout.setter
    def datalayout(self, new_data_layout):
        """new_data_layout is a string."""
        lib.LLVMSetDataLayout(self, new_data_layout)

    @property
    def target(self):
        return string_at(lib.LLVMGetTarget(self))

    @target.setter
    def target(self, new_target):
        """new_target is a string."""
        lib.LLVMSetTarget(self, new_target)

    def dump(self):
        lib.LLVMDumpModule(self)

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
            if not isinstance(self.function, Function):
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
        return Function(lib.LLVMGetFirstFunction(self))

    @property
    def last(self):
        return Function(lib.LLVMGetLastFunction(self))

    def print_module_to_file(self, filename):
        out = c_char_p(None)
        # Result is inverted so 0 means everything was ok.
        result = lib.LLVMPrintModuleToFile(self, filename, byref(out))        
        if result:
            raise RuntimeError("LLVM Error: %s" % out.value)

class Function(Value):

    def __init__(self, value):
        Value.__init__(self, value)
    
    @property
    def next(self):
        f = lib.LLVMGetNextFunction(self)
        return f and Function(f)
    
    @property
    def prev(self):
        f = lib.LLVMGetPreviousFunction(self)
        return f and Function(f)
    
    @property
    def first(self):
        b = lib.LLVMGetFirstBasicBlock(self)
        return b and BasicBlock(b)

    @property
    def last(self):
        b = lib.LLVMGetLastBasicBlock(self)
        return b and BasicBlock(b)

    class __bb_iterator(object):
        def __init__(self, function, reverse=False):
            self.function = function
            self.reverse = reverse
            if self.reverse:
                self.bb = function.last
            else:
                self.bb = function.first
        
        def __iter__(self):
            return self
        
        def next(self):
            if not isinstance(self.bb, BasicBlock):
                raise StopIteration("")
            result = self.bb
            if self.reverse:
                self.bb = self.bb.prev
            else:
                self.bb = self.bb.next
            return result
    
    def __iter__(self):
        return Function.__bb_iterator(self)

    def __reversed__(self):
        return Function.__bb_iterator(self, reverse=True)
    
    def __len__(self):
        return lib.LLVMCountBasicBlocks(self)

@lib.c_name("LLVMBasicBlockRef")
class BasicBlock(LLVMObject):
    
    def __init__(self, value):
        LLVMObject.__init__(self, value)

    @property
    def next(self):
        b = lib.LLVMGetNextBasicBlock(self)
        return b and BasicBlock(b)

    @property
    def prev(self):
        b = lib.LLVMGetPreviousBasicBlock(self)
        return b and BasicBlock(b)
    
    @property
    def first(self):
        i = lib.LLVMGetFirstInstruction(self)
        return i and Instruction(i)

    @property
    def last(self):
        i = lib.LLVMGetLastInstruction(self)
        return i and Instruction(i)

    def __as_value(self):
        return Value(lib.LLVMBasicBlockAsValue(self))
    
    @property
    def name(self):
        return string_at(lib.LLVMGetValueName(self.__as_value()))

    def dump(self):
        lib.LLVMDumpValue(self.__as_value())

    def get_operand(self, i):
        return Value(lib.LLVMGetOperand(self.__as_value(),
                                        i))
    
    def set_operand(self, i, v):
        return lib.LLVMSetOperand(self.__as_value(),
                                  i, v)
    
    def __len__(self):
        return lib.LLVMGetNumOperands(self.__as_value())

    class __inst_iterator(object):
        def __init__(self, bb, reverse=False):            
            self.bb = bb
            self.reverse = reverse
            if self.reverse:
                self.inst = self.bb.last
            else:
                self.inst = self.bb.first
        
        def __iter__(self):
            return self
        
        def next(self):
            if not isinstance(self.inst, Instruction):
                raise StopIteration("")
            result = self.inst
            if self.reverse:
                self.inst = self.inst.prev
            else:
                self.inst = self.inst.next
            return result
    
    def __iter__(self):
        return BasicBlock.__inst_iterator(self)

    def __reversed__(self):
        return BasicBlock.__inst_iterator(self, reverse=True)


class Instruction(Value):

    def __init__(self, value):
        Value.__init__(self, value)

    @property
    def next(self):
        i = lib.LLVMGetNextInstruction(self)
        return i and Instruction(i)

    @property
    def prev(self):
        i = lib.LLVMGetPreviousInstruction(self)
        return i and Instruction(i)

    @property
    def opcode(self):
        return OpCode(lib.LLVMGetInstructionOpcode(self))

@lib.c_name("LLVMContextRef")
class Context(LLVMObject):

    def __init__(self, context=None):
        if context is None:
            context = lib.LLVMContextCreate()
            LLVMObject.__init__(self, context)
        else:
            LLVMObject.__init__(self, context)

    def __dispose__(self):
        #lib.LLVMContextDispose(self)
        pass

    @classmethod
    def GetGlobalContext(cls):
        c = Context(lib.LLVMGetGlobalContext())
        c._self_owned = False
        return c

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
