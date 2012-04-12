#===- object.py - Python Object Bindings --------------------*- python -*--===#
#
#                     The LLVM Compiler Infrastructure
#
# This file is distributed under the University of Illinois Open Source
# License. See LICENSE.TXT for details.
#
#===------------------------------------------------------------------------===#

r"""
Object File Interface
=====================

This module provides an interface for reading information from object files
(e.g. binary executables and libraries).

Using this module, you can obtain information about an object file's sections,
symbols, and relocations. These are represented by the classes :class:`ObjectFile`,
:class:`Section`, :class:`Symbol`, and :class:`Relocation`, respectively.

Usage
-----

The only way to use this module is to start by creating an :class:`ObjectFile`. You can
create an ObjectFile by loading a file (specified by its path) or by creating a
:class:`llvm.core.MemoryBuffer` and loading that.

Once you have an object file, you can inspect its sections and symbols
directly by calling :meth:`~ObjectFile.get_sections` and
:meth:`~ObjectFile.get_symbols` respectively. To inspect
relocations, call :meth:`~Section.get_relocations` on a
:class:`Section` instance.

Iterator Interface
------------------

The LLVM bindings expose iteration over sections, symbols, and relocations in a
way that only allows one instance to be operated on at a single time. This is
slightly annoying from a Python perspective, as it isn't very Pythonic to have
objects that "expire" but are still active from a dynamic language.

To aid working around this limitation, each Section, Symbol, and Relocation
instance caches its properties after first access. So, if the underlying
iterator is advanced, the properties can still be obtained provided they have
already been retrieved.

In addition, we also provide a "cache" method on each class to cache all
available data. You can call this on each obtained instance. Or, you can pass
cache=True to the appropriate get_XXX() method to have this done for you.

Here are some examples on how to perform iteration:

.. code-block:: python

    obj = ObjectFile(filename='/bin/ls')

    # This is OK. Each Section is only accessed inside its own iteration slot.
    section_names = []
    for section in obj.get_sections():
        section_names.append(section.name)

    # This is NOT OK. You perform a lookup after the object has expired.
    symbols = list(obj.get_symbols())
    for symbol in symbols:
        print symbol.name # This raises because the object has expired.

    # In this example, we mix a working and failing scenario.
    symbols = []
    for symbol in obj.get_symbols():
        symbols.append(symbol)
        print symbol.name

    for symbol in symbols:
        print symbol.name # OK
        print symbol.address # NOT OK. We didn't look up this property before.

    # Cache everything up front.
    symbols = list(obj.get_symbols(cache=True))
    for symbol in symbols:
        print symbol.name # OK

"""

from .common import CachedProperty
from .common import LLVMObject
from .common import c_object_p
from .common import get_library
from .core.memorybuffer import MemoryBuffer

from ctypes import string_at

__all__ = [
    "lib",
    "ObjectFile",
    "Relocation",
    "Section",
    "Symbol",
]

lib = get_library()

@lib.c_name("LLVMObjectFileRef")
class ObjectFile(LLVMObject):
    """Represents an object/binary file."""

    def __init__(self, filename=None, contents=None):
        """Construct an instance from a filename or binary data.

        filename must be a path to a file that can be opened with open().
        contents can be either a native Python buffer type (like str) or a
        llvm.core.MemoryBuffer instance.
        """
        if contents:
            assert isinstance(contents, MemoryBuffer)

        if filename is not None:
            contents = MemoryBuffer(filename=filename)

        if contents is None:
            raise Exception('No input found.')

        ptr = lib.LLVMCreateObjectFile(contents)
        LLVMObject.__init__(self, ptr)
        self.take_ownership(contents)

    def __dispose__(self):
        lib.LLVMDisposeObjectFile(self)

    def get_sections(self, cache=False):
        """Obtain the sections in this object file.

        This is a generator for llvm.object.Section instances.

        Sections are exposed as limited-use objects. See the module's
        documentation on iterators for more.
        """
        sections = lib.LLVMGetSections(self)
        last = None
        while True:
            if lib.LLVMIsSectionIteratorAtEnd(self, sections):
                break

            last = Section(sections)
            if cache:
                last.cache()

            yield last

            lib.LLVMMoveToNextSection(sections)
            last.expire()

        if last is not None:
            last.expire()

        lib.LLVMDisposeSectionIterator(sections)

    def get_symbols(self, cache=False):
        """Obtain the symbols in this object file.

        This is a generator for llvm.object.Symbol instances.

        Each Symbol instance is a limited-use object. See this module's
        documentation on iterators for more.
        """
        symbols = lib.LLVMGetSymbols(self)
        last = None
        while True:
            if lib.LLVMIsSymbolIteratorAtEnd(self, symbols):
                break

            last = Symbol(symbols, self)
            if cache:
                last.cache()

            yield last

            lib.LLVMMoveToNextSymbol(symbols)
            last.expire()

        if last is not None:
            last.expire()

        lib.LLVMDisposeSymbolIterator(symbols)

