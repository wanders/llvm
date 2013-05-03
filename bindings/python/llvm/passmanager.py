#===- passmanager.py - Python LLVM Bindings ------------------*- python -*--===#
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


    def add_aggressive_DCE_pass(self):
        lib.LLVMAddAggressiveDCEPass(self)
    def add_CFG_simplification_pass(self):
        lib.LLVMAddCFGSimplificationPass(self)
    def add_dead_store_elimination_pass(self):
        lib.LLVMAddDeadStoreEliminationPass(self)
    def add_GVN_pass(self):
        lib.LLVMAddGVNPass(self)
    def add_induction_variable_simplify_pass(self):
        lib.LLVMAddIndVarSimplifyPass(self)
    def add_instruction_combining_pass(self):
        lib.LLVMAddInstructionCombiningPass(self)
    def add_jump_threading_pass(self):
        lib.LLVMAddJumpThreadingPass(self)
    def add_LICM_pass(self):
        """Loop Invariant Code Motion"""
        lib.LLVMAddLICMPass(self)
    def add_loop_deletion_pass(self):
        lib.LLVMAddLoopDeletionPass(self)
    def add_loop_idiom_pass(self):
        lib.LLVMAddLoopIdiomPass(self)
    def add_loop_rotate_pass(self):
        lib.LLVMAddLoopRotatePass(self)
    def add_loop_unroll_pass(self):
        lib.LLVMAddLoopUnrollPass(self)
    def add_loop_unswitch_pass(self):
        lib.LLVMAddLoopUnswitchPass(self)
    def add_memcpy_opt_pass(self):
        lib.LLVMAddMemCpyOptPass(self)
    def add_promote_memory_to_register_pass(self):
        lib.LLVMAddPromoteMemoryToRegisterPass(self)
    def add_reassociate_pass(self):
        lib.LLVMAddReassociatePass(self)
    def add_SCCP_pass(self):
        """Sparse Conditional Constant Propagation"""
        lib.LLVMAddSCCPPass(self)
    def add_scalar_repl_aggregates_pass(self, threshold=None):
        if threshold is None:
            lib.LLVMAddScalarReplAggregatesPass(self)
        else:
            lib.LLVMAddScalarReplAggregatesPassWithThreshold(self, threshold)
    def add_scalar_repl_aggregates_SSA_pass(self):
        lib.LLVMAddScalarReplAggregatesPassSSA(self)
    def add_simplify_lib_calls_pass(self):
        lib.LLVMAddSimplifyLibCallsPass(self)
    def add_tail_call_elimination_pass(self):
        lib.LLVMAddTailCallEliminationPass(self)
    def add_constant_propagation_pass(self):
        lib.LLVMAddConstantPropagationPass(self)
    def add_demote_register_to_memory_pass(self):
        lib.LLVMAddDemoteRegisterToMemoryPass(self)
    def add_verifier_pass(self):
        lib.LLVMAddVerifierPass(self)
    def add_correlated_value_propagation_pass(self):
        lib.LLVMAddCorrelatedValuePropagationPass(self)
    def add_early_CSE_pass(self):
        lib.LLVMAddEarlyCSEPass(self)
    def add_lower_expect_intrinsic_pass(self):
        lib.LLVMAddLowerExpectIntrinsicPass(self)
    def add_type_based_alias_analysis_pass(self):
        lib.LLVMAddTypeBasedAliasAnalysisPass(self)
    def add_basic_alias_analysis_pass(self):
        lib.LLVMAddBasicAliasAnalysisPass(self)



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

