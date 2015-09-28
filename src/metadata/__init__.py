# -*- coding: utf-8 -*-
"""
Created on Tue Sep 15 18:37:23 2015

@author: Ariel Ben-Yehuda
"""

try:
    from . import (loader, rbml)
    from .loader import WindowReader
    from .rbml import (Tag, DataTag, TreeTag, ExplicitTag,
                       parse_rbml_data, load_tags)
except SystemError:
    import loader
    from loader import WindowReader
    import rbml
    from rbml import (Tag, DataTag, TreeTag, ExplicitTag,
                      parse_rbml_data, load_tags)

class Tags(rbml.RbmlTags):
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

TAG_MAP = load_tags(Tags)

s1lib=open('/home/ariel/Rust/s1lib/libcore-bb943c5a.rlib','rb')
mdreader=loader.reader_from_metadata(loader.metadata_from_ar(s1lib))
coredata = parse_rbml_data(mdreader, TAG_MAP)
#coredata = parse_rbml_data(Tags.Root, mdreader)
#coretags = {tag:[] for tag in TAG_MAP.values()}
#for tag in PARSED:
#    coretags[tag.tag].append(tag)
