"""
!1 = metadata !{
  i32,      ;; Tag = 52 + LLVMDebugVersion 
            ;; (DW_TAG_variable)
  i32,      ;; Unused field.
  metadata, ;; Reference to context descriptor
  metadata, ;; Name
  metadata, ;; Display name (fully qualified C++ name)
  metadata, ;; MIPS linkage name (for C++)
  metadata, ;; Reference to file where defined
  i32,      ;; Line number where defined
  metadata, ;; Reference to type descriptor
  i1,       ;; True if the global is local to compile unit (static)
  i1,       ;; True if the global is defined in the compile unit (not extern)
  {}*       ;; Reference to the global variable
}


!4 = metadata !{
  i32,      ;; Tag = 36 + LLVMDebugVersion 
            ;; (DW_TAG_base_type)
  metadata, ;; Reference to context 
  metadata, ;; Name (may be "" for anonymous types)
  metadata, ;; Reference to file where defined (may be NULL)
  i32,      ;; Line number where defined (may be 0)
  i64,      ;; Size in bits
  i64,      ;; Alignment in bits
  i64,      ;; Offset in bits
  i32,      ;; Flags
  i32       ;; DWARF type encoding
}



derived
!5 = metadata !{
  i32,      ;; Tag (see below)
  metadata, ;; Reference to context
  metadata, ;; Name (may be "" for anonymous types)
  metadata, ;; Reference to file where defined (may be NULL)
  i32,      ;; Line number where defined (may be 0)
  i64,      ;; Size in bits
  i64,      ;; Alignment in bits
  i64,      ;; Offset in bits
  metadata, ;; Reference to type derived from
  metadata, ;; (optional) Name of the Objective C property assoicated with 
            ;; Objective-C an ivar 
  metadata, ;; (optional) Name of the Objective C property getter selector.
  metadata, ;; (optional) Name of the Objective C property setter selector.
  i32       ;; (optional) Objective C property attributes.
}

composite:
!6 = metadata !{
  i32,      ;; Tag (see below)
  metadata, ;; Reference to context
  metadata, ;; Name (may be "" for anonymous types)
  metadata, ;; Reference to file where defined (may be NULL)
  i32,      ;; Line number where defined (may be 0)
  i64,      ;; Size in bits
  i64,      ;; Alignment in bits
  i64,      ;; Offset in bits
  i32,      ;; Flags
  metadata, ;; Reference to type derived from
  metadata, ;; Reference to array of member descriptors
  i32       ;; Runtime languages
}


enum
!6 = metadata !{
  i32,      ;; Tag = 40 + LLVMDebugVersion 
            ;; (DW_TAG_enumerator)
  metadata, ;; Name
  i64       ;; Value
}

subrange
!42 = metadata !{
  i32,    ;; Tag = 33 + LLVMDebugVersion (DW_TAG_subrange_type)
  i64,    ;; Low value
  i64     ;; High value
}

subprogram
!2 = metadata !{
  i32,      ;; Tag = 46 + LLVMDebugVersion
            ;; (DW_TAG_subprogram)
  i32,      ;; Unused field.
  metadata, ;; Reference to context descriptor
  metadata, ;; Name
  metadata, ;; Display name (fully qualified C++ name)
  metadata, ;; MIPS linkage name (for C++)
  metadata, ;; Reference to file where defined
  i32,      ;; Line number where defined
  metadata, ;; Reference to type descriptor
  i1,       ;; True if the global is local to compile unit (static)
  i1,       ;; True if the global is defined in the compile unit (not extern)
  i32,      ;; Virtuality, e.g. dwarf::DW_VIRTUALITY__virtual
  i32,      ;; Index into a virtual function
  metadata, ;; indicates which base type contains the vtable pointer for the 
            ;; derived class
  i1,       ;; isArtificial
  i1,       ;; isOptimized
  Function *,;; Pointer to LLVM function
  metadata, ;; Lists function template parameters
  metadata  ;; Function declaration descriptor
  metadata  ;; List of function variables
}

"""

import llvm.core.value

VER = 0x90000
VER = 0xc0000 # XX NOT ALL CHECKED!

DW_TAG_variable = 52 + VER
DW_TAG_base_type = 36 + VER
#DW_TAG_formal_parameter = 5 + VER
DW_TAG_member           = 13 + VER
DW_TAG_pointer_type     = 15 + VER
#DW_TAG_reference_type   = 16 + VER
DW_TAG_typedef          = 22 + VER
DW_TAG_const_type       = 38 + VER
DW_TAG_volatile_type    = 53 + VER
DW_TAG_restrict_type    = 55 + VER

DW_TAG_array_type       = 1 + VER
DW_TAG_enumeration_type = 4 + VER
DW_TAG_structure_type   = 19 + VER
DW_TAG_union_type       = 23 + VER
#DW_TAG_vector_type      = 259 + VER
DW_TAG_subroutine_type  = 21 + VER
#DW_TAG_inheritance      = 28 + VER

DW_TAG_enumerator = 40 + VER

DW_TAG_subrange_type = 33 + VER


DW_TAG_subprogram = 46 + VER

DW_TAG_compile_unit = 17 + VER


class SimpleField(object):
    def __init__(self, pos):
        self.pos = pos

