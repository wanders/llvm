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


