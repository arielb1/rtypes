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

TY_TAG = 'TAG'
TY_DATA = 'DATA'

class Tag:
    @classmethod
    def read_len(klass, reader):
        return read_vuint(reader)

class ExplicitTag(Tag):
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
def parse_rbml_data(tag, reader):
    if tag.ty == TY_DATA:
        return []
    if tag in TAG_STACK:
        RECURSED.append(TAG_STACK[:])
    TAG_STACK.append(tag)
    children = []
    while reader.size():
        tag_id = read_rbml_tag(reader)
        tag = TAG_MAP[tag_id]
        data_len = tag.read_len(reader)
        data = reader.sublet(data_len)
        inner = RBMLObject(tag, data)
        PARSED.append(inner)
        children.append(inner)
    TAG_STACK.pop()
    return children

class RBMLObject:
    def __init__(self, tag, reader):
        self.tag = tag
        self.bin = reader.clone()
        self.children = parse_rbml_data(tag, reader.clone())
    def __repr__(self):
        tn = self.tag.__name__
        if self.tag.ty == TY_DATA:
            if self.bin.size() <= 16:
                return '%s(%r)' % (tn, self.bin.data)
            return '%s(..%d)' % (tn, self.bin.size())
        return '%s(%d children)' % (tn, len(self.children))
    __str__ = __repr__

