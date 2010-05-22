# Revision 1.0.0 - 20100203
#
# beware: the following is Python-like PSEUDO-code
#
# pyrana (V)

class PyranaError(Exception):
    pass

class EOSError(PyranaError):
    "End Of Stream"
    pass

class NeedFeedError(PyranaError):
    "More data is needed"
    pass

class ProcessingError(PyranaError):
    pass

class SetupError(PyranaError):
    pass

class UnsupportedError(PyranaError):
    pass


# pyrana.format (V)

input_formats  = frozenset()
output_formats = frozenset()


def is_streamable(name) # (XXX!!!)
     """
     is_streamable(name) -> Bool
     tells if a given format is streamable (-> needs seek()) or not.
     """
     pass

def find_stream(streams, streamid, media):
    """
    TODO
    """
    pass

class Packet(object):
    def __init__(self, idx, data, pts, dts, is_key):
        """
        a Packet object represents an immutable, encoded packet of a
        multimedia stream.
        """
        pass
    idx
    pts
    dts
    is_key
    size
    data


class Demuxer(object):
	def __init__(self, f, name=""):
        """
        Demuxer(file-like, name="")
        Initialize a new demuxer for the file type `name' (use "" (empty) for auto probing)
        A Demuxer needs a file-like as a source of data. The file-like object must be
        already open.
        """   
        pass
    def read_frame(self, streamid=pyrana.format.STREAM_ANY):
        """
        read_frame(streamid=ANY) -> Packet Object
        reads and returns a new complete encoded frame (enclosed in a Packet) from the demuxer.
        if the optional `streamid' argument is !ANY, returns a frame
        belonging to the specified streams.

        raises EndOfStreamError if
        - a stream id is specified, and such streams doesn't exists.
        - the streams ends.
        """
        raise NotImplementedError
    def open_decoder(self, streamid, params={}):
        """
        open_decoder(streamid) -> Decoder instance
        create and returns a full-blown decoder Instance capable to decode the selected
        stream. Like doing things manually, just easily.
        """
    streams
        """
        streams: read-only attribute
        list of StreamInfo objects describing the streams found by the demuxer
        (as in old pyrana, no changes)
        """

class Muxer(object): # (XXX!)
    """
    as the old pyrana Muxer class, with the following changes:
    write -> write_frame
    start -> header (called implicitely at first write)
    end   -> trailer (called implicitely at object del)
    add flush() methods (guess what?)
    a file-like is needed by the class constructor. The class guarantees that it will
    use ONLY the write() method and perhaps the seek() method (see is_streamable() function).
    all methods returning a stream will now returns None and will use the file-like instead.
    all methods above can raise IOError.
    """
    def __init__(self, f, name):
        pass
    def add_stream(self, streamid, params={}):
        pass
    def write_header(self):
        pass
    def write_trailer(self):
        pass
    def write_frame(self, Packet):
        """requires an encoded frame enclosed in a Packet!"""
        pass
    def get_pts(self, streamid):
        pass
    def flush(self):
        """flush() -> None"""


#pyrana.video

input_codecs       = frozenset()
output_codecs      = frozenset()
pixel_formats      = frozenset()
user_pixel_formats = frozenset()


class Plane(object):
    # no constructor, can be generated only from Images
    plane_id
    stride
    width
    height
    pix_fmt
    data
    size

class Image(object):
    def __init__(self, width, height, pix_fmt, data):
        """not yet decided"""
        pass
    width
    height
    pix_fmt
    def plane(self, num):
        return Plane # FIXME
    def convert(self, ...):
        return Image # ...


class Frame(object):
    def __init__(self, image, pts, is_key, is_interlaced, top_field_first):
        """not yet decided"""
        pass
    image
    pts
    is_key
    top_field_first
    is_interlaced
    pic_type      # can only by set by decoder/encoder
    coded_num     # ditto
    display_num   # ditto



class Decoder(object):
    """
    Like the old Pyrana class,
    - add the 'params' property (read-only preferred alias for getParams)
    - no conversion/scaling will be performed
    - add flush() operation
    """
    def __init__(self, input_codec, params={}):
        pass
    def decode(self, Packet):
        """decode(Packet) -> Frame"""
        return Frame # ...
    def flush(self):
        """flush() -> Frame"""
        return Frame # ...
    params
        """dict, read-only"""


class Encoder(object):
    """
    Like the old Pyrana class,
    - add the 'params' property (read-only preferred alias for getParams)
    - no conversion/scaling will be performed
    - add flush() operation
    """
    def __init__(self, output_codec, params={}):
        pass
    def encode(self, Frame):
        """encode(Frame) -> Packet"""
        return Packet # ...
    def flush(self):
        """flush() -> Packet"""
        return Packet # ...
    params
        """dict, read-only"""


#pyrana.audio

input_codecs   = frozenset()
output_codecs  = frozenset()

class Frame(object): # (V)
    def __init__(self, data, pts=0, dts=0):
        pass
    pts #XXX
    dts #XXX
    is_key [RO] #XXX
    size [RO]
    data [RO]

class Decoder(object):
    """
    Like the old Pyrana class,
    - add the 'params' property (read-only preferred alias for getParams)
    - no conversion/scaling will be performed
    - add flush() operation
    """
    def __init__(self, input_codec, params={}):
        pass
    def decode(self, Packet):
        """decode(Packet) -> Frame"""
        pass
    def flush(self):
        """flush() -> encdata [str]"""
        pass
    params
        """dict, read-only"""


class Encoder(object):
    """
    Like the old Pyrana class,
    - add the 'params' property (read-only preferred alias for getParams)
    - no conversion/scaling will be performed
    - add flush() operation
    """
    def __init__(self, name, params={}):
        pass
    def encode(self, Frame):
        """encode(Frame) -> Packet"""
        pass
    def flush(self):
        """flush() -> encdata [str]"""
        pass
    params
        """dict, read-only"""


