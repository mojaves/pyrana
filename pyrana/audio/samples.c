/*
 * Pyrana - python package for simple manipulation of multimedia files
 *
 * Copyright (c) <2010-2011> <Francesco Romani>
 *
 * This software is provided 'as-is', without any express or implied
 * warranty. In no event will the authors be held liable for any damages
 * arising from the use of this software.
 *
 * Permission is granted to anyone to use this software for any purpose,
 * including commercial applications, and to alter it and redistribute it
 * freely, subject to the following restrictions:
 *
 * 1. The origin of this software must not be misrepresented; you must not
 * claim that you wrote the original software. If you use this software
 * in a product, an acknowledgment in the product documentation would be
 * appreciated but is not required.
 *
 * 2. Altered source versions must be plainly marked as such, and must not be
 * misrepresented as being the original software.
 *
 * 3. This notice may not be removed or altered from any source
 * distribution.
 */

#include "pyrana/audio/samples.h"

/* TODO:
 * N/A
 */


/*************************************************************************/

enum {
    CHANNELS_MIN = 1,
    CHANNELS_MAX = 6,
    SAMPLE_RATE_MIN = 1000, /* kinda arbitrary */
    SAMPLE_RATE_MAX = 96000
};


typedef struct {
    enum SampleFormat fmt;
    const char *name;
    int sample_size; /* bytes */
} SampleFormatDesc;

static const SampleFormatDesc g_sample_fmts[] = {
    { SAMPLE_FMT_NONE, "none", 0 },
    { SAMPLE_FMT_U8, "u8", 1 },
    { SAMPLE_FMT_S16, "s16", 2 },
    { SAMPLE_FMT_S32, "s32", 4 },
    { SAMPLE_FMT_FLT, "float", 4 },
    { SAMPLE_FMT_DBL, "double", 8 },
    { SAMPLE_FMT_NB, NULL, 0 },
};


const char *
GetSampleFormatName(enum SampleFormat fmt)
{
    const char *name = NULL;
    int i = 0;

    for (i = 0; !name && g_sample_fmts[i].name != NULL; i++) {
        if (fmt == g_sample_fmts[i].fmt) {
            name = g_sample_fmts[i].name;
        }
    }

    return name;
}

int
GetSampleFormatSize(enum SampleFormat fmt)
{
    int size = 0;
    switch (fmt) {
      case SAMPLE_FMT_U8:
        size = 1;
        break;
      case SAMPLE_FMT_S16:
        size = 2;
        break;
      case SAMPLE_FMT_S32: /* fallthrough */
      case SAMPLE_FMT_FLT:
        size = 4;
        break;
      case SAMPLE_FMT_DBL:
        size = 8;
        break;
      case SAMPLE_FMT_NONE: /* fallthrough */
      case SAMPLE_FMT_NB: /* fallthrough */
      default:
        size = 0;
        break;
    }
    return size;
}


static PyObject *
BuildSampleFormatSet(const SampleFormatDesc g_sample_fmts[])
{
    PyObject *ret = NULL;
    PyObject *names = PySet_New(NULL);
    int i = 0, err = 0;

    for (i = 0; !err && g_sample_fmts[i].name != NULL; i++) { /* FIXME */
        PyObject *name = PyUnicode_FromString(g_sample_fmts[i].name);
        err = PySet_Add(names, name);
        if (err) {
            Py_DECREF(names);
            return NULL;
        }
    }

    ret = PyFrozenSet_New(names);
    Py_DECREF(names);
    return ret;
}


static enum SampleFormat
FindSampleFormatByName(const char *name)
{
    enum SampleFormat fmt = PIX_FMT_NB;
    if (name) {
        int i;
        /* FIXME */
        for (i = 0; fmt == PIX_FMT_NB && g_sample_fmts[i].name != NULL; i++) {
            if (!strcmp(g_sample_fmts[i].name, name)) {
                fmt = g_sample_fmts[i].fmt;
            }
        }
    }
    return fmt;
}


int
PyrSamples_Init(PyrSamples *S,
                enum SampleFormat sample_fmt,
                int sample_rate, int channels)
{
    int ret = -1;
    int size_bytes = PyrSamples_FrameSize(sample_fmt,
                                          sample_rate, channels);
    if (S && size_bytes > 0) {
        memset(S, 0, sizeof(*S));
        S->data = av_malloc(size_bytes);
        if (S->data) {
            S->size_bytes = size_bytes;
            S->sample_fmt = sample_fmt;
            S->sample_rate = sample_rate;
            S->channels = channels;
            ret = 0;
        }
    }
    return ret;
}

int
PyrSamples_Fini(PyrSamples *S)
{
    int ret = -1;
    if (S && S->data) {
        av_free(S->data);
        S->data = NULL;
    }
    return ret;
}

int
PyrSamples_Len(PyrSamples *S)
{
    int len = 0; /* FIXME */
    if (S) {
        len = S->size_bytes;
    }
    return len;
}

int
PyrSamples_FrameSize(enum SampleFormat sample_fmt,
                     int sample_rate, int channels)
{
    int samp_size = GetSampleFormatSize(sample_fmt);
    return samp_size * sample_rate * channels;
}

