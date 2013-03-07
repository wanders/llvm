#===- disassembler.py - Python LLVM Bindings -----------------*- python -*--===#
#
#                     The LLVM Compiler Infrastructure
#
# This file is distributed under the University of Illinois Open Source
# License. See LICENSE.TXT for details.
#
#===------------------------------------------------------------------------===#


from .common import LLVMObject
from .common import get_library

lib = get_library()

@lib.c_name("LLVMPassManagerRef")
class _PassManagerBase(LLVMObject):
    def __dispose__(self):
        lib.LLVMDisposePassManager(self)

class ModulePassManager(_PassManagerBase):
    def __init__(self):
        LLVMObject.__init__(self, ptr=lib.LLVMCreatePassManager())

    def add_passes_from_builder(self, builder):
        lib.LLVMPassManagerBuilderPopulateModulePassManager(builder, self)

    def run(self, module):
        return lib.LLVMRunPassManager(self, module)

    def add_argument_promotion_pass(self):
        lib.LLVMAddArgumentPromotionPass(self)
    def add_constant_merge_pass(self):
        lib.LLVMAddConstantMergePass(self)
    def add_dead_arg_elimination_pass(self):
        lib.LLVMAddDeadArgEliminationPass(self)
    def add_function_attrs_pass(self):
        lib.LLVMAddFunctionAttrsPass(self)
    def add_function_inlining_pass(self):
        lib.LLVMAddFunctionInliningPass(self)
    def add_always_inliner_pass(self):
        lib.LLVMAddAlwaysInlinerPass(self)
    def add_global_dce_pass(self):
        lib.LLVMAddGlobalDCEPass(self)
    def add_global_optimizer_pass(self):
        lib.LLVMAddGlobalOptimizerPass(self)
    def add_i_p_constant_propagation_pass(self):
        lib.LLVMAddIPConstantPropagationPass(self)
    def add_prune_eh_pass(self):
        lib.LLVMAddPruneEHPass(self)
    def add_ipsccp_pass(self):
        lib.LLVMAddIPSCCPPass(self)
    def add_internalize_pass(self, AllButMain):
        lib.LLVMAddInternalizePass(self, AllButMain)
    def add_strip_dead_prototypes_pass(self):
        lib.LLVMAddStripDeadPrototypesPass(self)
    def add_strip_symbols_pass(self):
        lib.LLVMAddStripSymbolsPass(self)


class FunctionPassManager(_PassManagerBase):
    def __init__(self, module):
        LLVMObject.__init__(self, ptr=lib.LLVMCreateFunctionPassManagerForModule(module))

    def add_passes_from_builder(self, builder):
        lib.LLVMPassManagerBuilderPopulateFunctionPassManager(builder, self)

    def init(self):
        return lib.LLVMInitializeFunctionPassManager(self)

    def run(self, f):
        return lib.LLVMRunFunctionPassManager(self, f)

    def finalize(self):
        return lib.LLVMFinalizeFunctionPassManager(self)

@lib.c_name("LLVMPassManagerBuilderRef")
class PassManagerBuilder(LLVMObject):
    _optlevel = 2 # default

    def __init__(self):
        LLVMObject.__init__(self, ptr=lib.LLVMPassManagerBuilderCreate())

    def __dispose__(self):
        return lib.LLVMPassManagerBuilderDispose(self)

    def _set_optlevel(self, val):
        lib.LLVMPassManagerBuilderSetOptLevel(self, val)
        self._optlevel = val

    optlevel = property(lambda self: self._optlevel,
                        _set_optlevel)

