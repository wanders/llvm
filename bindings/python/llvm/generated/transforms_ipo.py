#===-- Generated python interface definitions for 'IPO.h' ------------------===#
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
    'LLVMAddArgumentPromotionPass': (None,
                                     ['LLVMPassManagerRef']),
    'LLVMAddConstantMergePass': (None,
                                 ['LLVMPassManagerRef']),
    'LLVMAddDeadArgEliminationPass': (None,
                                      ['LLVMPassManagerRef']),
    'LLVMAddFunctionAttrsPass': (None,
                                 ['LLVMPassManagerRef']),
    'LLVMAddFunctionInliningPass': (None,
                                    ['LLVMPassManagerRef']),
    'LLVMAddAlwaysInlinerPass': (None,
                                 ['LLVMPassManagerRef']),
    'LLVMAddGlobalDCEPass': (None,
                             ['LLVMPassManagerRef']),
    'LLVMAddGlobalOptimizerPass': (None,
                                   ['LLVMPassManagerRef']),
    'LLVMAddIPConstantPropagationPass': (None,
                                         ['LLVMPassManagerRef']),
    'LLVMAddPruneEHPass': (None,
                           ['LLVMPassManagerRef']),
    'LLVMAddIPSCCPPass': (None,
                          ['LLVMPassManagerRef']),
    'LLVMAddInternalizePass': (None,
                               ['LLVMPassManagerRef', ctypes.c_uint]),
    'LLVMAddStripDeadPrototypesPass': (None,
                                       ['LLVMPassManagerRef']),
    'LLVMAddStripSymbolsPass': (None,
                                ['LLVMPassManagerRef']),
}

enum_declarations = {
}

