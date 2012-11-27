#===- context.py - Python Object Bindings --------------------*- python -*--===#
#
#                     The LLVM Compiler Infrastructure
#
# This file is distributed under the University of Illinois Open Source
# License. See LICENSE.TXT for details.
#
#===------------------------------------------------------------------------===#

from ..common import LLVMObject
from ..common import get_library


lib = get_library()

# @lib.c_name("LLVMContextRef")
# class Context(LLVMObject):
#     """LLVM state manager.

# A Context owns and manages the core "global" data of LLVM's core
# infrastructure, including the type and constant uniquing tables.

# The existence of these objects will most likely be transparent to most
# consumers of the Python bindings. However, they are exposed for
# advanced users to use, if needed.
# """

#     def __init__(self, context=None):
#         if context is None:
#             context = lib.LLVMContextCreate()
#             LLVMObject.__init__(self, context)
#         else:
#             LLVMObject.__init__(self, context)

#     def __dispose__(self):
#         #lib.LLVMContextDispose(self)
#         pass

#     @classmethod
#     def GetGlobalContext(cls):
#         c = Context(lib.LLVMGetGlobalContext())
#         c._self_owned = False
#         return c


@lib.c_name("LLVMContextRef")
class Context(LLVMObject):
    """LLVM state manager.

A Context owns and manages the core "global" data of LLVM's core
infrastructure, including the type and constant uniquing tables.

The existence of these objects will most likely be transparent to most
consumers of the Python bindings. However, they are exposed for
advanced users to use, if needed.
"""

    def __init__(self, ptr=None):
        """Create a new Context."""
        if ptr is None:
            ptr = lib.LLVMContextCreate()

        LLVMObject.__init__(self, ptr)

    def __dispose__(self):
        lib.LLVMContextDispose(self)

    @staticmethod
    def GetGlobalContext():
        return GlobalContext()


g_ctx = None
def GlobalContext():
    """Get a reference to the global context"""
    global g_ctx
    if g_ctx is None:
        ptr = lib.LLVMGetGlobalContext()
        g_ctx = Context(ptr=ptr)
        # Don't destroy the global context in __del__. Instead, let it persist
        # indefinitely.
        g_ctx._self_owned = False
    return g_ctx

