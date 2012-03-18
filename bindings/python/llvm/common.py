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

import ctypes.util

__all__ = [
    'c_object_p',
    'find_library',
    'get_library',
    'register_apis',
]

c_object_p = POINTER(c_void_p)

class LLVMObject(object):
    """Base class for objects that are backed by an LLVM data structure.

    This class should never be instantiated outside of this package.
    """
    def __init__(self, ptr=None, ownable=True, disposer=None):
        if ptr:
            self._set_pointer(ptr)

        self._self_owned = True
        self._ownable = ownable
        self._disposer = disposer

        self._owned_objects = []
        self._references = {}

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

    def release_ownership(self, obj):
        """Release ownership of another object.

        This is the opposite of take_owernship(). It is called rarely in
        comparison to take_ownership().
        """

        # Yes, this will throw a ValueError if obj isn't found. This is
        # intentional, as release_ownership() should only be called exactly
        # once after take_ownership() is.
        self._owned_objects.remove(obj)
        obj._self_owned = True

    def _set_ref(self, name, obj):
        """Create a reference to another object in this one.

        This method has 2 main purposes:

          1) Store a reference to another object so it can be used as part of a
             future API call.
          2) Store a reference to a parent object so the parent object doesn't
             lose all references and become garbage collected, possibly freeing
             resources used by this object.

        The focus of this API is internal and very low level. It is highly
        unlikely you will need to use it from external code.
        """
        if name in self._references:
            raise Exception('Reference already stored: %s' % name)

        self._references[name] = obj

    def _get_ref(self, name):
        """Obtain a previously stored object from the reference table.

        This complements create_reference(). You likely shouldn't be using this
        from external code.
        """
        return self._references[name]

    def _set_pointer(self, ptr):
        """Switch out the internal pointer to another one.

        If you find yourself calling this, please document at the call site
        why.
        """
        assert isinstance(ptr, c_object_p)
        self._ptr = self._as_parameter_ = ptr

    def from_param(self):
        """ctypes function that converts this object to a function parameter."""
        return self._as_parameter_

    def __del__(self):
        if not hasattr(self, '_self_owned') or not hasattr(self, '_disposer'):
            return

        if self._self_owned and self._disposer:
            self._disposer(self)

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

def find_library():
    # FIXME should probably have build system define absolute path of shared
    # library at install time.
    for lib in ['LLVM-3.1svn', 'libLLVM-3.1svn', 'LLVM', 'libLLVM']:
        result = ctypes.util.find_library(lib)
        if result:
            return result

    return None

lib = None

def get_library(fresh=False):
    """Obtain a reference to the llvm library."""
    global lib

    if not fresh and lib:
        return lib

    l = find_library()
    if not l:
        raise Exception('LLVM shared library not found!')

    result = cdll.LoadLibrary(l)
    lib = result
    return result

def register_apis(apis, library):
    """Register APIs with a libLLVM ctypes library instance.

    This takes a dictionary of str C function names to 2-tuples. The first
    element in the tuple is the return value of the function, or None if it
    is void. The second element is an array of the argument types to the
    function.

    This function likely won't be called outside of this package.
    """
    for name, (return_type, arguments) in apis.iteritems():
        fn = getattr(library, name)

        if len(arguments) > 0:
            fn.argtypes = arguments

        if return_type is not None:
            fn.restype = return_type
