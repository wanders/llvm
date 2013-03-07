#===- common.py - Python LLVM Bindings -----------------------*- python -*--===#
#
#                     The LLVM Compiler Infrastructure
#
# This file is distributed under the University of Illinois Open Source
# License. See LICENSE.TXT for details.
#
#===------------------------------------------------------------------------===#

from ctypes import POINTER
from ctypes import c_void_p
from ctypes import cdll

from weakref import WeakValueDictionary

import warnings

import ctypes.util
import platform

# LLVM_VERSION: sync with PACKAGE_VERSION in autoconf/configure.ac and CMakeLists.txt
#               but leave out the 'svn' suffix.
LLVM_VERSION = '3.4'

__all__ = [
    'c_object_p',
    'get_library',
]

c_object_p = POINTER(c_void_p)

def _object_p_to_key(o):
    return ctypes.cast(o, ctypes.c_void_p).value

def create_c_object_p_array(contents=None, ensure_type=None):
    if ensure_type is not None:
        if not all(isinstance(e, ensure_type) for e in contents):
            raise TypeError("Expected %s in sequence" % ensure_type.__name__)
    typ = c_object_p * len(contents)
    return typ(*[e.from_param() for e in contents])

def create_empty_c_object_p_array(size):
    typ = c_object_p * size
    return typ()

class LLVMObject(object):
    """Base class for objects that are backed by an LLVM data structure.

    This class should never be instantiated outside of this package.
    """
    def __init__(self, ptr, ownable=True):
        assert isinstance(ptr, c_object_p)

        self._ptr = self._as_parameter_ = ptr

        self._self_owned = True
        self._ownable = ownable

        self._owned_objects = []

        LLVMObject._unaliasing[_object_p_to_key(ptr)] = self

    def __dispose__(self):
        pass

    def take_ownership(self, obj):
        """Take ownership of another object.

        When you take ownership of another object, you are responsible for
        destroying that object. In addition, a reference to that object is
        placed inside this object so the Python garbage collector will not
        collect the object while it is still alive in libLLVM.

        This method should likely only be called from within modules inside
        this package.
        """
        assert isinstance(obj, LLVMObject)

        self._owned_objects.append(obj)
        obj._self_owned = False

    def from_param(self):
        """ctypes function that converts this object to a function parameter."""
        return self._as_parameter_

    def __del__(self):
        if not hasattr(self, '_self_owned'):
            return

        if self._self_owned:
            self.__dispose__()

    _unaliasing = WeakValueDictionary()
    @classmethod
    def _from_ptr(cls, ptr):
        if not ptr:
            return None
        key = _object_p_to_key(ptr)
        try:
            return LLVMObject._unaliasing[key]
        except KeyError:
            return cls(ptr=ptr)


class LLVMEnum(int):
    """
    Base class for enum types. Use combined with lib.c_enum decorator.
    """
    _INCLUDE_NUM = True

    def from_param(self):
        return self

    def __str__(self):
        name = "%s.%s" % (self.__class__.__name__, self._names.get(self, "?"))
        if self._INCLUDE_NUM:
            return "%s(%d)" % (name, int(self))
        return name

    __repr__ = __str__


class CachedProperty(object):
    """Decorator that caches the result of a property lookup.

    This is a useful replacement for @property. It is recommended to use this
    decorator on properties that invoke C API calls for which the result of the
    call will be idempotent.
    """
    def __init__(self, wrapped):
        self.wrapped = wrapped
        try:
            self.__doc__ = wrapped.__doc__
        except: # pragma: no cover
            pass

    def __get__(self, instance, instance_type=None):
        if instance is None:
            return self

        value = self.wrapped(instance)
        setattr(instance, self.wrapped.__name__, value)

        return value


def load_library():
    """Obtain a reference to the llvm library."""

    # On Linux, ctypes.cdll.LoadLibrary() respects LD_LIBRARY_PATH
    # while ctypes.util.find_library() doesn't.
    # See http://docs.python.org/2/library/ctypes.html#finding-shared-libraries
    #
    # To make it possible to run the unit tests without installing the LLVM shared
    # library into a default linker search path.  Always Try ctypes.cdll.LoadLibrary()
    # with all possible library names first, then try ctypes.util.find_library().

    names = ['LLVM-' + LLVM_VERSION, 'LLVM-' + LLVM_VERSION + 'svn']
    t = platform.system()
    if t == 'Darwin':
        pfx, ext = 'lib', '.dylib'
    elif t == 'Windows':
        pfx, ext = '', '.dll'
    else:
        pfx, ext = 'lib', '.so'

    for i in names:
        try:
            lib = cdll.LoadLibrary(pfx + i + ext)
        except OSError:
            pass
        else:
            return lib

    for i in names:
        t = ctypes.util.find_library(i)
        if t:
            return cdll.LoadLibrary(t)
    raise Exception('LLVM shared library not found!')

class OnDemandRegisteredDeclarationsLibrary(object):
    """
    Wrapper over a ctypes library.

    Reads declarations from the generated files in `llvm.generated.*`
    first time a function is called.

    Use the `c_name` and `c_enum` decorators to register types on the lib.
    """

    BASE = "llvm.generated."
    MODULES = ('object', 'disassembler', 'core', 'bitreader', 'analysis', 'executionengine', 'transforms_passmanagerbuilder', 'transforms_ipo')

    def __init__(self):
        self.lib = None
        self.types = {}
        self.funcs = {}
        self.defs = {}
        self.edefs = {}
        self.types['LLVMBool'] = ctypes.c_int

        for n in self.MODULES:
            m = __import__(self.BASE+n,
                           fromlist=['function_declarations',
                                     'enum_declarations'],
                           level=0)
            self.defs.update(m.function_declarations)
            self.edefs.update(m.enum_declarations)

    def c_name(self, cname):
        def _(klass):
            self.types[cname] = klass
            return klass
        return _

    def c_enum(self, enumname, stripprefix="", stripsuffix=""):
        enumdef = self.edefs[enumname]
        enumdef_stripped = {}
        for k,v in enumdef.iteritems():
            assert k.startswith(stripprefix)
            assert k.endswith(stripsuffix)
            if stripprefix:
                k = k[len(stripprefix):]
            if stripsuffix:
                k = k[:-len(stripsuffix)]
            enumdef_stripped[k] = v

        def _(klass):
            klass._names = dict((v,k) for k,v in enumdef_stripped.iteritems())
            for k,v in enumdef_stripped.iteritems():
                setattr(klass, k, klass(v))
            self.types[enumname] = klass
            return klass
        return _

    def __getattr__(self, attr):
        try:
            return self.funcs[attr]
        except KeyError:
            pass

        if self.lib is None:
            self.lib = load_library()

        r = getattr(self.lib, attr)
        self.funcs[attr] = r

        def resolvetype(t):
            if isinstance(t, basestring):
                return self.types[t]
            return t

        if attr in self.defs:
            rt, at = self.defs[attr]
            rt = resolvetype(rt)
            at = map(resolvetype, at)

            r.restype = rt
            r.argtypes = at

        else:
            warnings.warn("Function %s called without prototype" % repr(attr),
                          UserWarning, stacklevel=2)

        return r

_lib = None
def get_library():
    """Obtain a reference to the llvm library."""
    global _lib

    if _lib is not None:
        return _lib

    _lib = OnDemandRegisteredDeclarationsLibrary()
    return _lib
