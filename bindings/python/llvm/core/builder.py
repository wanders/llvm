#===- builder.py - Python Object Bindings --------------------*- python -*--===#
#
#                     The LLVM Compiler Infrastructure
#
# This file is distributed under the University of Illinois Open Source
# License. See LICENSE.TXT for details.
#
#===------------------------------------------------------------------------===#

from ..common import LLVMObject
from ..common import get_library
from ..common import get_library, create_c_object_p_array, create_empty_c_object_p_array
from .value import Value

from ctypes import byref

V=Value._create_from_ptr

lib = get_library()

@lib.c_name("LLVMBuilderRef")
class Builder(LLVMObject):
    def __init__(self, basicblock):
        ptr = lib.LLVMCreateBuilder(basicblock)
        LLVMObject.__init__(self, ptr=ptr)
        self.position_at_end(basicblock)

    def __dispose__(self):
        lib.LLVMDisposeBuilder(self)

    def position_before(self, inst):
        lib.LLVMPositionBuilderBefore(self, inst)

    def position_at_end(self, basicblock):
        lib.LLVMPositionBuilderAtEnd(self, basicblock)

    def clear_position(self):
        lib.LLVMClearInsertionPosition(self)

    @property
    def basic_block(self):
        return V(lib.LLVMGetInsertBlock(self))

    def insert(self, inst):
        lib.LLVMInsertIntoBuilder(self, inst)

    #lib.LLVMSetCurrentDebugLocation
    #lib.LLVMGetCurrentDebugLocation
    #lib.LLVMSetInstDebugLocation


    def ret(self, val):
        return V(lib.LLVMBuildRet(self, val))

    def ret_void(self):
        return V(lib.LLVMBuildRetVoid(self))

    def ret_aggregate(self, vals):
        arglist = create_c_object_p_array(vals, Value)
        return V(lib.LLVMBuildAggregateRet(self, byref(arglist), len(vals)))

    def br(self, bb):
        return V(lib.LLVMBuildBr(self, bb))

    def cond_br(self, cond, tbb, fbb):
        return V(lib.LLVMBuildCondBr(self, cond, tbb, fbb))


    def switch(self, val, elsebb, estimated_count=16):
        return V(lib.LLVMBuildSwitch(self, val, elsebb, estimated_count))

    # lib.LLVMBuildIndirectBr.argtypes = [LLVMBuilderRef, LLVMValueRef, c_uint]
    # lib.LLVMBuildInvoke.argtypes = [LLVMBuilderRef, LLVMValueRef, POINTER(LLVMValueRef), c_uint, LLVMBasicBlockRef, LLVMBasicBlockRef, c_char_p]
    # lib.LLVMBuildLandingPad.argtypes = [LLVMBuilderRef, LLVMTypeRef, LLVMValueRef, c_uint, c_char_p]
    # lib.LLVMBuildResume.argtypes = [LLVMBuilderRef, LLVMValueRef]

    def unreachable(self):
        return V(lib.LLVMBuildUnreachable(self))

    # lib.LLVMBuildBinOp.argtypes = [LLVMBuilderRef, LLVMOpcode, LLVMValueRef, LLVMValueRef, c_char_p]

    # lib.LLVMBuildMalloc.argtypes = [LLVMBuilderRef, LLVMTypeRef, c_char_p]
    # lib.LLVMBuildArrayMalloc.argtypes = [LLVMBuilderRef, LLVMTypeRef, LLVMValueRef, c_char_p]
    # lib.LLVMBuildAlloca.argtypes = [LLVMBuilderRef, LLVMTypeRef, c_char_p]
    # lib.LLVMBuildArrayAlloca.argtypes = [LLVMBuilderRef, LLVMTypeRef, LLVMValueRef, c_char_p]
    # lib.LLVMBuildFree.argtypes = [LLVMBuilderRef, LLVMValueRef]

    def load(self, ptr, name=""):
        return V(lib.LLVMBuildLoad(self, ptr, name))

    # lib.LLVMBuildLoad.argtypes = [LLVMBuilderRef, LLVMValueRef, c_char_p]
    # lib.LLVMBuildStore.argtypes = [LLVMBuilderRef, LLVMValueRef, LLVMValueRef]
    # lib.LLVMBuildGEP.argtypes = [LLVMBuilderRef, LLVMValueRef, POINTER(LLVMValueRef), c_uint, c_char_p]
    # lib.LLVMBuildInBoundsGEP.argtypes = [LLVMBuilderRef, LLVMValueRef, POINTER(LLVMValueRef), c_uint, c_char_p]
    # lib.LLVMBuildStructGEP.argtypes = [LLVMBuilderRef, LLVMValueRef, c_uint, c_char_p]
    # lib.LLVMBuildGlobalString.argtypes = [LLVMBuilderRef, c_char_p, c_char_p]
    # lib.LLVMBuildGlobalStringPtr.argtypes = [LLVMBuilderRef, c_char_p, c_char_p]

    # lib.LLVMBuildCast.argtypes = [LLVMBuilderRef, LLVMOpcode, LLVMValueRef, LLVMTypeRef, c_char_p]

    def _cast(llvmfuncname):
        def some_castop(self, val, typ, name=""):
            llvmfunc = getattr(lib, "LLVMBuild"+llvmfuncname)
            return V(llvmfunc(self, val, typ, name))
        some_castop.__name__ = llvmfuncname.lower()
        return some_castop

    trunc = _cast("Trunc")
    zext = _cast("ZExt")
    sext = _cast("SExt")
    fptoui = _cast("FPToUI")
    fptosi = _cast("FPToSI")
    uitofp = _cast("UIToFP")
    sitofp = _cast("SIToFP")
    fptrunc = _cast("FPTrunc")
    fpext = _cast("FPExt")
    ptrtoint = _cast("PtrToInt")
    inttoptr = _cast("IntToPtr")
    bitcast = _cast("BitCast")
    zextorbitcast = _cast("ZExtOrBitCast")
    sextorbitcast = _cast("SExtOrBitCast")
    truncorbitcast = _cast("TruncOrBitCast")
    pointercast = _cast("PointerCast")
    intcast = _cast("IntCast")
    fpcast = _cast("FPCast")


    def icmp(self, pred, lhs, rhs, name=""):
        return V(lib.LLVMBuildICmp(self, pred, lhs, rhs, name))

    def fcmp(self, pred, lhs, rhs, name=""):
        return V(lib.LLVMBuildFCmp(self, pred, lhs, rhs, name))


    def phi(self, typ, name=""):
        return V(lib.LLVMBuildPhi(self, typ, name))

    # lib.LLVMBuildCall.argtypes = [LLVMBuilderRef, LLVMValueRef, POINTER(LLVMValueRef), c_uint, c_char_p]

    def call(self, callee, args, name=""):
        arglist = create_c_object_p_array(args, Value)
        return V(lib.LLVMBuildCall(self, callee, arglist, len(args), name))

    # lib.LLVMBuildSelect.argtypes = [LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef, c_char_p]
    # lib.LLVMBuildVAArg.argtypes = [LLVMBuilderRef, LLVMValueRef, LLVMTypeRef, c_char_p]

    # lib.LLVMBuildExtractElement.argtypes = [LLVMBuilderRef, LLVMValueRef, LLVMValueRef, c_char_p]
    # lib.LLVMBuildInsertElement.argtypes = [LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef, c_char_p]
    # lib.LLVMBuildShuffleVector.argtypes = [LLVMBuilderRef, LLVMValueRef, LLVMValueRef, LLVMValueRef, c_char_p]
    # lib.LLVMBuildExtractValue.argtypes = [LLVMBuilderRef, LLVMValueRef, c_uint, c_char_p]
    # lib.LLVMBuildInsertValue.argtypes = [LLVMBuilderRef, LLVMValueRef, LLVMValueRef, c_uint, c_char_p]

    # lib.LLVMBuildIsNull.argtypes = [LLVMBuilderRef, LLVMValueRef, c_char_p]
    # lib.LLVMBuildIsNotNull.argtypes = [LLVMBuilderRef, LLVMValueRef, c_char_p]

    # lib.LLVMBuildPtrDiff.argtypes = [LLVMBuilderRef, LLVMValueRef, LLVMValueRef, c_char_p]

    def _binop(llvmfuncname):
        def some_binop(self, lhs, rhs, name=""):
            llvmfunc = getattr(lib, "LLVMBuild"+llvmfuncname)
            return V(llvmfunc(self, lhs, rhs, name))
        some_binop.__name__ = llvmfuncname.lower()
        return some_binop

    add = _binop("Add")
    nswadd = _binop("NSWAdd")
    nuwadd = _binop("NUWAdd")
    fadd = _binop("FAdd")
    sub = _binop("Sub")
    nswsub = _binop("NSWSub")
    nuwsub = _binop("NUWSub")
    fsub = _binop("FSub")
    mul = _binop("Mul")
    nswmul = _binop("NSWMul")
    nuwmul = _binop("NUWMul")
    fmul = _binop("FMul")
    udiv = _binop("UDiv")
    sdiv = _binop("SDiv")
    exactsdiv = _binop("ExactSDiv")
    fdiv = _binop("FDiv")
    urem = _binop("URem")
    srem = _binop("SRem")
    frem = _binop("FRem")
    shl = _binop("Shl")
    lshr = _binop("LShr")
    ashr = _binop("AShr")
    and_ = _binop("And")
    or_ = _binop("Or")
    xor = _binop("Xr")

    #unary
    def _unary(llvmfuncname):
        def some_unop(self, op, name=""):
            llvmfunc = getattr(lib, "LLVMBuild"+llvmfuncname)
            return V(llvmfunc(self, op, name))
        some_unop.__name__ = llvmfuncname.lower()
        return some_unop

    neg = _unary("Neg")
    nswneg = _unary("NSWNeg")
    nuwneg = _unary("NUWNeg")
    fneg = _unary("FNeg")
    not_ = _unary("Not")