class Tags:
    class ExplicitU8(ExplicitTag):
        tag = 0x00; ty = TY_DATA; explicit_len = 1
    class ExplicitU16(ExplicitTag):
        tag = 0x01; ty = TY_DATA; explicit_len = 2
    class ExplicitU32(ExplicitTag):
        tag = 0x02; ty = TY_DATA; explicit_len = 4
    class ExplicitU64(ExplicitTag):
        tag = 0x03; ty = TY_DATA; explicit_len = 8
    class ExplicitI8(ExplicitTag):
        tag = 0x04; ty = TY_DATA; explicit_len = 1
    class ExplicitI16(ExplicitTag):
        tag = 0x05; ty = TY_DATA; explicit_len = 2
    class ExplicitI32(ExplicitTag):
        tag = 0x06; ty = TY_DATA; explicit_len = 4
    class ExplicitI64(ExplicitTag):
        tag = 0x07; ty = TY_DATA; explicit_len = 8
    class ExplicitBool(ExplicitTag):
        tag = 0x08; ty = TY_DATA; explicit_len = 1
    class ExplicitChar(ExplicitTag):
        tag = 0x09; ty = TY_DATA; explicit_len = 4
    class ExplicitF32(ExplicitTag):
        tag = 0x0a; ty = TY_DATA; explicit_len = 4
    class ExplicitF64(ExplicitTag):
        tag = 0x0b; ty = TY_DATA; explicit_len = 8
    class ExplicitSub8(ExplicitTag):
        tag = 0x0c; ty = TY_DATA; explicit_len = 1
    class ExplicitSub32(ExplicitTag):
        tag = 0x0d; ty = TY_DATA; explicit_len = 4
    # 0x0e-0x10 HOLE
    class String(Tag):
        tag = 0x10; ty = TY_DATA
    class Enum(Tag):
        tag = 0x11; ty = TY_DATA
    class Vec(Tag):
        tag = 0x12; ty = TY_DATA # consider looking inside
    class VecElt(Tag):
        tag = 0x13; ty = TY_DATA
    class Map(Tag):
        tag = 0x14; ty = TY_DATA
    class MapKey(Tag):
        tag = 0x15; ty = TY_DATA
    class MapVal(Tag):
        tag = 0x16; ty = TY_DATA
    class Opaque(Tag):
        tag = 0x17; ty = TY_DATA
    class Root(Tag):
        tag = 0x18; ty = TY_TAG
    # 0x18-0x20 HOLE
    class Items(Tag):
        tag = 0x100; ty = TY_TAG
    class PathsDataName(Tag):
        tag = 0x20; ty = TY_DATA
    class DefId(Tag):
        tag = 0x21; ty = TY_DATA
    class ItemsData(Tag):
        tag = 0x22; ty = TY_TAG
    class ItemsDataItem(Tag):
        tag = 0x23; ty = TY_TAG
    class ItemsDataItemFamily(Tag):
        tag = 0x24; ty = TY_DATA
    class ItemsDataItemType(Tag):
        tag = 0x25; ty = TY_DATA
    class ItemsDataItemSymbol(Tag):
        tag = 0x26; ty = TY_DATA
    class ItemsDataItemVariant(Tag):
        tag = 0x27; ty = TY_DATA
    class ItemsDataParentItem(Tag):
        tag = 0x28; ty = TY_DATA
    class ItemsDataItemIsTupleStructCtor(Tag):
        tag = 0x29; ty = TY_DATA
    class Index(Tag):
        tag = 0x2a; ty = TY_DATA
    class MetaItemNameValue(Tag):
        tag = 0x2f; ty = TY_TAG
    class MetaItemName(Tag):
        tag = 0x30; ty = TY_DATA
    class MetaItemValue(Tag):
        tag = 0x31; ty = TY_DATA
    class Attributes(Tag):
        tag = 0x101; ty = TY_TAG
    class Attribute(Tag):
        tag = 0x32; ty = TY_TAG
    class AttributeIsSugaredDoc(Tag):
        tag = 0x8c; ty = TY_DATA
    class MetaItemWord(Tag):
        tag = 0x33; ty = TY_TAG
    class MetaItemList(Tag):
        tag = 0x34; ty = TY_TAG
    class CrateDeps(Tag):
        tag = 0x102; ty = TY_TAG
    class CrateDep(Tag):
        tag = 0x35; ty = TY_TAG
    class CrateHash(Tag):
        tag = 0x103; ty = TY_DATA
    class CrateCrateName(Tag):
        tag = 0x104; ty = TY_DATA
    class CrateDepCrateName(Tag):
        tag = 0x36; ty = TY_DATA
    class CrateDepHash(Tag):
        tag = 0x37; ty = TY_DATA
    class CrateDepExplicitlyLinked(Tag):
        tag = 0x38; ty = TY_DATA
    class ModImpl(Tag):
        tag = 0x39; ty = TY_DATA # killme
    class ItemTraitItem(Tag):
        tag = 0x3a; ty = TY_TAG
    class ItemTraitRef(Tag):
        tag = 0x3b; ty = TY_DATA
    class DisrVal(Tag):
        tag = 0x3c; ty = TY_DATA
    class Path(Tag):
        tag = 0x3d; ty = TY_TAG
    class PathLen(Tag):
        tag = 0x3e; ty = TY_DATA # ?
    class PathElemMod(Tag):
        tag = 0x3f; ty = TY_DATA
    class PathElemName(Tag):
        tag = 0x40; ty = TY_DATA
    class ItemField(Tag):
        tag = 0x41; ty = TY_TAG
    class ItemFieldOrigin(Tag):
        tag = 0x42; ty = TY_DATA # killme
    class ItemVariances(Tag):
        tag = 0x43; ty = TY_TAG
    class ItemImplItem(Tag):
        tag = 0x44; ty = TY_TAG
    class ItemTraitMethodExplicitSelf(Tag):
        tag = 0x45; ty = TY_DATA
    class DataItemReexport(Tag):
        tag = 0x46; ty = TY_DATA
    class DataItemReexportDefId(Tag):
        tag = 0x47; ty = TY_DATA
    class DataItemReexportName(Tag):
        tag = 0x48; ty = TY_DATA
    class Ast(Tag):
        tag = 0x50; ty = TY_TAG
    class Tree(Tag):
        tag = 0x51; ty = TY_TAG
