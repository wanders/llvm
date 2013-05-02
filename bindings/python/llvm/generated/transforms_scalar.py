#===-- Generated python interface definitions for 'Scalar.h' ---------------===#
#
#                     The LLVM Compiler Infrastructure
#
# This file is distributed under the University of Illinois Open Source
# License. See LICENSE.TXT for details.
#
#===------------------------------------------------------------------------===#
#
# This file is automatically generated by 'generate-from-includes.py',
# do not edit manually.
#
#===-----------------------------------------------------------------------====#

import ctypes
from ..common import c_object_p

function_declarations = {
    'LLVMAddAggressiveDCEPass': (None,
                                 ['LLVMPassManagerRef']),
    'LLVMAddCFGSimplificationPass': (None,
                                     ['LLVMPassManagerRef']),
    'LLVMAddDeadStoreEliminationPass': (None,
                                        ['LLVMPassManagerRef']),
    'LLVMAddGVNPass': (None,
                       ['LLVMPassManagerRef']),
    'LLVMAddIndVarSimplifyPass': (None,
                                  ['LLVMPassManagerRef']),
    'LLVMAddInstructionCombiningPass': (None,
                                        ['LLVMPassManagerRef']),
    'LLVMAddJumpThreadingPass': (None,
                                 ['LLVMPassManagerRef']),
    'LLVMAddLICMPass': (None,
                        ['LLVMPassManagerRef']),
    'LLVMAddLoopDeletionPass': (None,
                                ['LLVMPassManagerRef']),
    'LLVMAddLoopIdiomPass': (None,
                             ['LLVMPassManagerRef']),
    'LLVMAddLoopRotatePass': (None,
                              ['LLVMPassManagerRef']),
    'LLVMAddLoopUnrollPass': (None,
                              ['LLVMPassManagerRef']),
    'LLVMAddLoopUnswitchPass': (None,
                                ['LLVMPassManagerRef']),
    'LLVMAddMemCpyOptPass': (None,
                             ['LLVMPassManagerRef']),
    'LLVMAddPartiallyInlineLibCallsPass': (None,
                                           ['LLVMPassManagerRef']),
    'LLVMAddPromoteMemoryToRegisterPass': (None,
                                           ['LLVMPassManagerRef']),
    'LLVMAddReassociatePass': (None,
                               ['LLVMPassManagerRef']),
    'LLVMAddSCCPPass': (None,
                        ['LLVMPassManagerRef']),
    'LLVMAddScalarReplAggregatesPass': (None,
                                        ['LLVMPassManagerRef']),
    'LLVMAddScalarReplAggregatesPassSSA': (None,
                                           ['LLVMPassManagerRef']),
    'LLVMAddScalarReplAggregatesPassWithThreshold': (None,
                                                     ['LLVMPassManagerRef', ctypes.c_int]),
    'LLVMAddSimplifyLibCallsPass': (None,
                                    ['LLVMPassManagerRef']),
    'LLVMAddTailCallEliminationPass': (None,
                                       ['LLVMPassManagerRef']),
    'LLVMAddConstantPropagationPass': (None,
                                       ['LLVMPassManagerRef']),
    'LLVMAddDemoteRegisterToMemoryPass': (None,
                                          ['LLVMPassManagerRef']),
    'LLVMAddVerifierPass': (None,
                            ['LLVMPassManagerRef']),
    'LLVMAddCorrelatedValuePropagationPass': (None,
                                              ['LLVMPassManagerRef']),
    'LLVMAddEarlyCSEPass': (None,
                            ['LLVMPassManagerRef']),
    'LLVMAddLowerExpectIntrinsicPass': (None,
                                        ['LLVMPassManagerRef']),
    'LLVMAddTypeBasedAliasAnalysisPass': (None,
                                          ['LLVMPassManagerRef']),
    'LLVMAddBasicAliasAnalysisPass': (None,
                                      ['LLVMPassManagerRef']),
}

enum_declarations = {
}

