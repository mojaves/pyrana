void *av_malloc(size_t size);
void *av_mallocz(size_t size);
void av_free(void *ptr);

typedef struct AVRational {
     int num;
     int den;
} AVRational;

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
int av_get_bytes_per_sample(enum AVSampleFormat sample_fmt);

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

