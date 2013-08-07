"""
The pyrana exception hierarchy.
Outside the pyrana package it is expected to catch those
exception, not to raise them. However, doing so should'nt
harm anyone.
"""

class PyranaError(Exception):
    """
    Root of the pyrana error tree.
    You should'nt use it directly, not even in an except clause.
    """
    pass


class EOSError(PyranaError):
    """
    End Of Stream. Kinda more akin to StopIteration than EOFError.
    """
    pass


class NeedFeedError(PyranaError):
    """
    More data is needed to obtain a Frame or a Packet.
    """
    pass


class ProcessingError(PyranaError):
    """
    Runtime processing error.
    """
    pass


class SetupError(PyranaError):
    """
    Error while setting up a pyrana object.
    Check again the parameters.
    """
    pass


class UnsupportedError(PyranaError):
    """
    Requested an unsupported feature.
    Did you properly initialized everything?
    """
    pass
