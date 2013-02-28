#===- value.py - Python Object Bindings ----------------------*- python -*--===#
#
#                     The LLVM Compiler Infrastructure
#
# This file is distributed under the University of Illinois Open Source
# License. See LICENSE.TXT for details.
#
#===------------------------------------------------------------------------===#

from ..common import LLVMObject
from ..common import LLVMEnum
from ..common import get_library
from ..common import get_library, create_c_object_p_array, create_empty_c_object_p_array

import llvm.core.types
import llvm.core.module

from llvm.core import OpCode

import ctypes
from ctypes import string_at

lib = get_library()

@lib.c_name("LLVMValueRef")
class Value(LLVMObject):
    """
    This class is the root class of LLVM's Value class tree,
    corresponding to values in the IR (such as instructions).
    """
    @property
    def type(self):
        """
        The type of the value.
        """
        return llvm.core.types.Type._create_from_ptr(lib.LLVMTypeOf(self))

    @property
    def name(self):
        """
        This value's name.
        """
        return string_at(lib.LLVMGetValueName(self))
    @name.setter
    def name(self, name):
        lib.LLVMSetValueName(self, name)

    def is_constant(self):
        """
        """
        return bool(lib.LLVMIsConstant(self))

    def is_null(self):
        return bool(lib.LLVMIsNull(self))

    def is_undef(self):
        return bool(lib.LLVMIsUndef(self))

    @classmethod
    def _isa(cls, ptr):
        attr = "LLVMIsA"+cls.__name__
        class DummyValue(Value):
            def __init__(self):
                self._as_parameter_ = ptr
        return getattr(lib, attr)(DummyValue())

    @classmethod
    def _create_from_ptr(cls, ptr):
        if not ptr:
            return None
        assert cls == Value or cls._isa(ptr)
        for subclass in cls.__subclasses__():
            if subclass._isa(ptr):
                return subclass._create_from_ptr(ptr)
        return cls._from_ptr(ptr=ptr)

    def dump(self):
        lib.LLVMDumpValue(self)



class Argument(Value):
    pass
class BasicBlock(Value):
    pass
class InlineAsm(Value):
    pass
class MDNode(Value):
    @property
    def operands(self):
        nr = lib.LLVMGetNumOperands(self)
        return [Value._create_from_ptr(lib.LLVMGetOperand(self, i)) for i in range(nr)]

    def __getitem__(self, idx):
        nitems = lib.LLVMGetNumOperands(self)
        if idx < 0:
            idx = nitems + idx
        if not (0 <= idx < nitems):
            raise IndexError("Index out of range")
        return Value._create_from_ptr(lib.LLVMGetOperand(self, idx))

class MDString(Value):
    @property
    def value(self):
        l = ctypes.c_uint()
        return lib.LLVMGetMDString(self, ctypes.byref(l))
    def __repr__(self):
        return "<MDString: %s>" % repr(self.value)
    def __str__(self):
        return self.value

    def __hash__(self):
        return hash(self.value)
    def __eq__(self, o):
        if isinstance(o, MDString):
            return self.value == o.value
        if isinstance(o, basestring):
            return self.value == o
        raise TypeError("Can only compare MDString with str and other MDString")

class User(Value):
    @property
    def operands(self):
        nr = lib.LLVMGetNumOperands(self)
        return [Value._create_from_ptr(lib.LLVMGetOperand(self, i)) for i in range(nr)]

    def set_operand(self, pos, val):
        lib.LLVMSetOperand(self, pos, val)

    def get_operand(self, i):
        return Value(lib.LLVMGetOperand(self, i))

    def __len__(self):
        return lib.LLVMGetNumOperands(self)

class Constant(User):
    def __init__(self, typ=None, value=None, signextend=False, ptr=None):
        """
        Create new constant with specified type and value.

        Args:
            - typ (:class:`llvm.core.types.Type`): The type the new constant should have. (:class:`llvm.core.types.IntType`)
            - value (str or int): The value the new constant should have. Must be `int` for IntType:d constants, and float or string for FloatType:d.
            - signextend (bool):

        Returns:
            --
        """
        if ptr is None:
            import types
            if isinstance(typ, types.IntType):
                ptr = lib.LLVMConstInt(typ, value, signextend)
            elif isinstance(typ, types.FloatishType):
                if isinstance(value, basestring):
                    ptr = lib.LLVMConstRealOfString(typ, value)
                elif isinstance(value, float):
                    ptr = lib.LLVMConstReal(typ, value)
                else:
                    raise TypeError("value needs to be string or float")
            else:
                raise TypeError("Unsupported type")
        else:
            assert typ is None and value is None
        User.__init__(self, ptr=ptr)

    @staticmethod
    def undef(typ):
        return Value._create_from_ptr(lib.LLVMGetUndef(typ))

    @staticmethod
    def null(typ):
        return Value._create_from_ptr(lib.LLVMConstNull(typ))

    @staticmethod
    def all_ones(typ):
        return Value._create_from_ptr(lib.LLVMConstAllOnes(typ))

    @staticmethod
    def ptr_null(typ):
        return Value._create_from_ptr(lib.LLVMConstPointerNull(typ))

