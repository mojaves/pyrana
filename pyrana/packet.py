"""
This module provides the transport layer Packet support code.
For internal usage only: do not use nor import directly.
"""

from contextlib import contextmanager
from enum import IntEnum
from .common import PY3
from . import ff, errors


# this save us a call to ffi.cast("int64_t", TS_NULL)
# in C, we have fixed size integers, overflows and overflow tricks.
# in Python, we have unlimited integers aka longs and transparent
# promotions. Sometimes the two things mismatch.
TS_NULL = -0x8000000000000000
PKT_SIZE = 4096


# see avcodec for the meaning of flags
class PacketFlags(IntEnum):
    """
    wrapper for the (wannabe)enum of AVPktFlag
    in libavcodec/avcodec.h
    """
    AV_PKT_FLAG_KEY = 0x0001
    AV_PKT_FLAG_CORRUPT = 0x0002


def _new_cpkt(ffh, size):
    """
    builds a new C(ffi) packet of the given size.
    """
    pkt = ffh.ffi.new('AVPacket *')
    if size == 0:
        ffh.lavc.av_init_packet(pkt)
        pkt.data = ffh.ffi.NULL
        pkt.size = 0
    else:
        err = ffh.lavc.av_new_packet(pkt, size)
        if err < 0:
            raise errors.ProcessingError("cannot allocate packet")
    return pkt


@contextmanager
def raw_packet(size):
    """
    context manager for a raw ffmpeg packet of the given size.
    """
    ffh = ff.get_handle()
    pkt = _new_cpkt(ffh, size)
    yield pkt
    ffh.lavc.av_free_packet(pkt)


# In the current incarnation, it could be happily replaced by a namedtuple.
# however, things are expected to change once Muxer get implemented.
class Packet(object):
    """
    a Packet object represents an immutable, encoded packet of a
    multimedia stream.
    """
    def __init__(self, stream_id=None,
                 data=None, pts=TS_NULL, dts=TS_NULL, is_key=False):
        self._ff = ff.get_handle()
        ffi = self._ff.ffi  # shortcut

        size = PKT_SIZE
        if data is not None:
            data = bytes(data)
            size = len(data)

        self._pkt = _new_cpkt(self._ff, size)

        if stream_id is not None:
            self._pkt.stream_index = stream_id
        self._pkt.pts = ffi.cast("int64_t", pts)
        self._pkt.dts = ffi.cast("int64_t", dts)
        if is_key:
            self._pkt.flags |= PacketFlags.AV_PKT_FLAG_KEY
        self._raw_data = ffi.buffer(self._pkt.data, self._pkt.size)
        if data is not None:
            self._raw_data[0:self._pkt.size] = data

    @classmethod
    def from_cdata(cls, cpkt):
        """
        builds a pyrana Packet from (around) a (cffi-wrapped) libav*
        packet object.
        The libav object must be already initialized and ready to go.
        WARNING: raw access. Use with care.
        """
        ffh = ff.get_handle()
        pkt = object.__new__(cls)
        setattr(pkt, '_ff', ffh)
        setattr(pkt, '_pkt', cpkt)
        setattr(pkt, '_raw_data', ffh.ffi.buffer(cpkt.data, cpkt.size))
        return pkt

    def __del__(self):
        self._ff.lavc.av_free_packet(self._pkt)

    def __repr__(self):
        return "Packet(stream_id=%i, size=%i, " \
               "pts=%i, dts=%i, is_key=%i)" \
               % (self.stream_id, self.size, self.pts,
                  self.dts, self.is_key)

    def __len__(self):
        return self.size

    def __getitem__(self, key):
        dat = bytes(self)
        return dat[key]

    def blob(self):
        """returns the bytes() dump of the object"""
        return bytes(self.data)

    def __bytes__(self):
        return self.blob()

    def __str__(self):
        return repr(self) if PY3 else self.blob()

    def __eq__(self, other):
        return self.data == other.data

    def __hash__(self):
        return hash(self.data)

    @property
    def size(self):
        """
        Size of the packet data (bytes)
        """
        return self._pkt.size

    @property
    def data(self):
        """
        the raw data (bytes) this packet carries.
        """
        return self._raw_data[:self.size]

    @property
    def stream_id(self):
        """
        the identifier of the logical stream which this packet belongs to.
        """
        return self._pkt.stream_index

    @property
    def pts(self):
        """
        the Presentation TimeStamp of this packet.
        """
        return self._pkt.pts

    @property
    def dts(self):
        """
        the Decoding TimeStamp of this packet.
        """
        return self._pkt.dts

    @property
    def is_key(self):
        """
        boolean flag. Is this packet a key frame?
        (provided by libav*)
        """
        return bool(self._pkt.flags & PacketFlags.AV_PKT_FLAG_KEY)

    @contextmanager
    def raw_pkt(self):
        """
        raw access to the underlying FFmpeg packet.
        used by decoders in some corner but important cases.
        For internal usage only.
        TODO: ensure R/O and (thus) simplify
        """
        orig_data = self._pkt.data
        orig_size = self._pkt.size
        yield self._pkt
        self._pkt.data = orig_data
        self._pkt.size = orig_size
