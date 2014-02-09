void av_register_all(void);

/* frac = 'val + num / den'. must hold: 0 <= num < den. */
typedef struct AVFrac {
    int64_t val, num, den;
} AVFrac;

typedef struct AVInputFormat {
    const char *name;
    const char *long_name;
    int flags;
    /* ... */
} AVInputFormat;
typedef struct AVOutputFormat {
    const char *name;
    const char *long_name;
    const char *mime_type;
    const char *extensions;
    enum AVCodecID audio_codec;
    enum AVCodecID video_codec;
    enum AVCodecID subtitle_codec;
    int flags;
    /* ... */
} AVOutputFormat;
AVInputFormat *av_iformat_next(AVInputFormat *F);
AVOutputFormat *av_oformat_next(AVOutputFormat *F);

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

typedef struct AVStream {
    int index;
    int id;
    AVCodecContext *codec;
    void *priv_data;
    struct AVFrac pts;
    AVRational time_base;
    int64_t start_time;
    int64_t duration;
    int64_t nb_frames;
    int disposition;
    enum AVDiscard discard;
    AVRational sample_aspect_ratio;
    AVDictionary *metadata;
    AVRational avg_frame_rate;
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

AVStream *avformat_new_stream(AVFormatContext *s, const AVCodec *c);

AVFormatContext *avformat_alloc_context(void);
int avformat_alloc_output_context2(AVFormatContext **ctx, AVOutputFormat *oformat,
                                   const char *format_name, const char *filename);
void avformat_free_context(AVFormatContext *s);

int avformat_open_input(AVFormatContext **ps, const char *filename,
                        AVInputFormat *fmt, AVDictionary **options);
void avformat_close_input(AVFormatContext **s);
int avformat_find_stream_info(AVFormatContext *ic, AVDictionary **options);

int av_read_frame(AVFormatContext *s, AVPacket *pkt);

int av_seek_frame(AVFormatContext *s, int stream_index,
                  int64_t timestamp, int flags);
int avformat_seek_file(AVFormatContext *s, int stream_index,
                       int64_t min_ts, int64_t ts, int64_t max_ts, int flags);

int avformat_write_header(AVFormatContext *s, AVDictionary **options);
int av_write_frame(AVFormatContext *s, AVPacket *pkt);
int av_interleaved_write_frame(AVFormatContext *s, AVPacket *pkt);
int av_write_trailer(AVFormatContext *s);

