#===- value.py - Python LLVM Bindings ------------------------*- python -*--===#
#
#                     The LLVM Compiler Infrastructure
#
# This file is distributed under the University of Illinois Open Source
# License. See LICENSE.TXT for details.
#
#===------------------------------------------------------------------------===#

r"""
IR Value Types
==============

This module defines the Python classes for LLVM's Value class tree. These
correspond to typed values in LLVM's IR.

The classes in this file map to the classes exposed by llvm::Value and its
descendents.

See http://llvm.org/docs/ProgrammersManual.html#Value and
http://llvm.org/doxygen/classllvm_1_1Value.html for more.
"""

from ctypes import c_char_p
from ctypes import c_int

from . import enumerations
from .common import CachedProperty
from .common import LLVMObject
from .common import c_object_p

__all__ = [
    'Constant',
    'Instruction',
    'Operator',
    'User',
    'Value',
]

lib = None

class OpCode(object):
    """Represents an individual OpCode enumeration."""

    _value_map = {}

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return 'OpCode.%s' % self.name

    @staticmethod
    def from_value(value):
        """Obtain an OpCode instance from a numeric value."""
        result = OpCode._value_map.get(value, None)

        if result is None:
            raise ValueError('Unknown OpCode: %d' % value)

        return result

    @staticmethod
    def register(name, value):
        """Registers a new OpCode enumeration.

        This is called by this module for each enumeration defined in
        enumerations. You should not need to call this outside this module.
        """
        if value in OpCode._value_map:
            raise ValueError('OpCode value already registered: %d' % value)

        opcode = OpCode(name, value)
        OpCode._value_map[value] = opcode
        setattr(OpCode, name, opcode)

class Attribute(object):
    pass

class Value(LLVMObject):
    type_tree = {
        'Constant': {
            '_default': Constant,
            'BlockAddress': BlockAddress,
            'ConstantAggregateZero': ConstantAggregateZero,
            'ConstantArray': ConstantArray,
            'ConstantDataSequential': {
                '_default': ConstantDataSequential,
                'ConstantDataArray': ConstantDataArray,
                'ConstantDataVector': ConstantDataVector,
            },
            'ConstantExpr': {
                '_default': ConstantExpr,
                'BinaryConstantExpr': BinaryConstantExpr,
                'CompareConstantExpr': CompareConstantExpr,
                'ExtractElementConstantExpr': ExtractElementConstantExpr,
                'ExtractValueConstantExpr': ExtractValueConstantExpr,
                'GetElementPtrConstantExpr': GetElmenetPtrConstantExpr,
                'InsertElementConstantExpr': InsertElementConstnatExpr,
                'SelectConstantExpr': SelectConstantExpr,
                'ShuffleVectorConstantExpr': ShuffleVectorConstantExpr,
                'UnaryConstantExpr': UnaryConstantExpr,
            },
            'ConstantFP': ConstantFP,
            'ConstantInt': ConstantInt,
            'ConstantPointerNull': ConstantPointerNull,
            'ConstantStruct': ConstantStruct,
            'ConstantVector': ConstantVector,
            'GlobalValue': {
                '_default': GlobalValue,
                'Function': Function,
                'GlobalAlias': GlobalAlias,
                'GlobalVariable': GlobalVariable,
            },
            'UndefValue': Undef,
        },
        'Instruction': {
            'AtomicCmpXchgInst': AtomicCmpXchg,
            'AtomicRMWInst': AtomicRMW,
            'BinaryOperator': BinaryOperator,
            'CallInst': {
                '_default': Call,
                # TODO There are more in this tree
            },
            'CmpInst': {
                '_default': Cmp,
                'FCmpInst': FCmp,
                'ICmpInst': ICmpInst,
            },
            'ExtractElementInst': ExtractElement,
            'FencInst': Fence,
            'GelElementPtrInst': GetElementPtr,
            'InsertElementInst': InsertElementInst,
            'InsertValueInst': InsertValue,
            'LandingPadInst': LandingPad,
            'PHINode': PHINode,
            'SelectInst': Select,
            'ShuffleVectorInst': ShuffleVector,
            'StoreInst': Store,
            'TerminatorInst': {
                '_default': Terminator,
                'BranchInst': Branch,
                'IndirectBrInst': IndirectBr,
                'InvokeInst': Invoke,
                'ResumeInst': Resume,
                'ReturnInst': Return,
                'SwitchInst': Switch,
                'UnreachableInst': Unreachable,
            },
            'UnaryInstruction': {
                '_default': Unary,
                'AllocaInst': Alloca,
                'CastInst': {
                    '_default': CastInst,
                    'BitCastInst': BitCast,
                    'FPExtInst': FPExt,
                    'FPToSIInst': FPToSI,
                    'FPToUIInst': FPToUI,
                    'FPTruncInst': FPTrunc,
                    'IntToPtrInst': IntToPtr,
                    'PtrToInstInst': PtrToInt,
                    'SExtInst': SExt,
                    'SIToFPInst': SIToFP,
                    'TruncInst': Trunc,
                    'UIToFPInst': UIToFP,
                    'ZExtInst': ZExt,
                },
            },
        },
        'Operator': Operator,
        'Argument': Argument,
        'BasicBlock': BasicBlock,
        'InlineAsm': InlineAsm,
        'MDNode': MDNode,
        'MDString': MDString,
        'PseudoSourceValue': {
            '_default': PseudoSourceValue,
            'FixedStackPseudoSourceValue': FixedStackPseudoSource,
        },

    }

    def __init__(self, ptr, context=None, module=None):
        LLVMObject.__init__(self, ptr)

        if module:
            self._set_ref('module', module)
            self._set_ref('context', module._get_ref('context'))

        if context:
            self._set_ref('context', context)

    @staticmethod
    def make(ptr, context):
        """Create a Value instance from a pointer.

        This takes a pointer to a ValueRef and creates the appropriate Python
        class for it by determining which value type it corresponds to.
        """
        # This implementation is currently horribly inefficient.
        # TODO Consider exposing llvm::Value::getValueID() and the ValueTy
        # enumeration to the C API (even though it isn't binary compatible).

        ty = None
        def test_entry(k, v):
            lib_func = 'LLVMIsA%s' % k

            if not lib[lib_func](ptr):
                return None

            if not isinstance(v, dict):
                return v

            best = v['_default']

            for k2, v2 in v.iteritems():
                if k2 == '_default':
                    continue

                if test_entry(k2, v2):
                    best = v2
                    break

            return best

        ty = Value

        for k, v in Value.type_tree.iteritems():
            result = test_entry(k, v)
            if result:
                ty = result
                break

        return ty(ptr, context=context)

    @CachedProperty
    def type(self):
        ptr = lib.LLVMTypeOf(self)

        return Type(ptr, context=self._get_ref('context'))

    def _name_getter(self):
        return lib.LLVMGetValueName(self).value

    def _name_setter(self, value):
        lib.LLVMSetValueName(self, value)

    property('name', _name_getter, _name_setter)

    def dump(self):
        """Dump a representation of this Value to stderr."""
        lib.LLVMDumpValue(self)

    def replace_all_uses(self, value):
        """Replace all uses of this Value with another Value."""
        lib.LLVMReplaceAllUsesWith(self, value)

