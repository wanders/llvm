##===- bindings/python/Makefile ----------------------------*- Makefile -*-===##
# 
#                     The LLVM Compiler Infrastructure
#
# This file is distributed under the University of Illinois Open Source
# License. See LICENSE.TXT for details.
# 
##===----------------------------------------------------------------------===##

LEVEL := ../..
include $(LEVEL)/Makefile.common


all::
	$(Echo) "Building python bindings (which is currently is a no-op)"


GEN_HDRS:=Disassembler.h Object.h Core.h BitReader.h BitWriter.h Analysis.h ExecutionEngine.h Transforms/PassManagerBuilder.h Transforms/IPO.h Transforms/Scalar.h Target.h TargetMachine.h

.PHONY: generate-in-src-dir
generate-in-src-dir:
	@for hdr in $(GEN_HDRS); do \
	echo Generating interface definition for $$hdr...; \
	PYTHONPATH=$(PROJ_SRC_ROOT)/tools/clang/bindings/python/ \
	LD_LIBRARY_PATH=$(SharedLibDir) \
	PROJ_SRC_ROOT=$(PROJ_SRC_ROOT) \
	python $(PROJ_SRC_DIR)/tools/generate-from-includes.py -std=c11 $(CPP.Flags) -I$(PROJ_SRC_ROOT)/tools/clang/lib/Headers/ $(PROJ_SRC_ROOT)/include/llvm-c/$$hdr >$(PROJ_SRC_DIR)/llvm/generated/`echo $$hdr | tr A-Z/ a-z_ | sed s/.h$$//`.py; \
	done



.PHONY: check-py-local
ifeq ($(NOSETESTS),)
check-py-local::
	@ $(ECHO) '+++ NOT running tests for python bindings +++'
	@ $(ECHO) '    because nosetests could not be found'
else
check-py-local::
	@ $(ECHO) '--- Running tests for python bindings ---'
	$(Verb) PYTHONPATH=$(PROJ_SRC_DIR) \
	        LD_LIBRARY_PATH=$(SharedLibDir):$$LD_LIBRARY_PATH \
	        PYTHONDONTWRITEBYTECODE=1 \
	        $(NOSETESTS) -v --with-cov --cover-erase --cover-package=llvm $(PROJ_SRC_DIR)/llvm/tests
endif