PyObject *
PyrAudio_NewSampleFormats(void)
{
    return BuildSampleFormatSet(g_sample_fmts);
}

PyObject *
PyrAudio_NewUserSampleFormats(void)
{
    return BuildSampleFormatSet(g_sample_fmts);
}


static void
AFrame_Dealloc(PyrAFrameObject *self)
{
    PyrSamples_Fini(&(self->samples));
    PyObject_Del((PyObject *)self);
}


static int
AFrame_ValidParams(PyrAFrameObject *self,
                   PyObject *sample_fmt_obj,
                   int channels, int sample_rate,
                   enum SampleFormat *sample_fmt)
{
    int valid = 1;

    if (channels < CHANNELS_MIN || channels > CHANNELS_MAX) {
        PyErr_Format(PyrExc_SetupError,
                     "bad channel count, not in range [%i, %i]",
                     CHANNELS_MIN, CHANNELS_MAX);
        valid = 0;
    }
    else if (sample_rate <= SAMPLE_RATE_MIN ||
             sample_rate > SAMPLE_RATE_MAX) {
        PyErr_Format(PyrExc_SetupError,
                     "bad sample rate, not in range [%i, %i]",
                     SAMPLE_RATE_MIN, SAMPLE_RATE_MAX);
        valid = 0;
    }
    else {
        PyObject *sample_fmt_name = PyUnicode_AsASCIIString(sample_fmt_obj);
        const char *name = PyBytes_AsString(sample_fmt_name); /* FIXME */
        enum SampleFormat s_fmt = FindSampleFormatByName(name);

        if (s_fmt == SAMPLE_FMT_NB) {
            PyErr_Format(PyrExc_SetupError,
                         "unrecognized sample format 0x%X", s_fmt);
            valid = 0;
        }
        if (sample_fmt) {
            *sample_fmt = s_fmt;
        }
    }
    return valid;
}



#define AFRAME_NAME "Frame"
PyDoc_STRVAR(AFrame__doc__,
AFRAME_NAME" - N/A\n"
""
);
static int
AFrame_Init(PyrAFrameObject *self, PyObject *args, PyObject *kwds)
{
    int ret = 0, len = 0, sample_rate = 0, channels = 0;
    char *buf = NULL;
    PY_LONG_LONG pts = 0;
    PyObject *sample_fmt_obj = NULL;
    enum SampleFormat sample_fmt = SAMPLE_FMT_NONE;

    if (!PyArg_ParseTuple(args, "s#LOii:init",
                          &buf, &len, &pts, &sample_fmt_obj,
                          &sample_rate, &channels)) {
        ret = -1;
    }
    else if (!AFrame_ValidParams(self, sample_fmt_obj, channels, sample_rate,
                                 &sample_fmt)) {
        ret = -1;
    }
    else {
        self->origin = Pyr_FRAME_ORIGIN_USER;
        self->pts = pts;
        ret = PyrSamples_Init(&(self->samples),
                              sample_fmt, sample_rate, channels);

        if (ret != 0) {
            PyErr_Format(PyrExc_SetupError,
                         "samples initialization failed");
        }
        else {
            int samples_len = PyrSamples_Len(&(self->samples));
            if (samples_len != len) {
                PyErr_Format(PyrExc_SetupError,
                            "inconsistent sample buffer"
                            " (given=%i, expected=%i)",
                            len, samples_len);
                PyrSamples_Fini(&(self->samples));
                ret = -1;
            }
            else {
                memcpy(self->samples.data, buf, len); /* FIXME */
            }
        }
    }

    return ret;
}

static PyObject *
AFrame_Repr(PyrAFrameObject *self)
{
    /* TODO */
    return NULL;
}


static int
AFrame_GetBuffer(PyrAFrameObject *self,
                 Py_buffer *view, int flags)
{
    if (flags != PyBUF_SIMPLE) {
        PyErr_Format(PyExc_BufferError, "unsupported request");
        return -1;
    }

    memset(view, 0, sizeof(Py_buffer));

    /* TODO */

    return -1;
}



static PyObject *
PyrAFrame_GetKey(PyrAFrameObject *self)
{
    return PyLong_FromLong(1); /* FIXME */
}


static PyObject *
PyrAFrame_GetPts(PyrAFrameObject *self)
{
    return PyLong_FromLongLong(self->pts);
}

static PyObject *
PyrAFrame_GetData(PyrAFrameObject *self)
{
    /* FIXME: is that correct? */
    return PyUnicode_FromStringAndSize((char *)self->samples.data,
                                      self->samples.size_bytes);
}

static PyObject *
PyrAFrame_GetSize(PyrAFrameObject *self)
{
    return PyLong_FromLong(self->samples.size_bytes);
}

static PyObject *
PyrAFrame_GetSampleFormat(PyrAFrameObject *self)
{
    const char *fmt_name = GetSampleFormatName(self->samples.sample_fmt);
    return PyUnicode_FromString(fmt_name);
}