class Section(LLVMObject):
    """Represents a section in an object file."""

    def __init__(self, ptr):
        """Construct a new section instance.

        Section instances can currently only be created from an ObjectFile
        instance. Therefore, this constructor should not be used outside of
        this module.
        """
        LLVMObject.__init__(self, ptr)

        self.expired = False

    @CachedProperty
    def name(self):
        """Obtain the string name of the section.

        This is typically something like '.dynsym' or '.rodata'.
        """
        if self.expired:
            raise Exception('Section instance has expired.')

        return string_at(lib.LLVMGetSectionName(self))

    @CachedProperty
    def size(self):
        """The size of the section, in long bytes."""
        if self.expired:
            raise Exception('Section instance has expired.')

        return lib.LLVMGetSectionSize(self)

    @CachedProperty
    def contents(self):
        if self.expired:
            raise Exception('Section instance has expired.')

        return string_at(lib.LLVMGetSectionContents(self), self.size)

    @CachedProperty
    def address(self):
        """The address of this section, in long bytes."""
        if self.expired:
            raise Exception('Section instance has expired.')

        return lib.LLVMGetSectionAddress(self)

    def has_symbol(self, symbol):
        """Returns whether a Symbol instance is present in this Section."""
        if self.expired:
            raise Exception('Section instance has expired.')

        assert isinstance(symbol, Symbol)
        return lib.LLVMGetSectionContainsSymbol(self, symbol)

    def get_relocations(self, cache=False):
        """Obtain the relocations in this Section.

        This is a generator for llvm.object.Relocation instances.

        Each instance is a limited used object. See this module's documentation
        on iterators for more.
        """
        if self.expired:
            raise Exception('Section instance has expired.')

        relocations = lib.LLVMGetRelocations(self)
        last = None
        while True:
            if lib.LLVMIsRelocationIteratorAtEnd(self, relocations):
                break

            last = Relocation(relocations)
            if cache:
                last.cache()

            yield last

            lib.LLVMMoveToNextRelocation(relocations)
            last.expire()

        if last is not None:
            last.expire()

        lib.LLVMDisposeRelocationIterator(relocations)

    def cache(self):
        """Cache properties of this Section.

        This can be called as a workaround to the single active Section
        limitation. When called, the properties of the Section are fetched so
        they are still available after the Section has been marked inactive.
        """
        getattr(self, 'name')
        getattr(self, 'size')
        getattr(self, 'contents')
        getattr(self, 'address')

    def expire(self):
        """Expire the section.

        This is called internally by the section iterator.
        """
        self.expired = True

