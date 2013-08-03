
TS_NULL = 0x8000000000000000

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



