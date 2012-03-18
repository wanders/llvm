#===- execution.py - Python LLVM Bindings --------------------*- python -*--===#
#
#                     The LLVM Compiler Infrastructure
#
# This file is distributed under the University of Illinois Open Source
# License. See LICENSE.TXT for details.
#
#===------------------------------------------------------------------------===#

from ctypes import POINTER
from ctypes import byref
from ctypes import c_bool
from ctypes import c_char_p
from ctypes import c_double
from ctypes import c_int
from ctypes import c_uint
from ctypes import c_ulonglong
from ctypes import c_void_p

from .common import LLVMObject
from .common import c_object_p
from .common import get_library
from .common import register_apis
from .modules import Module
from .types import Type
from .values import Function
from .values import GlobalValue

lib = get_library()

class GenericValue(LLVMObject):
    def __init__(self):
        LLVMObject.__init__(self)

class ExecutionEngine(LLVMObject):
    """Provides an interface for executing LLVM code.

    This class corresponds to the llvm::ExecutionEngine C++ class.
    """

    def __init__(self, module, interpreter=False, jit=False,
                 jit_optimization=0):
        """Create a new ExecutionEngine instance.

        ExecutionEngines are bound to a single Module instance. When the
        ExecutionEngine is created, either an interpreter or a JIT may be
        created. The default behavior is to let LLVM decide. LLVM will try
        to construct a JIT. If that fails, it will fall back to an interpreter.

        If interpreter is True force LLVM to create an interpeter. If jit is
        True, force LLVM to create a JIT.

        Created JITs have different optimization levels. The jit_optimization
        argument defines a numeric optimization level. This integer value
        roughly corresponds to the -O<N> flags to a compiler. e.g. 0 is no
        optimization and 3 (-O3) is full optimization.

        If interpreter creation fails, an exception will be raised.
        """
        assert isinstance(module, Module)

        ptr = c_object_p()
        error = c_char_p()

        fn = lib.LLVMCreateExecutionEngineForModule
        args = [byref(ptr), module, byref(error)]

        if interpreter:
            fn = lib.LLVMCreateInterpreterForModule

        if jit:
            fn = lib.LLVMCreateJITCompilerForModule
            args.insert(2, jit_optimization)

        if fn(*args):
            raise Exception('Could not create ExecutionEngine: %s' %
                    error.value)

        LLVMObject.__init__(self, ptr, disposer=lib.LLVMDisposeExecutionEngine)

        # The ExecutionEngine destructor deletes all modules. Prevent double
        # free in Python by taking ownership of the module.
        self.take_ownership(module)

        self._set_ref('context', module.context)

    def add_module(self, module):
        """Add a Module to this ExecutionEngine."""

        lib.LLVMAddModule(self, module)
        self.take_ownership(module)

    def remove_module(self, module):
        """Remove a Module from this ExecutionEngine."""

        # The C API is a little weird. The OutError parameter isn't populated
        # and the function always returns 0. Also, the C API re-wraps the
        # module. However, in C++ land, the original module is operated on.
        # Since both wrapped C modules point to the same underlying
        # llvm::Module, we could just preserve the old wrapper. Instead, we
        # play it safe and switch out the old pointer from inside the module.
        # This is hacky but does buffer us slightly from changes in the C API.
        # Of course, if the C API starts returning a new llvm::Module instance,
        # this approach will fail hard.

        ptr = c_object_p()
        error = c_char_p()

        assert not lib.LLVMRemoveModule(self, module, byref(ptr), byref(error))
        module._set_pointer(ptr)
        self.release_ownership(module)

    def run_static_constructors(self):
        """Runs static constructors for all registered modules."""

        lib.LLVMRunStaticConstructors(self)

    def run_static_destructors(self):
        """Runs static destructors for all registered modules."""

        lib.LLVMRunStaticDestructors(self)

    def run_main(self, fn='main', argv=None, env=None):
        """Run a function as the main function.

        This is effectively invoking the int main() function in a program.
        The big difference is you can optionally select which function to
        run.

        Is called without any arguments, we will search for a function named
        'main' and call it with an empty argument list and an empty
        environment.

        The signature of the called function must be valid. Basically, it can
        have up to 3 parameters. The first must be a 32 bit integer. The
        second and third must be pointers. Finally, the return type must be a
        32 bit integer or void.

        If the function does not take enough parameters to receive arguments
        or environment variables, these are silently dropped on the floor.

        Arguments:

        fn - The function to call. This can be a llvm.values.Function instance
          or a str. If a str, we will search for a function by that name and
          run that.
        argv - Iterable of str to pass as arguments. Remember that the first
          argument is the program's name.
        env - Dictionary of environment variables.
        """
        if isinstance(fn, str):
            name = fn
            fn = self.find_function(name)
            if not fn:
                raise Exception('Could not find function: %s' % name)

        assert isinstance(fn, Function)

        if argv is None:
            argv = []

        if env is None:
            env = {}

        out_args = c_char_p * len(argv)
        for i in range(0, len(argv)):
            out_args[i] = argv[i]

        out_env = c_char_p * (len(env) + 1)

        i = 0
        for k, v in env.iteritems():
            out_env[i] = '%s=%s' % ( k, v )
            i += 1
        out_env[i] = None

        import pdb; pdb.set_trace()

    def find_function(self, name):
        """Find a function with the given name.

        This attempts to find a function with the given str name in the
        ExecutionEngine. If the function is found, an llvm.values.Function will
        be returned. If not, None will be returned.
        """
        ptr = c_object_p()

        if lib.LLVMFindFunction(self, name, byref(ptr)):
            return None

        return Function(ptr, context=self._get_ref('context'))

