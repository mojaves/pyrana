void avcodec_register_all(void);

typedef struct AVBufferRef AVBufferRef;

/* AVPacket is part of the stable ABI. */
typedef struct AVPacket {
    AVBufferRef *buf;
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
typedef struct AVPanScan AVPanScan;

typedef struct AVFrame AVFrame;

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
    void (*draw_horiz_band)(struct AVCodecContext *s,
                            const AVFrame *src, int offset[8],
                            int y, int type, int height);
    enum AVPixelFormat (*get_format)(struct AVCodecContext *s,
                                     const enum AVPixelFormat * fmt);
    int max_b_frames;
    float b_quant_factor;
    int rc_strategy;
    int b_frame_strategy;
    float b_quant_offset;
    int has_b_frames;
    int mpeg_quant;
    float i_quant_factor;
    float i_quant_offset;
    float lumi_masking;
    float temporal_cplx_masking;
    float spatial_cplx_masking;
    float p_masking;
    float dark_masking;
    int slice_count;
    int prediction_method;
    int *slice_offset;
    AVRational sample_aspect_ratio;
    int me_cmp;
    int me_sub_cmp;
    int mb_cmp;
    int ildct_cmp;
    int dia_size;
    int last_predictor_count;
    int pre_me;
    int me_pre_cmp;
    int pre_dia_size;
    int me_subpel_quality;
    int dtg_active_format;
    int me_range;
    int intra_quant_bias;
    int inter_quant_bias;
    int slice_flags;
    int xvmc_acceleration;
    int mb_decision;
    uint16_t *intra_matrix;
    uint16_t *inter_matrix;
    int scenechange_threshold;
    int noise_reduction;
    int me_threshold;
    int mb_threshold;
    int intra_dc_precision;
    int skip_top;
    int skip_bottom;
    float border_masking;
    int mb_lmin;
    int mb_lmax;
    int me_penalty_compensation;
    int bidir_refine;
    int brd_scale;
    int keyint_min;
    int refs;
    int chromaoffset;
    int scenechange_factor;
    int mv0_threshold;
    int b_sensitivity;
    enum AVColorPrimaries color_primaries;
    enum AVColorTransferCharacteristic color_trc;
    enum AVColorSpace colorspace;
    enum AVColorRange color_range;
    enum AVChromaLocation chroma_sample_location;
    int slices;
    enum AVFieldOrder field_order;
    /* audio only */
    int sample_rate;
    int channels;
    enum AVSampleFormat sample_fmt;
    int frame_size;
    int frame_number;
    int block_align;
    int cutoff;
    int request_channels;
    uint64_t channel_layout;
    uint64_t request_channel_layout;
    /* ... */
} AVCodecContext;
AVCodecContext *avcodec_alloc_context3(const AVCodec *codec);

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
AVCodec *avcodec_find_encoder(enum AVCodecID id);
AVCodec *avcodec_find_encoder_by_name(const char *name);

enum AVMediaType avcodec_get_type(enum AVCodecID codec_id);
const char *avcodec_get_name(enum AVCodecID id);
int avcodec_is_open(AVCodecContext *s);
int av_codec_is_encoder(const AVCodec *codec);
int av_codec_is_decoder(const AVCodec *codec);

int avcodec_open2(AVCodecContext *avctx, const AVCodec *codec, AVDictionary **options);
int avcodec_close(AVCodecContext *avctx);

AVFrame *avcodec_alloc_frame(void);
void avcodec_get_frame_defaults(AVFrame *frame);
void avcodec_free_frame(AVFrame **frame);

int av_frame_get_channels(const AVFrame *frame);
int av_frame_get_sample_rate(const AVFrame *frame);

int avcodec_decode_video2(AVCodecContext *avctx, AVFrame *picture,
                          int *got_picture_ptr,
                          const AVPacket *avpkt);
int avcodec_decode_audio4(AVCodecContext *avctx, AVFrame *frame,
                          int *got_frame_ptr,
                          const AVPacket *avpkt);

int avcodec_encode_video2(AVCodecContext *avctx, AVPacket *avpkt,
                          const AVFrame *frame, int *got_packet_ptr);
int avcodec_encode_audio2(AVCodecContext *avctx, AVPacket *avpkt,
                          const AVFrame *frame, int *got_packet_ptr);
