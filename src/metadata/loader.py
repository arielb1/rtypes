import struct
import zlib

class WindowReader:
    def __init__(self, data, begin, end):
        self.cdata = data
        self.begin = begin
        self.end = end

    def clone(self):
        return WindowReader(self.cdata, self.begin, self.end)

    def size(self):
        return self.end - self.begin

    def read(self, rlen=-1):
        if rlen < 0 or rlen > self.size():
            rlen = self.size()
        old_begin = self.begin
        self.begin += rlen
        return self.cdata[old_begin:self.begin]

    def sublet(self, sub_len):
        if self.end - self.begin < sub_len:
            raise IndexError('end={} begin={} sub_len={}'.format(
                self.end, self.begin, sub_len
            ))
        old_begin = self.begin
        self.begin += sub_len
        return WindowReader(self.cdata, old_begin, self.begin)

    @property
    def data(self):
        return self.cdata[self.begin:self.end]

def metadata_from_ar(f):
    f.seek(8)
    names = None
    while True:
        header = f.read(60)
        assert len(header) == 60
        assert header.endswith(b'\x60\x0a')
        name = header[:16]
        size = int(header[48:58])
        if name == b'//              ':
            names = f.read(size)
        else:
            name, sep, more = name.partition(b'/')
            more = more.strip()
            if more:
                assert name == b''
                nameoff = int(more)
                name = names[nameoff:names.find(b'/', nameoff)]
            if name == b'rust.metadata.bin':
                return f.read(size)
            f.seek(size, 1)

def metadata_from_elf(f):
    f.seek(4)
    bits, endian, ver = f.read(3)
    assert ver == 1
    word = 'HIQ'[bits]
    wordlen = [2,4,8][bits]
    endian = '!<>'[endian]
    f.seek(0x18+2*wordlen)
    shoff, = struct.unpack(endian + word, f.read(wordlen))
    f.seek(0x18+3*wordlen+0x0a)
    shentsize, shnum, shstrndx = struct.unpack(endian + 'HHH', f.read(6))

    class ElfSection:
        def __init__(self, hdr):
            d = struct.unpack(endian + 'II' + word*4 + 'II' + word*2, hdr)
            self.shname, self.shtype, \
                self.shflags, self.shaddr, self.shoffset, self.shsize, \
                self.shlink, self.shinfo, \
                self.shaddralign, self.shentsize = d

        def data(self):
            f.seek(self.shoffset)
            return f.read(self.shsize)

        def name(self):
            return strpool[self.shname:strpool.find(0, self.shname)]

    f.seek(shoff)
    sections = []
    for i in range(shnum):
        sections.append(ElfSection(f.read(0x10+6*wordlen)))
    strpool = sections[shstrndx].data()

    metadata = list(s for s in sections if s.name() == b'.note.rustc')[-1].data()
    assert metadata.startswith(b'rust\0\0\0\2')
    return zlib.decompress(metadata[8:], -zlib.MAX_WBITS)


def reader_from_metadata(metadata):
    mdlen, = struct.unpack('!I', metadata[:4])
    mdreader = WindowReader(metadata, 4, 4+mdlen)
    return mdreader
