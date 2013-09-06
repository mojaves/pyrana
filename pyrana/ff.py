"""
WRITEME
"""

from functools import wraps
import cffi


def _wire(ffi):
    """
    declare and export all the C API items needed
    by pyrana.
    """
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
         int url_feof(AVIOContext *s);

         /* AVPacket is part of the stable ABI. */
         typedef struct AVPacket {
             int64_t pts;
             int64_t dts;
             uint8_t *data;
             int   size;
             int   stream_index;
             int   flags;
             struct {
                 uint8_t *data;
                 int      size;
                 enum AVPacketSideDataType type;
             } *side_data;
             int side_data_elems;
             int   duration;
             void  (*destruct)(struct AVPacket *);
             void  *priv;
             int64_t pos;
             int64_t convergence_duration;
         } AVPacket;

         void av_destruct_packet(AVPacket *pkt);
         void av_init_packet(AVPacket *pkt);
         int av_new_packet(AVPacket *pkt, int size);
         void av_shrink_packet(AVPacket *pkt, int size);
         int av_grow_packet(AVPacket *pkt, int grow_by);
         int av_dup_packet(AVPacket *pkt);
         int av_copy_packet(AVPacket *dst, AVPacket *src);
         void av_free_packet(AVPacket *pkt);

         typedef struct AVDictionary AVDictionary;
         typedef struct AVClass AVClass;
         typedef struct AVProgram AVProgram;
         typedef struct AVChapter AVChapter;

         typedef struct AVCodecContext {
            const AVClass *av_class;
            int log_level_offset;
            enum AVMediaType codec_type;
            const struct AVCodec *codec;
            char codec_name[32];
            enum AVCodecID codec_id;
            unsigned int codec_tag;
            unsigned int stream_codec_tag;
            /* ... */
         } AVCodecContext;

         typedef struct AVStream {
            int index;
            int id;
            AVCodecContext *codec;
            /* ... */
         } AVStream;

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
         void avformat_free_context(AVFormatContext *s);
         int avformat_open_input(AVFormatContext **ps, const char *filename,
                                 AVInputFormat *fmt, AVDictionary **options);
         void avformat_close_input(AVFormatContext **s);
         int avformat_find_stream_info(AVFormatContext *ic, AVDictionary **options);

         int av_read_frame(AVFormatContext *s, AVPacket *pkt);

         typedef struct AVCodec {
             const char *name;
             const char *long_name;
             enum AVMediaType type;
             enum AVCodecID id;
             int capabilities;
              /* ... */
         } AVCodec;
         AVCodec *av_codec_next(const AVCodec *c);
         AVCodec *avcodec_find_decoder(enum AVCodecID id);
         AVCodec *avcodec_find_decoder_by_name(const char *name);

         enum AVMediaType avcodec_get_type(enum AVCodecID codec_id);
         const char *avcodec_get_name(enum AVCodecID id);
         int avcodec_is_open(AVCodecContext *s);
         int av_codec_is_encoder(const AVCodec *codec);
         int av_codec_is_decoder(const AVCodec *codec);

         /* TODO: replace magic number - 8 */
         typedef struct AVFrame {
             uint8_t *data[8];
             int linesize[8];
             uint8_t **extended_data;
             int width, height;
             int nb_samples;
             int format;
             int key_frame;
             enum AVPictureType pict_type;
             /* ... */
         } AVFrame;

         AVFrame *avcodec_alloc_frame(void);
         void avcodec_get_frame_defaults(AVFrame *frame);
         void avcodec_free_frame(AVFrame **frame);
 
         const char *av_get_media_type_string(enum AVMediaType media_type);

         int av_opt_get_int   (void *obj, const char *name, int search_flags, int64_t    *out_val);
         int av_opt_get_double(void *obj, const char *name, int search_flags, double     *out_val);
         """)


# The dreaded singleton. It is a necessary evil[1] and this is the reason why:
# https://bitbucket.org/cffi/cffi/issue/4/typeerror-initializer-for-ctype-double

# http://wiki.python.org/moin/PythonDecoratorLibrary#Singleton
def singleton(cls):
    """Use class as singleton."""

    cls.__new_original__ = cls.__new__

    @wraps(cls.__new__)
    def singleton_new(cls, *args, **kw):
        """the singleton workhorse."""
        
        _it = cls.__dict__.get('__it__')
        if _it is not None:
            return _it

        _it = cls.__new_original__(cls, *args, **kw)
        cls.__it__ = _it
        _it.__init_original__(*args, **kw)
        return _it

    cls.__new__ = singleton_new
    cls.__init_original__ = cls.__init__
    cls.__init__ = object.__init__

    return cls


@singleton
class FF:
    """
    FFMpeg abstraction objects.
    Needs to be a singleton because the FFI instance has to be
    one and exacly one.
    Do not use directly. Use get_handle() instead.
    """
    def __init__(self):
        self.ffi = cffi.FFI()
        _wire(self.ffi)
        self.lavc = self.ffi.dlopen("avcodec")
        self.lavf = self.ffi.dlopen("avformat")
        self.lavu = self.ffi.dlopen("avutil")

    def setup(self):
        """
        initialize the FFMpeg libraries.
        """
        # libav* already protects against multiple calls.
        self.lavc.avcodec_register_all()
        self.lavf.av_register_all()

    def versions(self):
        """
        fetch the version of the FFMpeg libraries.
        """
        return (self.lavc.avcodec_version(),
                self.lavf.avformat_version(),
                self.lavu.avutil_version())


def get_handle():
    """
    return a FF instance, taking care of bookkeeping.
    Safe to call multiple times.
    Do not instantiate FF directly.
    """
    return FF()


def setup():
    """
    return an already-setup ready-to-go FF instance.
    Safe to call multiple times.
    Do not instantiate FF directly.
    """
    ffh = FF()
    ffh.setup()
    return ffh