#   class IdRange(Tag):
#       tag = 0x52; unused
    class Table(Tag):
        tag = 0x53; ty = TY_TAG
    class TableDef(Tag):
        tag = 0x56; ty = TY_TAG
    class TableNodeType(Tag):
        tag = 0x57; ty = TY_TAG
    class TableItemSubst(Tag):
        tag = 0x58; ty = TY_TAG
    class TableFreevars(Tag):
        tag = 0x59; ty = TY_TAG
    class TableTCache(Tag):
        tag = 0x5a; ty = TY_TAG
    class TableParamDefs(Tag):
        tag = 0x5b; ty = TY_TAG
#   class TableMutbl(Tag):
#       tag = 0x5c; unused
#   class TableLastUse(Tag):
#       tag = 0x5d; unused
#   class TableSpill(Tag):
#       tag = 0x5e; unused
    class TableMethodMap(Tag):
        tag = 0x5f; ty = TY_TAG
#   class TableVtableMap(Tag):
#       tag = 0x60; unused
    class TableAdjustments(Tag):
        tag = 0x61; ty = TY_TAG
#   class TableMoveMap(Tag):
#       tag = 0x62; unused
#   class TableCaptureMap(Tag):
#       tag = 0x63; unused
    class TableClosureTys(Tag):
        tag = 0x64; ty = TY_TAG
    class TableClosureKinds(Tag):
        tag = 0x65; ty = TY_TAG
    class TableUpvarCaptureMap(Tag):
        tag = 0x66; ty = TY_TAG
#   class TableCaptureModes(Tag):
#       tag = 0x67; unused
    class TagTableConstQualif(Tag):
        tag = 0x69; ty = TY_TAG
    class TableCastKinds(Tag):
        tag = 0x6a; ty = TY_TAG
    class ItemsTraitItemSort(Tag):
        tag = 0x70; ty = TY_DATA
    class ItemsTraitParentSort(Tag):
        tag = 0x71; ty = TY_DATA # killme
    class ItemsImplTypeBasename(Tag):
        tag = 0x72; ty = TY_DATA # killme
    class CrateTriple(Tag):
        tag = 0x105; ty = TY_DATA
    class DylibDependencyFormats(Tag):
        tag = 0x106; ty = TY_DATA
    class LangItems(Tag):
        tag = 0x107; ty = TY_TAG
    class LangItemsItem(Tag):
        tag = 0x73; ty = TY_TAG
    class LangItemsItemId(Tag):
        tag = 0x74; ty = TY_DATA
    class LangItemsItemNodeId(Tag):
        tag = 0x75; ty = TY_DATA
    class LangItemsMissing(Tag):
        tag = 0x76; ty = TY_DATA
    class UnnamedField(Tag):
        tag = 0x77; ty = TY_TAG
    class ItemsDataItemVisibility(Tag):
        tag = 0x78; ty = TY_DATA
#   class ItemMethodTps(Tag):
#       tag = 0x79; unused
    class ItemMethodFty(Tag):
        tag = 0x7a; ty = TY_DATA
    class ModChild(Tag):
        tag = 0x7b; ty = TY_DATA
    class MiscInfo(Tag):
        tag = 0x108; ty = TY_TAG
    class MiscInfoCrateItems(Tag):
        tag = 0x7c; ty = TY_TAG
    class ItemMethodProvidedSource(Tag):
        tag = 0x7d; ty = TY_DATA
