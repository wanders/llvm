#===-- Generated python interface definitions for 'PassManagerBuilder.h' ---===#
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
    'LLVMPassManagerBuilderCreate': (c_object_p,
                                     []),
    'LLVMPassManagerBuilderDispose': (None,
                                      ['LLVMPassManagerBuilderRef']),
    'LLVMPassManagerBuilderSetOptLevel': (None,
                                          ['LLVMPassManagerBuilderRef', ctypes.c_uint]),
    'LLVMPassManagerBuilderSetSizeLevel': (None,
                                           ['LLVMPassManagerBuilderRef', ctypes.c_uint]),
    'LLVMPassManagerBuilderSetDisableUnitAtATime': (None,
                                                    ['LLVMPassManagerBuilderRef', 'LLVMBool']),
    'LLVMPassManagerBuilderSetDisableUnrollLoops': (None,
                                                    ['LLVMPassManagerBuilderRef', 'LLVMBool']),
    'LLVMPassManagerBuilderSetDisableSimplifyLibCalls': (None,
                                                         ['LLVMPassManagerBuilderRef', 'LLVMBool']),
    'LLVMPassManagerBuilderUseInlinerWithThreshold': (None,
                                                      ['LLVMPassManagerBuilderRef', ctypes.c_uint]),
    'LLVMPassManagerBuilderPopulateFunctionPassManager': (None,
                                                          ['LLVMPassManagerBuilderRef', 'LLVMPassManagerRef']),
    'LLVMPassManagerBuilderPopulateModulePassManager': (None,
                                                        ['LLVMPassManagerBuilderRef', 'LLVMPassManagerRef']),
    'LLVMPassManagerBuilderPopulateLTOPassManager': (None,
                                                     ['LLVMPassManagerBuilderRef', 'LLVMPassManagerRef', 'LLVMBool', 'LLVMBool']),
}

enum_declarations = {
}

