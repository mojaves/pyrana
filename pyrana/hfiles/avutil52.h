void *av_malloc(size_t size);
void *av_mallocz(size_t size);
void av_free(void *ptr);

int av_strerror(int errnum, char *errbuf, size_t errbuf_size);

typedef struct AVRational {
     int num;
     int den;
} AVRational;

int64_t av_rescale_q(int64_t a, AVRational bq, AVRational cq);

const char *av_get_media_type_string(enum AVMediaType media_type);

int av_opt_get_int(void *obj, const char *name, int search_flags, int64_t *out_val);
int av_opt_get_double(void *obj, const char *name, int search_flags, double *out_val);

int av_opt_set_int(void *obj, const char *name, int64_t val, int search_flags);
int av_opt_set_double(void *obj, const char *name, double val, int search_flags);

typedef struct AVPixFmtDescriptor {
   const char *name;
   uint8_t nb_components;
   uint8_t log2_chroma_w;
   uint8_t log2_chroma_h;
   uint8_t flags;
   /* ... */
} AVPixFmtDescriptor;

const AVPixFmtDescriptor *av_pix_fmt_desc_get(enum AVPixelFormat pix_fmt);

/* frame.h */

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
    struct AVPanScan *pan_scan;
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
    struct AVDictionary *metadata;
    int decode_error_flags;
    int channels;
    int pkt_size;
} AVFrame;

/* imgutils.h */
int av_image_get_linesize(enum AVPixelFormat pix_fmt, int width, int plane);
int av_image_get_buffer_size(enum AVPixelFormat pix_fmt,
                             int width, int height, int align);

int av_image_alloc(uint8_t *pointers[4], int linesizes[4],
                   int w, int h, enum AVPixelFormat pix_fmt, int align);

/* mathematics.h */
int64_t av_rescale(int64_t a, int64_t b, int64_t c);
int64_t av_rescale_rnd(int64_t a, int64_t b, int64_t c, enum AVRounding);

/* channel_layout.h */
int av_get_channel_layout_nb_channels(uint64_t channel_layout);

/* samplefmt.h */
const char *av_get_sample_fmt_name(enum AVSampleFormat sample_fmt);
enum AVSampleFormat av_get_sample_fmt(const char *name);
enum AVSampleFormat av_get_alt_sample_fmt(enum AVSampleFormat sample_fmt, int planar);
enum AVSampleFormat av_get_packed_sample_fmt(enum AVSampleFormat sample_fmt);
enum AVSampleFormat av_get_planar_sample_fmt(enum AVSampleFormat sample_fmt);
char *av_get_sample_fmt_string(char *buf, int buf_size, enum AVSampleFormat sample_fmt);
int av_get_bytes_per_sample(enum AVSampleFormat sample_fmt);
int av_sample_fmt_is_planar(enum AVSampleFormat sample_fmt);
int av_samples_get_buffer_size(int *linesize, int nb_channels, int nb_samples,
                               enum AVSampleFormat sample_fmt, int align);
int av_samples_fill_arrays(uint8_t **audio_data, int *linesize,
                           const uint8_t *buf,
                           int nb_channels, int nb_samples,
                           enum AVSampleFormat sample_fmt, int align);
int av_samples_alloc(uint8_t **audio_data, int *linesize, int nb_channels,
                     int nb_samples, enum AVSampleFormat sample_fmt, int align);