class InstantiatedField(object):
    def __init__(self, pos):
        self.pos = pos

class InstantiatedListField(object):
    def __init__(self, pos):
        self.pos = pos

class MetadataNodeMetaClass(type):

    @classmethod
    def instantiate(kls, t):
        if t is None:
            return None
        tag = t[0].value
        if tag not in kls.tag2class:
            raise ValueError("Unknown tag 0x%x (=0x%x + %dd)" % (tag, tag & 0xffff0000, tag & 0xffff))
        return kls.tag2class[tag](t)

    tag2class = {}

    def __new__(cls, name, bases, dct):
        newdct = {}
        for k,v in dct.iteritems():
            def dogetter(pos, func):
                def getter(self):
                    return func(self.data[pos])
                return getter
            if isinstance(v, SimpleField):
                v = property(dogetter(v.pos, lambda a:a))
            elif isinstance(v, InstantiatedField):
                v = property(dogetter(v.pos, cls.instantiate))
            elif isinstance(v, InstantiatedListField):
                def l(o):
                    if o is None:
                        return []

                    # The empty list is represented as a one entry list with a constant 0 as first entry
                    # see DIBuilder::getOrCreateArray.
                    if len(o.operands) == 1 and isinstance(o[0], llvm.core.value.ConstantInt) and o[0].value == 0:
                        return []

                    return map(cls.instantiate, o)
                v = property(dogetter(v.pos, l))
            newdct[k] = v
        r = type.__new__(cls, name, bases, newdct)
        if 'TAG' in dct:
            tag = dct['TAG']
            if tag in cls.tag2class:
                raise ValueError("Tag %d already defined" % tag )
            cls.tag2class[tag] = r
        return r



class Common(object):
    __metaclass__ = MetadataNodeMetaClass
    def __init__(self, data):
        self.data = data
        assert self.tag.value == self.TAG, ("BAD TAG in %s: %s vs %s" % (self.__class__, self.tag, self.TAG))
    tag = SimpleField(0)


class Variable(Common):
    TAG = DW_TAG_variable
    name = SimpleField(3)
    lineno = SimpleField(7)
    type = InstantiatedField(8)
    isstatic = SimpleField(9)
    #defined = SimpleField(10) # "not extern"

class BaseType(Common):
    TAG = DW_TAG_base_type
    name = SimpleField(2)
    bit_size = SimpleField(5)
    bit_alignment = SimpleField(6)

class DerivedType(Common):
    name = SimpleField(2)
    parent = InstantiatedField(9)
    bit_size = SimpleField(5)
    bit_alignment = SimpleField(6)
    bit_offset = SimpleField(7)

class Typedef(DerivedType):
    TAG = DW_TAG_typedef

class PtrType(DerivedType):
    TAG = DW_TAG_pointer_type

class ConstType(DerivedType):
    TAG = DW_TAG_const_type

class VolatileType(DerivedType):
    TAG = DW_TAG_volatile_type

class RestrictType(DerivedType):
    TAG = DW_TAG_restrict_type

class CompositeType(Common):
    name = SimpleField(2)
    parent = InstantiatedField(9)
    members = InstantiatedListField(10)
    bit_size = SimpleField(5)
    bit_alignment = SimpleField(6)

class StructType(CompositeType):
    TAG = DW_TAG_structure_type

class UnionType(CompositeType):
    TAG = DW_TAG_union_type

class ArrayType(CompositeType):
    TAG = DW_TAG_array_type

class EnumType(CompositeType):
    TAG = DW_TAG_enumeration_type

class SubroutineType(CompositeType):
    TAG = DW_TAG_subroutine_type

class MemberType(DerivedType):
    TAG = DW_TAG_member

class Enumerator(Common):
    TAG = DW_TAG_enumerator
    name = SimpleField(1)
    value = SimpleField(2)

class SubrangeType(Common):
    TAG = DW_TAG_subrange_type
    low = SimpleField(1)
    high = SimpleField(2)

class SubProgram(Common):
    TAG = DW_TAG_subprogram
    name = SimpleField(3)
    type = InstantiatedField(8)
    func = SimpleField(16)

class CompileUnit(Common):
    TAG = DW_TAG_compile_unit
    langid = SimpleField(2)
    enum_types = InstantiatedListField(10)
    retained_types = InstantiatedListField(11)
    subprograms = InstantiatedListField(12)
    global_variables = InstantiatedListField(13)

class DebugLoader:
    def __init__(self, m):
        self.m = m
        self.items = {}
        try:
            md = m.get_metadata_named("llvm.dbg.cu")
        except KeyError:
            raise ValueError("No llvm.dbg.cu metadata found in module")
        else:
            self.cu = MetadataNodeMetaClass.instantiate(md[0])
            for c in self.cu.global_variables:
                assert c.TAG == Variable.TAG
                self.items[c.name] = c
            for c in self.cu.subprograms:
                assert c[0] == SubProgram.TAG
                v = SubProgram(c)
                self.items[v.name] = v

    enum_types = property(lambda self: self.cu.enum_types)
    retained_types = property(lambda self: self.cu.retained_types)
    subprograms = property(lambda self: self.cu.subprograms)
    global_variables = property(lambda self: self.cu.global_variables)

    def __getitem__(self, nam):
        return self.items[nam]
