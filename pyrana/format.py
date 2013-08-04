"""
this module provides the transport layer facilities.
(WRITEME)
"""

STREAM_ANY = -1
TS_NULL = 0x8000000000000000


INPUT_FORMATS = frozenset()
OUTPUT_FORMATS = frozenset()


def is_streamable(name):
    """
    is_streamable(name) -> Bool
    tells if a given format is streamable (do NOT need seek()) or not.
    """
    return name in INPUT_FORMATS or name in OUTPUT_FORMATS  # TODO


def find_stream(streams, stream_id, media):
    """
    TODO
    """
    pass


class Packet:
    """
    a Packet object represents an immutable, encoded packet of a
    multimedia stream.
    """
    def __init__(self, stream_id, data,
                 pts=TS_NULL, dts=TS_NULL, is_key=False):
        self._stream_id = stream_id
        self._pts = pts
        self._dts = dts
        self._data = bytes(data)
        self._is_key = is_key

    def __len__(self):
        return len(self._data)

    def __bytes__(self):
        return self._data

    def __hash__(self):
        return hash(self._data)

    @property
    def stream_id(self):
        """
        the identifier of the logical stream which this packet belongs to.
        """
        return self._stream_id

    @property
    def pts(self):
        """
        the Presentation TimeStamp of this packet.
        """
        return self._pts

    @property
    def dts(self):
        """
        the Decoding TimeStamp of this packet.
        """
        return self._dts

    @property
    def data(self):
        """
        the raw data (bytes) this packet carries.
        """
        return self._data

    @property
    def is_key(self):
        """
        boolean flag. Is this packe a key frame?
        (provided by libav*)
        """
        return self._is_key

    @property
    def size(self):
        """
        Size of the packet data (bytes)
        """
        return len(self._data)


class Demuxer:
    def __init__(self, src, name=None):
        """
        Demuxer(src, name="")
        Initialize a new demuxer for the file type `name' (use "" (empty)
        for auto probing).
        A Demuxer needs a RawIOBase-compliant as a source of data.
        The RawIOBase-compliant object must be already open.
        """
        pass

    def read_frame(self, stream_id=STREAM_ANY):
        """
        read_frame(stream_id=ANY) -> Packet Object
        reads and returns a new complete encoded frame (enclosed in a Packet)
        from the demuxer.
        if the optional `stream_id' argument is !ANY, returns a frame
        belonging to the specified streams.

        raises EndOfStreamError if
        - a stream id is specified, and such streams doesn't exists.
        - the streams ends.
        """
        raise NotImplementedError

    def open_decoder(self, stream_id, params=None):
        """
        open_decoder(stream_id) -> Decoder instance
        create and returns a full-blown decoder Instance capable
        to decode the selected stream.
        Like doing things manually, just easily.
        """
        params = {} if params is None else params
        raise NotImplementedError

    @property
    def streams(self):
        """
        streams: read-only attribute
        list of StreamInfo objects describing the streams found by the demuxer
        (as in old pyrana, no changes)
        """
        return []


class Muxer:
    def __init__(self, dst, name):
        """
        Muxer(dst, name="")
        Initialize a new muxer for the file type `name'
        A Muxer needs a RawIOBase-compliant as a sink of data.
        The RawIOBase-compliant object must be already open.
        """
        pass

    def add_stream(self, stream_id, params=None):
        params = {} if params is None else params
        raise NotImplementedError

    def write_header(self):
        raise NotImplementedError

    def write_trailer(self):
        raise NotImplementedError

    def write_frame(self, packet):
        """requires an encoded frame enclosed in a Packet!"""
        raise NotImplementedError

    def get_pts(self, stream_id):
        raise NotImplementedError

    def flush(self):
        """flush() -> None"""
        pass
