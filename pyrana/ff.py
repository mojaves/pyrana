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
             void *av_mallocz(size_t size);
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


             typedef struct AVDictionary AVDictionary;
             typedef struct AVClass AVClass;
             typedef struct AVProgram AVProgram;
             typedef struct AVChapter AVChapter;
             typedef struct AVStream AVStream;

             typedef struct AVFormatContext {
                 const AVClass *av_class;
                 struct AVInputFormat *iformat;
                 struct AVOutputFormat *oformat;
                 void *priv_data;
                 AVIOContext *pb;
                 int ctx_flags;
                 unsigned int nb_streams;
                 AVStream **streams;
                 char filename[1024];
                 int64_t start_time;
                 int64_t duration;
                 int bit_rate;
                 unsigned int packet_size;
                 int max_delay;
                 int flags;
                 unsigned int probesize;
                 int max_analyze_duration;
                 const uint8_t *key;
                 int keylen;
                 unsigned int nb_programs;
                 AVProgram **programs;
                 enum AVCodecID video_codec_id;
                 enum AVCodecID audio_codec_id;
                 enum AVCodecID subtitle_codec_id;
                 unsigned int max_index_size;
                 unsigned int max_picture_buffer;
                 unsigned int nb_chapters;
                 AVChapter **chapters;
                 AVDictionary *metadata;
                 int64_t start_time_realtime;
                 int fps_probe_size;
                 int error_recognition;
                 /* ... */
             } AVFormatContext;
             AVFormatContext *avformat_alloc_context(void);
             int avformat_open_input(AVFormatContext **ps, const char *filename,
                                     AVInputFormat *fmt, void/*AVDictionary*/ **options);

             """)


# The dreaded singleton. It is a necessary evil[1] and this is the reason why:
# https://bitbucket.org/cffi/cffi/issue/4/typeerror-initializer-for-ctype-double
#
# FIXME: need a more pythonic way to enforce unique-ness.
# what we need yet is a 

class FF:
    __inited = False
    __instance = None
    def __new__(cls, *args, **kwargs):
        if FF.__instance is None:
            FF.__instance = super().__new__(cls, *args, **kwargs)
        return FF.__instance
    def __init__(self):
        if not FF.__inited:
            self.ffi = cffi.FFI()
            _wire(self.ffi)
            self.lavc = self.ffi.dlopen("avcodec")
            self.lavf = self.ffi.dlopen("avformat")
            self.lavu = self.ffi.dlopen("avutil")
            FF.__inited = True
    def versions(self):
        return (self.lavc.avcodec_version(),
                self.lavf.avformat_version(),
                self.lavu.avutil_version())

def getFF():
    return FF()