class User(Value):
    def get_operands(self):
        raise Exception('TODO Implement.')

class Constant(User):
    pass

class GlobalValue(Constant):
    pass

class Function(GlobalValue):
    pass

class GlobalVariable(GlobalValue):
    pass

class BasicBlock(Value):
    pass

class Instruction(User):
    """Common base class for all LLVM instructions."""

    @property
    def has_metadata(self):
        return lib.LLVMHasMetadata(self) > 0

    def get_metadata(self, kind):
        ptr = lib.LLVMGetMetadata(self, kind)
        return MDNode(ptr, context=self._get_ref('context'))

    def set_metadata(self, kind, node):
        lib.LLVMSetMetadata(self, kind, node)

class Operator(User):
    pass

class Argument(Value):
    pass

class MDNode(Value):
    pass

class Use(LLVMObject):
    def __init__(self, ptr, context):
        LLVMObject.__init__(ptr, context=context)

    @property
    def user(self):
        ptr = lib.LLVMGetUser(self)
        return Value(ptr, context=self._get_ref('context'))

    @property
    def value(self):
        ptr = lib.LLVMGetUsedValue(self)
        return Value(ptr, context=self._get_ref('context'))

def register_library(library):
    """Registers functions with ctypes library instance."""

    library.LLVMAddAttribute.argtypes = [ArgumentValue, Attribute]

    library.LLVMAddFunctionAttr.argtypes = [FunctionValue, Attribute]

    library.LLVMDeleteFunction.argtypes = [Value]

    library.LLVMDeleteGlobal.argtypes = [Value]

    library.LLVMGetAlignment.argtypes = [GlobalValue]
    library.LLVMGetAlignment.restype = c_uint

    library.LLVMGetAttribute.argtypes = [ArgumentValue]
    library.LLVMGetAttribute.restype = c_int

    library.LLVMDumpValue.argtypes = [Value]

    library.LLVMGetFirstParam.argtypes = [FunctionValue]
    library.LLVMGetFirstParam.restype = c_object_p

    library.LLVMGetFirstUse.argtypes = [Value]
    library.LLVMGetFirstUse.restype = c_object_p

    library.LLVMGetFunctionAttr.argtypes = [FunctionValue]
    library.LLVMGetFunctionAttr.restype = c_int

    library.LLVMGetFunctionCallConv.argtypes = [FunctionValue]
    library.LLVMGetFunctionCallConv.restype = c_uint

    library.LLVMGetGC.argtypes = [FunctionValue]
    library.LLVMGetGC.restype = c_char_p

    library.LLVMGetInitializer.argtypes = [GlobalValue]
    library.LLVMGetInitializer.restype = c_object_p

    library.LLVMGetIntrinsicID.argtypes = [FunctionValue]
    library.LLVMGetIntrinsicID.restype = c_uint

    library.LLVMGetLinkage.argtypes = [GlobalValue]
    library.LLVMGetLinkage.restype = c_int

    library.LLVMGetMetadata.argtypes = [Instruction, c_uint]
    library.LLVMGetMetadata.restype = c_object_p

    library.LLVMGetNextFunction.argtypes = [Value]
    library.LLVMGetNextFunction.restype = c_object_p

    library.LLVMGetNextGlobal.argtypes = [Value]
    library.LLVMGetNextGlobal.restype = c_object_p

    library.LLVMGetNextUse.argtypes = [Use]
    library.LLVMGetNextUse.restype = c_object_p

    library.LLVMGetNumOperands.argtypes = [User]
    library.LLVMGetNumOperands.restype = c_int

    library.LLVMGetOperand.argtypes = [User, c_uint]
    library.LLVMGetOperand.restype = c_object_p

    library.LLVMGetSection.argtypes = [GlobalValue]
    library.LLVMGetSection.restype = c_char_p

    library.LLVMGetUsedValue.argtypes = [Use]
    library.LLVMGetUsedValue.restype = c_object_p

    library.LLVMGetUser.argtypes = [Use]
    library.LLVMGetUser.restype = c_object_p

    library.LLVMGetNextParam.argtypes = [Value]
    library.LLVMGetNextParam.restype = c_object_p

    library.LLVMGetValueName.argtypes = [Value]
    library.LLVMGetValueName.restype = c_char_p

    library.LLVMGetVisibility.argtypes = [GlobalValue]
    library.LLVMGetVisibility.restype = c_int

    library.LLVMHasMetadata.argtypes = [Instruction]
    library.LLVMHasMetadata.restype = c_int

    library.LLVMIsDeclaration.argtypes = [GlobalValue]
    library.LLVMIsDeclaration.restype = c_bool

    library.LLVMIsGlobalConstant.argtypes = [GlobalValue]
    library.LLVMIsGlobalConstant.restype = c_bool

    library.LLVMIsThreadLocal.argtypes = [GlobalValue]
    library.LLVMIsThreadLocal.restype = c_bool

    library.LLVMRemoveAttribute.argtypes = [ArgumentValue, Attribute]

    library.LLVMRemoveFunctionAttr.argtypes = [FunctionValue, Attribute]

    library.LLVMSetAlignment.argtypes = [GlobalValue, c_uint]

    library.LLVMSetFunctionCallConv.argtypes = [FunctionValue, c_uint]

    library.LLVMSetGC.argtypes = [FunctionValue, c_char_p]

    library.LLVMSetGlobalConstant.argtypes = [GlobalValue]

    library.LLVMSetInitializer.argtypes = [GlobalValue, ConstantValue]

    library.LLVMSetLinkage.argtypes = [GlobalValue, c_int]

    library.LLVMSetMetadata.argtypes = [Instruction, c_uint, MDNode]

    library.LLVMSetOperand.argtypes = [User, c_uint, Value]

    library.LLVMSetSection.argtypes = [GlobalValue, c_char_p]

    library.LLVMSetThreadLocal.argtypes = [GlobalValue]

    library.LLVMSetValueName.argtypes = [Value, c_char_p]

    library.LLVMSetVisibility.argtypes = [GlobalValue, c_int]

    library.LLVMTypeOf.argtypes = [Value]
    library.LLVMTypeOf.restype = c_object_p

    def handle_entry(k, v):
        if k == '_default':
            return

        func = 'LLVMIsA%s' % k

        library[func].argtypes = [c_object_p]
        library[func].restype = c_object_p

        if isinstance(v, dict):
            for k2, v2 in v.iteritems():
                handle_entry(k2, v2)

    for k, v in Value.type_tree.iteritems():
        handle_entry(k, v)

def register_enumerations():
    for name, value in enumerations.OpCodes:
        OpCode.register(name, value)

register_library(lib)
register_enumerations()

