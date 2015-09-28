# -*- coding: utf-8 -*-
"""
Created on Tue Sep 15 18:37:23 2015

@author: Ariel Ben-Yehuda
"""

import struct
try:
    from . import loader
    from .loader import WindowReader
except SystemError:
    import loader
    from loader import WindowReader

class Tag:
    def __init__(self, reader):
        self.bin = reader.clone()

    @classmethod
    def read_len(klass, reader):
        return read_vuint(reader)

    @property
    def tag_name(self):
        return type(self).__name__

    def __repr__(self):
        if self.bin.size() <= 16:
            return '%s(%r)' % (self.tag_name, self.bin.data)
        return '%s(..%d)' % (self.tag_name, self.bin.size())
    __str__ = __repr__

class DataTag(Tag):
    @property
    def value(self):
        result = 0
        for c in self.bin.data:
            result = (result<<8)+c
        return result

class TreeTag(Tag):
    def __init__(self, reader):
        super().__init__(reader)
        tag = type(self)
        if tag in TAG_STACK:
            RECURSED.append(TAG_STACK[:])
        TAG_STACK.append(tag)
        self.children = parse_rbml_data(reader.clone())
        TAG_STACK.pop()

    def child_tagged(self, child_tag):
        for child in self.children:
            if isinstance(child, child_tag):
                return child

    def __repr__(self):
        return '%s(%d children)' % (self.tag_name, len(self.children))
    __str__ = __repr__

class ExplicitTag(DataTag):
    @classmethod
    def read_len(klass, _reader):
        return klass.explicit_len

def read_vuint(reader):
    fst = reader.read(1)[0]
    if fst >= 0x80:
        return fst & 0x7f
    elif fst >= 0x40:
        snd = reader.read(1)[0]
        return ((fst & 0x3f)<<8)+snd
    elif fst >= 0x20:
        snd = reader.read(1)[0]
        trd = reader.read(1)[0]
        return ((fst & 0x1f)<<16)+(snd<<8)+trd
    elif fst >= 0x10:
        snd = reader.read(1)[0]
        trd = reader.read(1)[0]
        fth = reader.read(1)[0]
        return ((fst & 0x0f)<<24)+(snd<<16)+(trd<<8)+fth
    else:
        raise ValueError('invalid code %d' % fst)

def read_rbml_tag(reader):
    fst = reader.read(1)[0]
    if fst < 0xf0:
        return fst
    elif fst == 0xf0:
        raise ValueError('overlong form')
    else:
        snd = reader.read(1)[0]
        return ((fst&0x0f)<<8)+snd

TAG_STACK = []
RECURSED = []
PARSED = []
def parse_rbml_data(reader):
    children = []
    while reader.size():
        tag_id = read_rbml_tag(reader)
        tag = TAG_MAP[tag_id]
        data_len = tag.read_len(reader)
        data = reader.sublet(data_len)
        inner = tag(data)
        PARSED.append(inner)
        children.append(inner)
    return children