#   class ItemImplVtables(Tag):
#       tag = 0x7e; unused
    class Impls(Tag):
        tag = 0x109; ty = TY_TAG
    class ImplsImpl(Tag):
        tag = 0x7f; ty = TY_TAG
    class ImplsImplTraitDefId(Tag):
        tag = 0x8d; ty = TY_DATA
    class ItemsDataItemInherentImpl(Tag):
        tag = 0x80; ty = TY_TAG
    class ItemsDataItemExtensionImpl(Tag):
        tag = 0x81; ty = TY_TAG
    class NativeLibraries(Tag):
        tag = 0x10a; ty = TY_TAG
    class NativeLibrariesLib(Tag):
        tag = 0x82; ty = TY_TAG
    class NativeLibrariesName(Tag):
        tag = 0x83; ty = TY_DATA
    class NativeLibrariesKind(Tag):
        tag = 0x84; ty = TY_DATA
    class PluginRegistrarFn(Tag):
        tag = 0x10b; ty = TY_DATA
    class MethodArgumentNames(Tag):
        tag = 0x85; ty = TY_TAG
    class MethodArgumentName(Tag):
        tag = 0x86; ty = TY_DATA
    class ReachableIds(Tag):
        tag = 0x10c; ty = TY_TAG
    class ReachableId(Tag):
        tag = 0x87; ty = TY_DATA
    class ItemsDataItemStability(Tag):
        tag = 0x88; ty = TY_TAG
    class ItemsDataItemRepr(Tag):
        tag = 0x89; ty = TY_TAG
    class StructFields(Tag):
        tag = 0x10d; ty = TY_TAG
    class StructField(Tag):
        tag = 0x8a; ty = TY_TAG
    class StructFieldId(Tag):
        tag = 0x8b; ty = TY_DATA
    class ItemsDataRegion(Tag):
        tag = 0x8e; ty = TY_DATA
    class RegionParamDef(Tag):
        tag = 0x8f; ty = TY_TAG
    class RegionParamDefIdent(Tag):
        tag = 0x90; ty = TY_TAG
    class RegionParamDefDefId(Tag):
        tag = 0x91; ty = TY_DATA
    class RegionParamDefSpace(Tag):
        tag = 0x92; ty = TY_DATA
    class RegionParamDefIndex(Tag):
        tag = 0x93; ty = TY_DATA
    class TypeParamDef(Tag):
        tag = 0x94; ty = TY_DATA
    class ItemGenerics(Tag):
        tag = 0x95; ty = TY_TAG
    class MethodTyGenerics(Tag):
        tag = 0x96; ty = TY_TAG
    class Predicate(Tag):
        tag = 0x97; ty = TY_TAG
    class PredicateSpace(Tag):
        tag = 0x98; ty = TY_DATA
    class PredicateData(Tag):
        tag = 0x99; ty = TY_DATA
    class Unsafety(Tag):
        tag = 0x9a; ty = TY_DATA
    class AssociatedTypeNames(Tag):
        tag = 0x9b; ty = TY_TAG
    class AssociatedTypeName(Tag):
        tag = 0x9c; ty = TY_DATA
    class Polarity(Tag):
        tag = 0x9d; ty = TY_DATA
    class MacroDefs(Tag):
        tag = 0x10e; ty = TY_TAG
    class MacroDef(Tag):
        tag = 0x9e; ty = TY_TAG
    class MacroDefBody(Tag):
        tag = 0x9f; ty = TY_DATA
    class ParenSugar(Tag):
        tag = 0xa0; ty = TY_DATA
    class Codemap(Tag):
        tag = 0xa1; ty = TY_TAG
    class CodemapFilemap(Tag):
        tag = 0xa2; ty = TY_TAG
    class ItemSuperPredicates(Tag):
        tag = 0xa3; ty = TY_TAG
    class DefaultedTrait(Tag):
        tag = 0xa4; ty = TY_DATA
    class ImplCoerceUnsizedKind(Tag):
        tag = 0xa5; ty = TY_TAG
    class ItemsDataItemConstness(Tag):
        tag = 0xa6; ty = TY_DATA

TAG_MAP = {}
for tv in Tags.__dict__.values():
    try:
        if not issubclass(tv, Tag):
            continue
    except TypeError:
        continue
    TAG_MAP[tv.tag] = tv
def tagged_child(parent, child_tag):
    for child in parent.children:
        if child.tag == child_tag:
            return child
    return None

#coredata = parse_rbml_data(Tags.Root, mdreader)
#coretags = {tag:[] for tag in TAG_MAP.values()}
#for tag in PARSED:
#    coretags[tag.tag].append(tag)
