"""
WRITEME
"""


import cffi


def _wire(ffi):
    ffi.cdef("""
             unsigned avcodec_version(void);
             unsigned avformat_version(void);
             unsigned avutil_version(void);

             void av_register_all(void);
             void avcodec_register_all(void);

             typedef struct AVInputFormat {
                 const char *name;
                 /* ... */
             } AVInputFormat;
             typedef struct AVOutputFormat {
                 const char *name;
                 /* ... */
             } AVOutputFormat;
             AVInputFormat *av_iformat_next(AVInputFormat *F);
             AVOutputFormat *av_oformat_next(AVOutputFormat *F);

             void *av_malloc(size_t size);
             void av_free(void *ptr);

             typedef struct AVIOContext AVIOContext;
             AVIOContext *avio_alloc_context(
                    unsigned char *buffer,
                    int buffer_size,
                    int write_flag,
                    void *opaque,
                    int (*read_packet)(void *opaque, uint8_t *buf, int buf_size),
                    int (*write_packet)(void *opaque, uint8_t *buf, int buf_size),
                    int64_t (*seek)(void *opaque, int64_t offset, int whence));

             typedef struct AVFormatContext {
                 const void *av_class;
                 struct AVInputFormat *iformat;
                 struct AVOutputFormat *oformat;
                 void *priv_data;
                 AVIOContext *pb;
                 int ctx_flags;
                 unsigned int nb_streams;
                 void **streams;
                 char filename[1024];
                 int64_t start_time;
                 /* ... */
             } AVFormatContext;
             AVFormatContext *avformat_alloc_context(void);
             int avformat_open_input(AVFormatContext **ps, const char *filename,
                                     AVInputFormat *fmt, void/*AVDictionary*/ **options);

             """)


# this is a Borg.
# http://code.activestate.com/recipes/66531-singleton-we-dont-need-no-stinkin-singleton-the-bo/
class FF:
    __shared_state = {}
    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls, *args, **kwargs)
        instance.__dict__ = cls.__shared_state
        return instance
    def __init__(self):
        self.ffi = cffi.FFI()
        _wire(self.ffi)
        self.lavc = self.ffi.dlopen("avcodec")
        self.lavf = self.ffi.dlopen("avformat")
        self.lavu = self.ffi.dlopen("avutil")
    def versions(self):
        return (self.lavc.avcodec_version(),
                self.lavf.avformat_version(),
                self.lavu.avutil_version())
