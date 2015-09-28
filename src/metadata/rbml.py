__all__ = ['Tag', 'DataTag', 'TreeTag', 'ExplicitTag',
           'parse_rbml_data', 'load_tags']

class Tag:
    def __init__(self, reader, _tag_map):
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
    def __init__(self, reader, tag_map):
        super().__init__(reader, tag_map)
        tag = type(self)
        if tag in TAG_STACK:
            RECURSED.append(TAG_STACK[:])
        TAG_STACK.append(tag)
        self.children = parse_rbml_data(reader.clone(), tag_map)
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
def parse_rbml_data(reader, tag_map):
    children = []
    while reader.size():
        tag_id = read_rbml_tag(reader)
        tag = tag_map[tag_id]
        data_len = tag.read_len(reader)
        data = reader.sublet(data_len)
        inner = tag(data, tag_map)
        PARSED.append(inner)
        children.append(inner)
    return children

class RbmlTags:
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
    # 0x18-0x1f HOLE

def load_tags(klass):
    tag_map = {}
    for subklass in klass.__mro__[::-1]:
        for tv in subklass.__dict__.values():
            try:
                if not issubclass(tv, Tag):
                    continue
            except TypeError:
                continue
            tag_map[tv.tag] = tv
    return tag_map