class BlockAddress(Constant):
    pass
class ConstantAggregateZero(Constant):
    pass
class ConstantArray(Constant):
    pass
class ConstantExpr(Constant):
    pass
class ConstantFP(Constant):
    pass
class ConstantInt(Constant):
    @property
    def value(self):
        return lib.LLVMConstIntGetZExtValue(self)

    @property
    def signed_value(self):
        return lib.LLVMConstIntGetSExtValue(self)

class ConstantPointerNull(Constant):
    pass
class ConstantStruct(Constant):
    pass
class ConstantVector(Constant):
    pass
class GlobalValue(Constant):
    @property
    def module(self):
        """
        The module the value belongs to.
        """
        return llvm.core.module.Module._from_ptr(lib.LLVMGetGlobalParent(self))


    @property
    def initializer(self):
        return lib.LLVMGetInitializer(self)
    @initializer.setter
    def initializer(self, val):
        lib.LLVMSetInitializer(self, val)

    @property
    def constant(self):
        return lib.LLVMIsGlobalConstant(self)
    @constant.setter
    def constant(self, val):
        lib.LLVMSetGlobalConstant(self, val)

    @property
    def thread_local(self):
        return lib.LLVMIsThreadLocal(self)
    @thread_local.setter
    def thread_local(self, val):
        lib.LLVMSetThreadLocal(self, val)

    @property
    def linkage(self):
        return lib.LLVMGetLinkage(self)
    @linkage.setter
    def linkage(self, val):
        lib.LLVMSetLinkage(self, val)

    @property
    def section(self):
        return lib.LLVMGetSection(self)
    @section.setter
    def section(self, val):
        lib.LLVMSetSection(self, val)

    @property
    def visibility(self):
        return lib.LLVMGetVisibility(self)
    @visibility.setter
    def visibility(self, val):
        lib.LLVMSetVisibility(self, val)

    @property
    def alignment(self):
        return lib.LLVMGetAlignment(self)
    @alignment.setter
    def alignment(self, val):
        lib.LLVMSetAlignment(self, val)


class Function(GlobalValue):
    @property
    def args(self):
        """
        The argument values of the function call.
        """
        cnt = lib.LLVMCountParams(self)
        arr = create_empty_c_object_p_array(cnt)
        lib.LLVMGetParams(self, arr)
        return map(Value._create_from_ptr, arr)

    def append_basic_block(self, name):
        return ProperBasicBlock._from_ptr(lib.LLVMAppendBasicBlock(self, name))

    @property
    def basic_blocks(self):
        f = ProperBasicBlock._from_ptr(lib.LLVMGetFirstBasicBlock(self))
        while f:
            yield f
            f = ProperBasicBlock._from_ptr(lib.LLVMGetNextBasicBlock(f))

    @property
    def entry(self):
        return ProperBasicBlock._from_ptr(lib.LLVMGetEntryBasicBlock(self))

    @property
    def next(self):
        f = lib.LLVMGetNextFunction(self)
        return f and Value._create_from_ptr(f)
    
    @property
    def prev(self):
        f = lib.LLVMGetPreviousFunction(self)
        return f and Value._create_from_ptr(f)
    
    @property
    def first(self):
        b = lib.LLVMGetFirstBasicBlock(self)
        return b and ProperBasicBlock._from_ptr(b)

    @property
    def last(self):
        b = lib.LLVMGetLastBasicBlock(self)
        return b and ProperBasicBlock._from_ptr(b)

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
            if not isinstance(self.bb, ProperBasicBlock):
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


class GlobalAlias(GlobalValue):
    pass
class GlobalVariable(GlobalValue):
    @property
    def initializer(self):
        return Value._create_from_ptr(lib.LLVMGetInitializer(self))

    @initializer.setter
    def initializer(self, val):
        lib.LLVMSetInitializer(self, val)

class UndefValue(Constant):
    pass
class Instruction(User):
    @property
    def basic_block(self):
        return ProperBasicBlock._from_ptr(lib.LLVMGetInstructionParent(self))

    def get_metadata(self, kind):
        kindid = lib.LLVMGetMDKindID(kind, len(kind))
        return Value._create_from_ptr(lib.LLVMGetMetadata(self, kindid))

    @property
    def next(self):
        i = lib.LLVMGetNextInstruction(self)
        return i and Value._create_from_ptr(i)

    @property
    def prev(self):
        i = lib.LLVMGetPreviousInstruction(self)
        return i and Value._create_from_ptr(i)

    @property
    def opcode(self):
        return OpCode(lib.LLVMGetInstructionOpcode(self))

class BinaryOperator(Instruction):
    pass
