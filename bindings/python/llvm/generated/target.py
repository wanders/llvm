#===-- Generated python interface definitions for 'Target.h' ---------------===#
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
    'LLVMInitializeAllTargetInfos': (None,
                                     []),
    'LLVMInitializeAllTargets': (None,
                                 []),
    'LLVMInitializeAllTargetMCs': (None,
                                   []),
    'LLVMInitializeAllAsmPrinters': (None,
                                     []),
    'LLVMInitializeAllAsmParsers': (None,
                                    []),
    'LLVMInitializeAllDisassemblers': (None,
                                       []),
    'LLVMInitializeNativeTarget': ('LLVMBool',
                                   []),
    'LLVMCreateTargetData': (c_object_p,
                             [ctypes.c_char_p]),
    'LLVMAddTargetData': (None,
                          ['LLVMTargetDataRef', 'LLVMPassManagerRef']),
    'LLVMAddTargetLibraryInfo': (None,
                                 ['LLVMTargetLibraryInfoRef', 'LLVMPassManagerRef']),
    'LLVMCopyStringRepOfTargetData': (ctypes.POINTER(ctypes.c_char),
                                      ['LLVMTargetDataRef']),
    'LLVMByteOrder': ('LLVMByteOrdering',
                      ['LLVMTargetDataRef']),
    'LLVMPointerSize': (ctypes.c_uint,
                        ['LLVMTargetDataRef']),
    'LLVMPointerSizeForAS': (ctypes.c_uint,
                             ['LLVMTargetDataRef', ctypes.c_uint]),
    'LLVMIntPtrType': (c_object_p,
                       ['LLVMTargetDataRef']),
    'LLVMIntPtrTypeForAS': (c_object_p,
                            ['LLVMTargetDataRef', ctypes.c_uint]),
    'LLVMSizeOfTypeInBits': (ctypes.c_ulonglong,
                             ['LLVMTargetDataRef', 'LLVMTypeRef']),
    'LLVMStoreSizeOfType': (ctypes.c_ulonglong,
                            ['LLVMTargetDataRef', 'LLVMTypeRef']),
    'LLVMABISizeOfType': (ctypes.c_ulonglong,
                          ['LLVMTargetDataRef', 'LLVMTypeRef']),
    'LLVMABIAlignmentOfType': (ctypes.c_uint,
                               ['LLVMTargetDataRef', 'LLVMTypeRef']),
    'LLVMCallFrameAlignmentOfType': (ctypes.c_uint,
                                     ['LLVMTargetDataRef', 'LLVMTypeRef']),
    'LLVMPreferredAlignmentOfType': (ctypes.c_uint,
                                     ['LLVMTargetDataRef', 'LLVMTypeRef']),
    'LLVMPreferredAlignmentOfGlobal': (ctypes.c_uint,
                                       ['LLVMTargetDataRef', 'LLVMValueRef']),
    'LLVMElementAtOffset': (ctypes.c_uint,
                            ['LLVMTargetDataRef', 'LLVMTypeRef', ctypes.c_ulonglong]),
    'LLVMOffsetOfElement': (ctypes.c_ulonglong,
                            ['LLVMTargetDataRef', 'LLVMTypeRef', ctypes.c_uint]),
    'LLVMDisposeTargetData': (None,
                              ['LLVMTargetDataRef']),
}

enum_declarations = {
    'LLVMByteOrdering': {
                        'LLVMBigEndian': 0,
                        'LLVMLittleEndian': 1,
    },

}