apis = {
    # Generic Values.
    'LLVMDisposeGenericValue': (None, [GenericValue]),
    'LLVMGenericValueIntWidth': (c_uint, [GenericValue]),
    'LLVMGenericValueToFloat': (c_double, [Type, GenericValue]),
    'LLVMGenericValueToInt': (c_ulonglong, [GenericValue, c_bool]),
    'LLVMGenericValueToPointer': (c_void_p, [GenericValue]),
    'LLVMCreateGenericValueOfFloat': (c_object_p, [Type, c_double]),
    'LLVMCreateGenericValueOfInt': (c_object_p, [Type, c_ulonglong, c_bool]),
    'LLVMCreateGenericValueOfPointer': (c_object_p, [c_void_p]),

    # Execution Engine.
    'LLVMAddGlobalMapping': (None, [ExecutionEngine, GlobalValue, c_void_p]),
    'LLVMAddModule': (None, [ExecutionEngine, Module]),
    'LLVMCreateExecutionEngineForModule': (bool, [POINTER(c_object_p), Module,
        POINTER(c_char_p)]),
    'LLVMCreateInterpreterForModule': (bool, [POINTER(c_object_p), Module,
        POINTER(c_char_p)]),
    'LLVMCreateJITCompilerForModule': (bool, [POINTER(c_object_p), Module,
        c_uint, POINTER(c_char_p)]),
    'LLVMDisposeExecutionEngine': (None, [ExecutionEngine]),
    'LLVMFindFunction': (None, [ExecutionEngine, c_char_p,
        POINTER(c_object_p)]),
    'LLVMFreeMachineCodeForFunction': (None, [ExecutionEngine, Function]),
    'LLVMGetExecutionEngineTargetData': (c_object_p, [ExecutionEngine]),
    'LLVMGetPointerToGlobal': (c_void_p, [ExecutionEngine, GlobalValue]),
    'LLVMRemoveModule': (bool, [ExecutionEngine, Module, POINTER(c_object_p),
        POINTER(c_char_p)]),
    'LLVMRunFunctionAsMain': (c_int, [ExecutionEngine, Function, c_uint,
        POINTER(c_char_p), POINTER(c_char_p)]),
    'LLVMRunFunction': (c_object_p, [ExecutionEngine, Function, c_uint,
        POINTER(c_object_p)]),
    'LLVMRecompileAndRelinkFunction': (c_void_p, [ExecutionEngine, Function]),
    'LLVMRunStaticConstructors': (None, [ExecutionEngine]),
    'LLVMRunStaticDestructors': (None, [ExecutionEngine]),
}

register_apis(apis, lib)