static PyObject *
PyrAFrame_GetChannels(PyrAFrameObject *self)
{
    return PyLong_FromLong(self->samples.channels);
}

static PyObject *
PyrAFrame_GetSampleRate(PyrAFrameObject *self)
{
    return PyLong_FromLong(self->samples.sample_rate);
}

#define AFRAME_RESAMPLE_NAME "resample"
PyDoc_STRVAR(AFrame_Resample__doc__,
AFRAME_RESAMPLE_NAME" - N/A\n"
"");
static PyObject *
AFrame_Resample(PyrAFrameObject *self, PyObject *args)
{
    /* TODO */
    PyErr_Format(PyExc_NotImplementedError, "not yet");
    return NULL;
}


static PyGetSetDef AFrame_GetSet[] =
{
    {
        "is_key",
        (getter)PyrAFrame_GetKey,
        NULL,
        "reference frame flag"
    },
    {
        "pts",
        (getter)PyrAFrame_GetPts,
        NULL,
        "frame presentation timestamp."
    },
    {
        "data",
        (getter)PyrAFrame_GetData,
        NULL,
        "frame data as binary string."
    },
    {
        "size",
        (getter)PyrAFrame_GetSize,
        NULL,
        "frame size in bytes."
    },
    {
        "sample_format",
        (getter)PyrAFrame_GetSampleFormat,
        NULL,
        "frame sample format."
    },
    {
        "sample_rate",
        (getter)PyrAFrame_GetSampleRate,
        NULL,
        "frame sample rate."
    },
    {
        "channels",
        (getter)PyrAFrame_GetChannels,
        NULL,
        "frame channels."
    },
    {
        NULL, NULL, NULL, NULL
    }, /* Sentinel */
};

static PyBufferProcs AFrame_AsBuffer = {
    (getbufferproc)AFrame_GetBuffer, /* bf_getbuffer     */
    NULL /* bf_releasebuffer */
};


static PyMethodDef AFrame_Methods[] =
{
    {
        AFRAME_RESAMPLE_NAME,
        (PyCFunction)AFrame_Resample,
        METH_VARARGS,
        AFrame_Resample__doc__
    },
    { NULL, NULL }, /* Sentinel */
};

static PyType_Slot AFrame_Slots[] =
{
    { Py_tp_dealloc,    AFrame_Dealloc      },
    { Py_tp_repr,       AFrame_Repr         },
/*    { Py_tp_as_buffer,  &AFrame_AsBuffer     },*/
    { Py_tp_init,       AFrame_Init         },
    { Py_tp_methods,    AFrame_Methods      },
    { Py_tp_getset,     AFrame_GetSet       },
    { Py_tp_doc,        AFrame__doc__       },
    { Py_tp_alloc,      PyType_GenericAlloc },
    { Py_tp_new,        PyType_GenericNew   },
    { 0,                NULL                }
};

static PyType_Spec AFrame_Spec =
{
    AFRAME_NAME,
    sizeof(PyrAFrameObject),
    0,
    Py_TPFLAGS_DEFAULT|Py_TPFLAGS_BASETYPE,
    AFrame_Slots
};

/*************************************************************************/

static PyObject *AFrame_Type = NULL;

int
PyrAFrame_Check(PyObject *o)
{
    return (((void *)Py_TYPE(o)) == (void *)AFrame_Type);
}

int
PyrAFrame_Setup(PyObject *m)
{
    int ret = -1;
    AFrame_Type = PyType_FromSpec(&AFrame_Spec);
    if (AFrame_Type) {
        /* UGLY hack. But we really need the Buffer Protocol. */
        AFrame_Type->ob_type->tp_as_buffer = &AFrame_AsBuffer;
        PyType_Ready((PyTypeObject *)AFrame_Type);
        PyModule_AddObject(m, AFRAME_NAME, AFrame_Type);
        ret = 0;
    }
    return ret;
}

/*************************************************************************/

PyrAFrameObject *
PyrAFrame_NewEmpty(enum SampleFormat sample_fmt,
                   int sample_rate, int channels)
{
    int size_bytes = PyrSamples_FrameSize(sample_fmt,
                                          sample_rate, channels);
    PyrAFrameObject *self = NULL;

    if (size_bytes > 0) {
        self = PyObject_New(PyrAFrameObject, (PyTypeObject *)AFrame_Type);
        if (self) {
            int err = PyrSamples_Init(&(self->samples),
                                      sample_fmt, sample_rate, channels);
            if (!err) {
                self->origin = Pyr_FRAME_ORIGIN_UNKNOWN;
                self->pts = 0;
            }
            else {
                Py_DECREF(self);
                self = NULL;
            }
        }
    }
    return self;
}

PyrAFrameObject *
PyrAFrame_NewFromSamples(const PyrSamples *S)
{
    PyrAFrameObject *self = NULL;
    if (S) {
        self = PyrAFrame_NewEmpty(S->sample_fmt, S->sample_rate, S->channels);

        if (self) {
            memcpy(self->samples.data, S->data, S->size_bytes);
            self->samples.sample_fmt = S->sample_fmt;
        }
    }
    return self;
}

/* vim: set ts=4 sw=4 et */

