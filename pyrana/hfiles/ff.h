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

 typedef struct AVRational{
      int num;
      int den;
 } AVRational;

 typedef struct AVDictionary AVDictionary;
 typedef struct AVClass AVClass;
 typedef struct AVProgram AVProgram;
 typedef struct AVChapter AVChapter;
 typedef struct AVPanScan AVPanScan;

 typedef struct AVCodec AVCodec;

 typedef struct AVCodecContext {
    const AVClass *av_class;
    int log_level_offset;
    enum AVMediaType codec_type;
    const struct AVCodec *codec;
    char codec_name[32];
    enum AVCodecID codec_id;
    unsigned int codec_tag;
    unsigned int stream_codec_tag;
    /*attribute_deprecated*/ int sub_id;
    void *priv_data;
    struct AVCodecInternal *internal;
    void *opaque;
    int bit_rate;
    int bit_rate_tolerance;
    int global_quality;
    int compression_level;
    int flags;
    int flags2;
    uint8_t *extradata;
    int extradata_size;
    AVRational time_base;
    int ticks_per_frame;
    int delay;
    int width, height;
    int coded_width, coded_height;
    int gop_size;
    enum AVPixelFormat pix_fmt;
    int me_method;
    /* ... */
 } AVCodecContext;
 AVCodecContext *avcodec_alloc_context3(const AVCodec *codec);

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

 int avcodec_open2(AVCodecContext *avctx, const AVCodec *codec, AVDictionary **options);
 int avcodec_close(AVCodecContext *avctx);

 typedef struct AVFrame {
     uint8_t *data[8];
     int linesize[8];
     uint8_t **extended_data;
     int width, height;
     int nb_samples;
     int format;
     int key_frame;
     enum AVPictureType pict_type;
     uint8_t *base[8];
     AVRational sample_aspect_ratio;
     int64_t pts;
     int64_t pkt_pts;
     int64_t pkt_dts;
     int coded_picture_number;
     int display_picture_number;
     int quality;
     int reference;
     int8_t *qscale_table;
     int qstride;
     int qscale_type;
     uint8_t *mbskip_table;
     int16_t (*motion_val[2])[2];
     uint32_t *mb_type;
     short *dct_coeff;
     int8_t *ref_index[2];
     void *opaque;
     uint64_t error[8];
     int type;
     int repeat_pict;
     int interlaced_frame;
     int top_field_first;
     int palette_has_changed;
     int buffer_hints;
     AVPanScan *pan_scan;
     int64_t reordered_opaque;
     void *hwaccel_picture_private;
     struct AVCodecContext *owner;
     void *thread_opaque;
     uint8_t motion_subsample_log2;
     int sample_rate;
     uint64_t channel_layout;
     int64_t best_effort_timestamp;
     int64_t pkt_pos;
     int64_t pkt_duration;
     AVDictionary *metadata;
     int decode_error_flags;
     int channels;
     int pkt_size;
 } AVFrame;

 AVFrame *avcodec_alloc_frame(void);
 void avcodec_get_frame_defaults(AVFrame *frame);
 void avcodec_free_frame(AVFrame **frame);

 int av_frame_get_channels(const AVFrame *frame);
 int av_frame_get_sample_rate(const AVFrame *frame);

 int av_image_get_buffer_size(enum AVPixelFormat pix_fmt, int width, int height, int align);

 int avcodec_decode_video2(AVCodecContext *avctx, AVFrame *picture,
                           int *got_picture_ptr,
                           const AVPacket *avpkt);
 int avcodec_decode_audio4(AVCodecContext *avctx, AVFrame *frame,
                           int *got_frame_ptr,
                           const AVPacket *avpkt);

 const char *av_get_media_type_string(enum AVMediaType media_type);

 int av_opt_get_int(void *obj, const char *name, int search_flags, int64_t *out_val);
 int av_opt_get_double(void *obj, const char *name, int search_flags, double *out_val);

 typedef struct AVPixFmtDescriptor {
    const char *name;
    uint8_t nb_components;
    uint8_t log2_chroma_w;
    uint8_t log2_chroma_h;
    uint8_t flags;
    /* ... */
 } AVPixFmtDescriptor;

 const AVPixFmtDescriptor *av_pix_fmt_desc_get(enum AVPixelFormat pix_fmt);
