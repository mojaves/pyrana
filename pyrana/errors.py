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


class LibraryVersionError(PyranaError):
    """
    Missing the right library version for the expected dependency.
    """


class EOSError(PyranaError):
    """
    End Of Stream. Kinda more akin to StopIteration than EOFError.
    """


class NeedFeedError(PyranaError):
    """
    More data is needed to obtain a Frame or a Packet.
    Feed more data in the raising object and try again.
    """


class ProcessingError(PyranaError):
    """
    Runtime processing error.
    """


class SetupError(PyranaError):
    """
    Error while setting up a pyrana object.
    Check again the parameters.
    """


class UnsupportedError(PyranaError):
    """
    Requested an unsupported feature.
    Did you properly initialized everything?
    """


class NotFoundError(PyranaError):
    """
    cannot satisfy the user request: asked for an
    inexistent attribute or for unsupported parameter
    combination.
    """