class Symbol(LLVMObject):
    """Represents a symbol in an object file."""
    def __init__(self, ptr, object_file):
        assert isinstance(ptr, c_object_p)
        assert isinstance(object_file, ObjectFile)

        LLVMObject.__init__(self, ptr)

        self.expired = False
        self._object_file = object_file

    @CachedProperty
    def name(self):
        """The str name of the symbol.

        This is often a function or variable name. Keep in mind that name
        mangling could be in effect.
        """
        if self.expired:
            raise Exception('Symbol instance has expired.')

        return string_at(lib.LLVMGetSymbolName(self))

    @CachedProperty
    def address(self):
        """The address of this symbol, in long bytes."""
        if self.expired:
            raise Exception('Symbol instance has expired.')

        return lib.LLVMGetSymbolAddress(self)

    @CachedProperty
    def file_offset(self):
        """The offset of this symbol in the file, in long bytes."""
        if self.expired:
            raise Exception('Symbol instance has expired.')

        return lib.LLVMGetSymbolFileOffset(self)

    @CachedProperty
    def size(self):
        """The size of the symbol, in long bytes."""
        if self.expired:
            raise Exception('Symbol instance has expired.')

        return lib.LLVMGetSymbolSize(self)

    @CachedProperty
    def section(self):
        """The Section to which this Symbol belongs.

        The returned Section instance does not expire, unlike Sections that are
        commonly obtained through iteration.

        Because this obtains a new section iterator each time it is accessed,
        calling this on a number of Symbol instances could be expensive.
        """
        sections = lib.LLVMGetSections(self._object_file)
        lib.LLVMMoveToContainingSection(sections, self)

        return Section(sections)

    def cache(self):
        """Cache all cacheable properties."""
        getattr(self, 'name')
        getattr(self, 'address')
        getattr(self, 'file_offset')
        getattr(self, 'size')

    def expire(self):
        """Mark the object as expired to prevent future API accesses.

        This is called internally by this module and it is unlikely that
        external callers have a legitimate reason for using it.
        """
        self.expired = True

class Relocation(LLVMObject):
    """Represents a relocation definition."""
    def __init__(self, ptr):
        """Create a new relocation instance.

        Relocations are created from objects derived from Section instances.
        Therefore, this constructor should not be called outside of this
        module. See Section.get_relocations() for the proper method to obtain
        a Relocation instance.
        """
        assert isinstance(ptr, c_object_p)

        LLVMObject.__init__(self, ptr)

        self.expired = False

    @CachedProperty
    def address(self):
        """The address of this relocation, in long bytes."""
        if self.expired:
            raise Exception('Relocation instance has expired.')

        return lib.LLVMGetRelocationAddress(self)

    @CachedProperty
    def offset(self):
        """The offset of this relocation, in long bytes."""
        if self.expired:
            raise Exception('Relocation instance has expired.')

        return lib.LLVMGetRelocationOffset(self)

    @CachedProperty
    def symbol(self):
        """The Symbol corresponding to this Relocation."""
        if self.expired:
            raise Exception('Relocation instance has expired.')

        ptr = lib.LLVMGetRelocationSymbol(self)
        return Symbol(ptr)

    @CachedProperty
    def type_number(self):
        """The relocation type, as a long."""
        if self.expired:
            raise Exception('Relocation instance has expired.')

        return lib.LLVMGetRelocationType(self)

    @CachedProperty
    def type_name(self):
        """The relocation type's name, as a str."""
        if self.expired:
            raise Exception('Relocation instance has expired.')

        return string_at(lib.LLVMGetRelocationTypeName(self))

    @CachedProperty
    def value_string(self):
        if self.expired:
            raise Exception('Relocation instance has expired.')

        return string_at(lib.LLVMGetRelocationValueString(self))

    def expire(self):
        """Expire this instance, making future API accesses fail."""
        self.expired = True

    def cache(self):
        """Cache all cacheable properties on this instance."""
        getattr(self, 'address')
        getattr(self, 'offset')
        getattr(self, 'symbol')
        getattr(self, 'type')
        getattr(self, 'type_name')
        getattr(self, 'value_string')

lib.c_name("LLVMSectionIteratorRef")(c_object_p)
lib.c_name("LLVMSymbolIteratorRef")(c_object_p)
lib.c_name("LLVMRelocationIteratorRef")(c_object_p)

