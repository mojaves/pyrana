typedef struct SwrContext SwrContext;

struct SwrContext *swr_alloc(void);

int swr_init(struct SwrContext *s);

struct SwrContext *swr_alloc_set_opts(struct SwrContext *s,
                                      int64_t out_ch_layout, enum AVSampleFormat out_sample_fmt, int out_sample_rate,
                                      int64_t  in_ch_layout, enum AVSampleFormat  in_sample_fmt, int  in_sample_rate,
                                      int log_offset, void *log_ctx);

void swr_free(struct SwrContext **s);

int swr_convert(struct SwrContext *s, uint8_t **out, int out_count,
                                const uint8_t **in , int in_count);

int64_t swr_next_pts(struct SwrContext *s, int64_t pts);

int swr_set_channel_mapping(struct SwrContext *s, const int *channel_map);

int swr_inject_silence(struct SwrContext *s, int count);

int64_t swr_get_delay(struct SwrContext *s, int64_t base);
