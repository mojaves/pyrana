"""
The pyrana exception hierarchy.
Should NOT be used directly by the external code.
"""

class PyranaError(Exception):
    """
    Root of the pyrana error tree.
    """
    pass


class EOSError(PyranaError):
    """
    End Of Stream
    """
    pass


class NeedFeedError(PyranaError):
    """
    More data is needed
    """
    pass


class ProcessingError(PyranaError):
    """
    Runtime processing error
    """
    pass


class SetupError(PyranaError):
    """
    Error while setting up a pyrana object
    """
    pass


class UnsupportedError(PyranaError):
    """
    Requested an unsupported feature.
    """
    pass