class Tags:
    class ExplicitU8(ExplicitTag):
        tag = 0x00; explicit_len = 1
    class ExplicitU16(ExplicitTag):
        tag = 0x01; explicit_len = 2
    class ExplicitU32(ExplicitTag):
        tag = 0x02; explicit_len = 4
    class ExplicitU64(ExplicitTag):
        tag = 0x03; explicit_len = 8
    class ExplicitI8(ExplicitTag):
        tag = 0x04; explicit_len = 1
    class ExplicitI16(ExplicitTag):
        tag = 0x05; explicit_len = 2
    class ExplicitI32(ExplicitTag):
        tag = 0x06; explicit_len = 4
    class ExplicitI64(ExplicitTag):
        tag = 0x07; explicit_len = 8
    class ExplicitBool(ExplicitTag):
        tag = 0x08; explicit_len = 1
    class ExplicitChar(ExplicitTag):
        tag = 0x09; explicit_len = 4
    class ExplicitF32(ExplicitTag):
        tag = 0x0a; explicit_len = 4
    class ExplicitF64(ExplicitTag):
        tag = 0x0b; explicit_len = 8
    class ExplicitSub8(ExplicitTag):
        tag = 0x0c; explicit_len = 1
    class ExplicitSub32(ExplicitTag):
        tag = 0x0d; explicit_len = 4
    # 0x0e-0x10 HOLE
    class String(DataTag): tag = 0x10
    class Enum(TreeTag): tag = 0x11
    class Vec(TreeTag): tag = 0x12
    class VecElt(TreeTag): tag = 0x13
    class Map(TreeTag): tag = 0x14
    class MapKey(DataTag): tag = 0x15
    class MapVal(DataTag): tag = 0x16
    class Opaque(DataTag): tag = 0x17
    # 0x18-0x20 HOLE
    class Items(TreeTag): tag = 0x100
    class PathsDataName(DataTag): tag = 0x20
    class DefId(DataTag): tag = 0x21
    class ItemsData(TreeTag): tag = 0x22
    class ItemsDataItem(TreeTag): tag = 0x23
    class ItemsDataItemFamily(DataTag): tag = 0x24
    class ItemsDataItemType(DataTag): tag = 0x25
    class ItemsDataItemSymbol(DataTag): tag = 0x26
    class ItemsDataItemVariant(DataTag): tag = 0x27
    class ItemsDataParentItem(DataTag): tag = 0x28
    class ItemsDataItemIsTupleStructCtor(DataTag): tag = 0x29
    class Index(DataTag): tag = 0x110
    class XrefIndex(DataTag): tag = 0x111
    class XrefData(DataTag): tag = 0x112
    class MetaItemNameValue(TreeTag): tag = 0x2f
    class MetaItemName(DataTag): tag = 0x30
    class MetaItemValue(DataTag): tag = 0x31
    class Attributes(TreeTag): tag = 0x101
    class Attribute(TreeTag): tag = 0x32
    class AttributeIsSugaredDoc(DataTag): tag = 0x8c
    class MetaItemWord(TreeTag): tag = 0x33
    class MetaItemList(TreeTag): tag = 0x34
    class CrateDeps(TreeTag): tag = 0x102
    class CrateDep(TreeTag): tag = 0x35
    class CrateHash(DataTag): tag = 0x103
    class CrateCrateName(DataTag): tag = 0x104
    class CrateDepCrateName(DataTag): tag = 0x36
    class CrateDepHash(DataTag): tag = 0x37
    class CrateDepExplicitlyLinked(DataTag): tag = 0x38
    # GAP 0x39
    class ItemTraitItem(TreeTag): tag = 0x3a
    class ItemTraitRef(DataTag): tag = 0x3b
    class DisrVal(DataTag): tag = 0x3c
    class Path(TreeTag): tag = 0x3d
    class PathLen(DataTag): tag = 0x3e # ?
    class PathElemMod(DataTag): tag = 0x3f
    class PathElemName(DataTag): tag = 0x40
    class ItemField(TreeTag): tag = 0x41
    # GAP 0x42
    class ItemVariances(TreeTag): tag = 0x43
    class ItemImplItem(TreeTag): tag = 0x44
    class ItemTraitMethodExplicitSelf(DataTag): tag = 0x45
    class DataItemReexport(DataTag): tag = 0x46
    class DataItemReexportDefId(DataTag): tag = 0x47
    class DataItemReexportName(DataTag): tag = 0x48
    # GAP 0x49 - 0x4f

    # -- 0x50-0x6f: astencode tags
    class Ast(TreeTag): tag = 0x50
    class Tree(DataTag): tag = 0x51
    # GAP 0x52
    class Table(TreeTag): tag = 0x53
    # GAP 0x54, 0x55
    class TableDef(TreeTag): tag = 0x56
    class TableNodeType(TreeTag): tag = 0x57
    class TableItemSubst(TreeTag): tag = 0x58
    class TableFreevars(TreeTag): tag = 0x59
    # GAP 0x5a
    class TableParamDefs(TreeTag): tag = 0x5b # killme
    # GAP 0x5c, 0x5d, 0x5e
    class TableMethodMap(TreeTag): tag = 0x5f
    # GAP 0x60
    class TableAdjustments(TreeTag): tag = 0x61
    # GAP 0x62, 0x63
    class TableClosureTys(TreeTag): tag = 0x64
    class TableClosureKinds(TreeTag): tag = 0x65
    class TableUpvarCaptureMap(TreeTag): tag = 0x66
    # GAP 0x67
    class TagTableConstQualif(TreeTag): tag = 0x69
    class TableCastKinds(TreeTag): tag = 0x6a
    # GAP 0x6b, 0x6c, 0x6d, 0x6e, 0x6f
    # -- end astencode tags

    class ItemsTraitItemSort(DataTag): tag = 0x70
    class CrateTriple(DataTag): tag = 0x105
    class DylibDependencyFormats(DataTag): tag = 0x106
    class LangItems(TreeTag): tag = 0x107
    class LangItemsItem(TreeTag): tag = 0x73
    class LangItemsItemId(DataTag): tag = 0x74
    class LangItemsItemNodeId(DataTag): tag = 0x75
    class LangItemsMissing(DataTag): tag = 0x76
    class UnnamedField(TreeTag): tag = 0x77
    class ItemsDataItemVisibility(DataTag): tag = 0x78
    # GAP 0x79, 0x7a
    class ModChild(DataTag): tag = 0x7b
    class MiscInfo(TreeTag): tag = 0x108
    class MiscInfoCrateItems(TreeTag): tag = 0x7c
    class ItemMethodProvidedSource(DataTag): tag = 0x7d
    # GAP 0x7e
    class Impls(TreeTag): tag = 0x109
    class ImplsImpl(DataTag): tag = 0x7f
    class ImplsImplTraitDefId(DataTag): tag = 0x8d
    class ItemsDataItemInherentImpl(TreeTag): tag = 0x80
    class ItemsDataItemExtensionImpl(TreeTag): tag = 0x81
    class NativeLibraries(TreeTag): tag = 0x10a
    class NativeLibrariesLib(TreeTag): tag = 0x82
    class NativeLibrariesName(DataTag): tag = 0x83
    class NativeLibrariesKind(DataTag): tag = 0x84
    class PluginRegistrarFn(DataTag): tag = 0x10b
    class MethodArgumentNames(TreeTag): tag = 0x85
    class MethodArgumentName(DataTag): tag = 0x86
    class ReachableIds(TreeTag): tag = 0x10c
    class ReachableId(DataTag): tag = 0x87
    class ItemsDataItemStability(TreeTag): tag = 0x88
    class ItemsDataItemRepr(TreeTag): tag = 0x89
    class StructFields(TreeTag): tag = 0x10d
    class StructField(TreeTag): tag = 0x8a
    class StructFieldId(DataTag): tag = 0x8b
    # 0x8c = AttributeIsSugaredDoc
    # 0x8d = ImplTraitDefId
    class ItemsDataRegion(DataTag): tag = 0x8e
    class RegionParamDef(TreeTag): tag = 0x8f
    class RegionParamDefIdent(TreeTag): tag = 0x90
    class RegionParamDefDefId(DataTag): tag = 0x91
    class RegionParamDefSpace(DataTag): tag = 0x92
    class RegionParamDefIndex(DataTag): tag = 0x93
    class TypeParamDef(DataTag): tag = 0x94
    class ItemGenerics(TreeTag): tag = 0x95
    class MethodTyGenerics(TreeTag): tag = 0x96
    class TypePredicate(DataTag): tag = 0x97
    class SelfPredicate(DataTag): tag = 0x98
    class FnPredicate(DataTag): tag = 0x99
    class Unsafety(DataTag): tag = 0x9a
    class AssociatedTypeNames(TreeTag): tag = 0x9b
    class AssociatedTypeName(DataTag): tag = 0x9c
    class Polarity(DataTag): tag = 0x9d
    class MacroDefs(TreeTag): tag = 0x10e
    class MacroDef(TreeTag): tag = 0x9e
    class MacroDefBody(DataTag): tag = 0x9f
    class ParenSugar(DataTag): tag = 0xa0
    class Codemap(TreeTag): tag = 0xa1
    class CodemapFilemap(TreeTag): tag = 0xa2
    class ItemSuperPredicates(TreeTag): tag = 0xa3
    class DefaultedTrait(DataTag): tag = 0xa4
    class ImplCoerceUnsizedKind(TreeTag): tag = 0xa5
    class ItemsDataItemConstness(DataTag): tag = 0xa6

TAG_MAP = {}
for tv in Tags.__dict__.values():
    try:
        if not issubclass(tv, Tag):
            continue
    except TypeError:
        continue
    TAG_MAP[tv.tag] = tv

import sys
sys.tag_stack=TAG_STACK
s1lib=open('/home/ariel/Rust/s1lib/libcore-bb943c5a.rlib','rb')
mdreader=loader.reader_from_metadata(loader.metadata_from_ar(s1lib))
coredata = parse_rbml_data(mdreader)
#coredata = parse_rbml_data(Tags.Root, mdreader)
#coretags = {tag:[] for tag in TAG_MAP.values()}
#for tag in PARSED:
#    coretags[tag.tag].append(tag)
