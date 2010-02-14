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

class ProcessingError(PyranaError):
    pass

class SetupError(PyranaError):
    pass

class UnsupportedError(PyranaError):
    pass


# pyrana.format (V)

input_formats  = []
output_formats = []


def is_streaming(name) # (XXX!!!)
     """
     is_streaming(name) -> Bool
     tells if a given format is streamable (-> needs seek()) or not.
     """
     pass


class Packet(object):
    def __init__(self, idx, data, pts, dts, isKey):
        """
        a Packet object represents an immutable, encoded packet of a
        multimedia stream.
        """
        pass
    idx
    pts
    dts
    isKey
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
    def readFrame(self, streamid=pyrana.format.STREAM_ANY):
        """
        readFrame(streamid=ANY) -> Packet Object
        reads and returns a new complete encoded frame (enclosed in a Packet) from the demuxer.
        if the optional `streamid' argument is !ANY, returns a frame
        belonging to the specified streams.

        raises EndOfStreamError if
        - a stream id is specified, and such streams doesn't exists.
        - the streams ends.
        """
        raise NotImplementedError
    def openDecoder(self, streamid, params={}):
        """
        openDecoder(streamid) -> Decoder instance
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
    write -> writeFrame
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
    def addStream(self, streamid, params={}):
        pass
    def writeHeader(self):
        pass
    def writeTrailer(self):
        pass
    def writeFrame(self, Packet):
        """requires an encoded frame enclosed in a Packet!"""
        pass
    def getStreamPTS(self, streamid):
        pass
    def flush(self):
        """flush() -> None"""


#pyrana.video

input_codecs   = []
output_codecs  = []
pixel_formats  = []

class Image(object):
    def __init__(self, width, height, pixFmt, data[4]):
        """not yet decided"""
        pass
    stride
    width
    height
    sizes[4]  [RO]
    planes[4] [RO]
    pixFmt


class Frame(object):
    def __init__(self, image, pts, dts, isKey, isInterlaced, topFieldFirst):
        """not yet decided"""
        pass
    image
    pts
    dts
    isKey
    topFieldFirst
    isInterlaced
    picType
    codedNum
    displayNum


class ImageConverter(object):
     def __init__(self, icsp, ocsp, iw, ih, ow, oh):
         pass
     def convert(self, vframe):
        "vframe -> vframe"
         pass


class Decoder(object):
    """
    Like the old Pyrana class,
    - add the 'params' property (read-only preferred alias for getParams)
    - no conversion/scaling will be performed
    - add flush() operation
    """
    def __init__(self, name, params={}):
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


#pyrana.audio

input_codecs   = []
output_codecs  = []

class Frame(object): # (V)
    def __init__(self, data, pts=0, dts=0):
        pass
    pts   #XXX
    dts   #XXX
    isKey [RO] #XXX
    size  [RO]
    data  [RO]

class Decoder(object):
    """
    Like the old Pyrana class,
    - add the 'params' property (read-only preferred alias for getParams)
    - no conversion/scaling will be performed
    - add flush() operation
    """
    def __init__(self, name, params={}):
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