class CallInst(Instruction):
    @property
    def callee(self):
        return self.operands[-1]

    @property
    def tailcall(self):
        return lib.LLVMIsTailCall(self)
    @tailcall.setter
    def tailcall(self, value):
        lib.LLVMSetTailCall(self, bool(value))

class IntrinsicInst(CallInst):
    pass
class DbgInfoIntrinsic(IntrinsicInst):
    pass
class DbgDeclareInst(DbgInfoIntrinsic):
    pass
class MemIntrinsic(IntrinsicInst):
    pass
class MemCpyInst(MemIntrinsic):
    pass
class MemMoveInst(MemIntrinsic):
    pass
class MemSetInst(MemIntrinsic):
    pass
class CmpInst(Instruction):
    pass
class FCmpInst(CmpInst):
    pass
class ICmpInst(CmpInst):
    pass
class ExtractElementInst(Instruction):
    pass
class GetElementPtrInst(Instruction):
    pass
class InsertElementInst(Instruction):
    pass
class InsertValueInst(Instruction):
    pass
class LandingPadInst(Instruction):
    pass
class PHINode(Instruction):
    def add_incoming(self, *pairs):
        values, blocks = zip(*pairs) # unzip
        valarr = create_c_object_p_array(values, Value)
        blkarr = create_c_object_p_array(blocks, ProperBasicBlock)
        lib.LLVMAddIncoming(self, valarr, blkarr, len(pairs))

    @property
    def incoming(self):
        for i in xrange(lib.LLVMCountIncoming(self)):
            yield ((Value._create_from_ptr(lib.LLVMGetIncomingValue(self, i)),
                    ProperBasicBlock._from_ptr(lib.LLVMGetIncomingBlock(self, i))))

class SelectInst(Instruction):
    pass
class ShuffleVectorInst(Instruction):
    pass
class StoreInst(Instruction):
    pass
class TerminatorInst(Instruction):
    pass
class BranchInst(TerminatorInst):
    pass
class IndirectBrInst(TerminatorInst):
    pass
class InvokeInst(TerminatorInst):
    pass
class ReturnInst(TerminatorInst):
    pass
class SwitchInst(TerminatorInst):
    def add_case(self, value, block):
        lib.LLVMAddCase(self, value, block)

class UnreachableInst(TerminatorInst):
    pass
class ResumeInst(TerminatorInst):
    pass
class UnaryInstruction(Instruction):
    pass
class AllocaInst(UnaryInstruction):
    pass
class CastInst(UnaryInstruction):
    pass
class BitCastInst(CastInst):
    pass
class FPExtInst(CastInst):
    pass
class FPToSIInst(CastInst):
    pass
class FPToUIInst(CastInst):
    pass
class FPTruncInst(CastInst):
    pass
class IntToPtrInst(CastInst):
    pass
class PtrToIntInst(CastInst):
    pass
class SExtInst(CastInst):
    pass
class SIToFPInst(CastInst):
    pass
class TruncInst(CastInst):
    pass
class UIToFPInst(CastInst):
    pass
class ZExtInst(CastInst):
    pass
class ExtractValueInst(UnaryInstruction):
    pass
class LoadInst(UnaryInstruction):
    pass
class VAArgInst(UnaryInstruction):
    pass

@lib.c_enum("LLVMLinkage", "LLVM", "Linkage")
class Linkage(LLVMEnum):
    pass

@lib.c_name("LLVMBasicBlockRef")
class ProperBasicBlock(LLVMObject):
    @property
    def function(self):
        return Value._create_from_ptr(lib.LLVMGetBasicBlockParent(self))

    @property
    def instructions(self):
        c = Value._create_from_ptr(lib.LLVMGetFirstInstruction(self))
        while c:
            yield c
            c = Value._create_from_ptr(lib.LLVMGetNextInstruction(c))

    @property
    def terminator(self):
        return Value._create_from_ptr(lib.LLVMGetBasicBlockTerminator(self))

    @property
    def next(self):
        b = lib.LLVMGetNextBasicBlock(self)
        return b and ProperBasicBlock._from_ptr(b)

    @property
    def prev(self):
        b = lib.LLVMGetPreviousBasicBlock(self)
        return b and ProperBasicBlock._from_ptr(b)
    
    @property
    def first(self):
        i = lib.LLVMGetFirstInstruction(self)
        return i and Value._create_from_ptr(i)

    @property
    def last(self):
        i = lib.LLVMGetLastInstruction(self)
        return i and Value._create_from_ptr(i)

    @property
    def _value(self):
        return BasicBlock(ptr=lib.LLVMBasicBlockAsValue(self))

    @property
    def name(self):
        return self._value.name

    def dump(self):
        return self._value.dump()

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
        return ProperBasicBlock.__inst_iterator(self)

    def __reversed__(self):
        return ProperBasicBlock.__inst_iterator(self, reverse=True)
