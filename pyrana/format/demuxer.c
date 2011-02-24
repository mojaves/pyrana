/*
 * Pyrana - python package for simple manipulation of multimedia files
 *
 * Copyright (c) <2010> <Francesco Romani>
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


#include "pyrana/format/demuxer.h"
#include "pyrana/format/packet.h"

#include "pyrana/format/pyfileproto.h"

#include "pyrana/video/decoder.h"


#define DEMUXER_NAME "Demuxer"


enum {
    Pyr_ERROR_MESSAGE_LEN = 256
};


static int
Demuxer_SetAttribute(PyObject *dict, const char *key, PyObject *val)
{
    int ret = -1;
    if (val) {
        PyDict_SetItemString(dict, key, val);
        ret = 0;
    }
    return ret;
}

static const char *
GetCodecName(AVCodecContext *ctx)
{
    AVCodec *c = avcodec_find_decoder(ctx->codec_id);
    if (c->name) {
        return c->name;
    }
    return ctx->codec_name;
}


static PyObject *
UnicodeFromASCII(const char *S)
{
    int L = strlen(S);
    return PyUnicode_DecodeASCII(S, L, "strict");
}

static void
Demuxer_FillStreamInfo(PyObject *stream_info, AVCodecContext *ctx)
{
    const char *as = NULL;

    as = GetCodecName(ctx);
    Demuxer_SetAttribute(stream_info, "name", UnicodeFromASCII(as));
    Demuxer_SetAttribute(stream_info, "bitrate",
                         PyLong_FromLong(ctx->bit_rate));
    Demuxer_SetAttribute(stream_info, "type",
                         PyLong_FromLong(ctx->codec_type));
    if (ctx->codec_type == CODEC_TYPE_VIDEO) {
        as = avcodec_get_pix_fmt_name(ctx->pix_fmt);
        Demuxer_SetAttribute(stream_info, "pixel_format",
                             UnicodeFromASCII(as));
        if (ctx->width) {
            Demuxer_SetAttribute(stream_info, "width",
                                 PyLong_FromLong(ctx->width));
            Demuxer_SetAttribute(stream_info, "height",
                                 PyLong_FromLong(ctx->height));
        }
    }
    if (ctx->codec_type == CODEC_TYPE_AUDIO) {
        Demuxer_SetAttribute(stream_info, "channels",
                             PyLong_FromLong(ctx->channels));
        /* for uniformity with bitrate */
        Demuxer_SetAttribute(stream_info, "samplerate",
                             PyLong_FromLong(ctx->sample_rate));
        Demuxer_SetAttribute(stream_info, "sample_bytes",
                             PyLong_FromLong(2));
        /* FIXME: BPP is hardcoded */
    }
    if (ctx->extradata && ctx->extradata_size) {
        PyObject *obj = (PyObject *)PyrPacket_NewFromData(ctx->extradata,
                                                          ctx->extradata_size);
        Demuxer_SetAttribute(stream_info, "extraData", obj);
    }
    return;
}

#define STREAMS "streams"
PyDoc_STRVAR(Demuxer_Streams__doc__,
STREAMS" -> streams\n"
"Returns list of streams within after the header is read in order they listed in a master stream.\n"
"It may contain the following attributes:\n"
"    type    - stream type ('audio' or 'video' or 'extra')\n"
"    bitrate - stream bitrate\n"
"    width   - picture width if any\n"
"    height  - picture height if any"
);
static PyObject *
Demuxer_GetStreams(PyrDemuxerObject *self)
{
    if (!self->streams) {
        self->streams = PyTuple_New(self->ic->nb_streams);
        if (self->streams) {
            int i;

            for (i = 0; i < self->ic->nb_streams; i++) {
                PyObject *stream_info = Py_None;
                AVCodecContext *ctx = self->ic->streams[i]->codec;

                if (ctx->codec_id) {
                    stream_info = PyDict_New();
                    if (!stream_info) {
                        PyErr_Format(PyExc_RuntimeError,
                                     "Unable to allocate stream info data");
                        return NULL;
                    }

                    Demuxer_FillStreamInfo(stream_info, ctx);
                }
                PyTuple_SetItem(self->streams, i, stream_info);
            }
        }
    }
    Py_INCREF(self->streams);
    return self->streams;
}


#define OPEN_DECODER "open_decoder"
PyDoc_STRVAR(Demuxer_OpenDecoder__doc__,
OPEN_DECODER"(stream_id) -> Decoder instance\n"
"\n"
"create and returns a full-blown decoder Instance capable to decode the selected\n"
"stream. Like doing things manually, just easily."
);
static PyObject *
Demuxer_OpenDecoder(PyrDemuxerObject *self, PyObject *args)
{
    PyObject *params = NULL;
    PyObject *dec = NULL;
    int stream_id = 0;

    if (!PyArg_ParseTuple(args, "i|O:"OPEN_DECODER, &stream_id, &params)) {
        PyErr_Format(PyrExc_SetupError, "Wrong arguments");
        return NULL;
    }
    if (params && !PyMapping_Check(params)) {
        PyErr_Format(PyExc_TypeError,
                     "'params' argument has to be a mapping");
        return NULL;
    }

    if (stream_id < 0 || stream_id > self->ic->nb_streams) {
        PyErr_Format(PyrExc_SetupError,
                     "'stream_id' value out of range [0,%i]",
                     self->ic->nb_streams);
        return NULL;
    }

    /* FIXME */
    if (self->ic->streams[stream_id]->codec->codec_type == CODEC_TYPE_VIDEO) {
        dec = (PyObject *)PyrVDecoder_NewFromDemuxer((PyObject*)self,
                                                     stream_id, params);
    } /* TODO */
    else {
        PyErr_Format(PyrExc_SetupError,
                     "unsupported codec type for stream %i",
                     stream_id);
        dec = NULL; /* enforce */
    }
    return dec;
}

static int
Demuxer_NextPacket(PyrDemuxerObject *self, int stream_id, AVPacket *pkt)
{
    int ret = 0;

    while (pkt) {
        ret = av_read_frame(self->ic, pkt);

        if (ret < 0) {
            break;
        }
        if (stream_id == Pyr_STREAM_ANY ||
           (pkt->stream_index == stream_id)) {
            break;
        }

        av_free_packet(pkt);
    }

    return ret;
}


#define READ_FRAME "read_frame"
PyDoc_STRVAR(Demuxer_ReadFrame__doc__,
READ_FRAME"(stream_id=ANY) -> Packet Object\n"
"reads and returns a new complete encoded frame (enclosed in a Packet)\n"
"from the demuxer. if the optional `stream_id' argument is !ANY,\n"
"then returns a frame belonging to the specified streams.\n"
"\n"
"raises EndOfStreamError if either\n"
"- a stream id is specified, and such streams doesn't exists.\n"
"- the streams ends."
);
static PyObject *
Demuxer_ReadFrame(PyrDemuxerObject *self, PyObject *args)
{
    int stream_id = Pyr_STREAM_ANY, ret = 0;
    PyrPacketObject *pkt = NULL;
    AVPacket packet;

    if (!PyArg_ParseTuple(args, "|i:"READ_FRAME, &stream_id)) {
        return NULL;
    }

    if (stream_id != Pyr_STREAM_ANY &&
       (stream_id < 0 ||  stream_id > self->ic->nb_streams)) {
        PyErr_Format(PyrExc_EOSError,
                     "Invalid stream index (%i)", stream_id);
        return NULL;
    }

    ret = Demuxer_NextPacket(self, stream_id, &packet);

    if (ret < 0) {
        PyErr_Format(PyrExc_EOSError, "Stream end reached");
    } else {
        pkt = PyrPacket_NewFromAVPacket(&packet);
    }
    return (PyObject *)pkt;
}


static PyObject *
Demuxer_GetIter(PyrDemuxerObject *self)
{
    Py_INCREF(self);
    return (PyObject *)self;
}

static PyObject *
Demuxer_Next(PyrDemuxerObject *self)
{
    PyrPacketObject *pkt = NULL;
    AVPacket packet;

    int ret = Demuxer_NextPacket(self, Pyr_STREAM_ANY, &packet);

    if (ret < 0) {
        PyErr_Format(PyExc_StopIteration, "Stream end reached");
    } else {
        pkt = PyrPacket_NewFromAVPacket(&packet);
    }
    return (PyObject *)pkt;
}



static PyMethodDef Demuxer_methods[] =
{
    {
        READ_FRAME,
        (PyCFunction)Demuxer_ReadFrame,
        METH_VARARGS,
        Demuxer_ReadFrame__doc__
    },
    {
        OPEN_DECODER,
        (PyCFunction)Demuxer_OpenDecoder,
        METH_VARARGS,
        Demuxer_OpenDecoder__doc__
    },
    { NULL, NULL }, /* Sentinel */
};


static void
Demuxer_Dealloc(PyrDemuxerObject *self)
{
    int err;

    if (self->ic) {
        av_close_input_file(self->ic); /* FIXME */
        self->ic = NULL;
    }
    err = PyrFileProto_DelMappedFile(self->key);
    if (!err) {
        Py_XDECREF(self->streams);
        Py_XDECREF(self->key);
        PyObject_Del((PyObject *)self);
    }
}


PyDoc_STRVAR(Demuxer__doc__,
DEMUXER_NAME"(file [, name]) -> demuxer\n"
"Returns demuxer objecte."
);
static int
Demuxer_Init(PyrDemuxerObject *self, PyObject *args, PyObject *kwds)
{
    char filebuf[Pyr_FILE_KEY_LEN] = { '\0' };
    AVInputFormat *ifmt = NULL;
    const char *name = NULL;
    PyObject *rawiobase = NULL;
    int seeking = 0, ret = -1;

    /* TODOpy3 format */
    if (!PyArg_ParseTuple(args, "O|s:init", &rawiobase, &name)) {
        PyErr_Format(PyrExc_SetupError, "Wrong arguments");
        return -1;
    }
/*  TODOpy3: reimplement the check
    if (!PyFile_Check(src)) {
        PyErr_Format(PyExc_TypeError,
                     "`File' argument is not a file-like object");
        return -1;
    }
*/
    if (name) {
        if (!PyrFormat_IsInput(name)) {
            PyErr_Format(PyrExc_UnsupportedError,
                         "unknown input format `%s'", name);
            return -1;
        }
        ifmt = av_find_input_format(name);
        if (!ifmt) {
            PyErr_Format(PyrExc_SetupError,
                         "libavformat error (found no format `%s')", name);
            return -1;
        }
        seeking = PyrFormat_NeedSeeking(name);
    }

    self->key = PyrFileProto_GetFileKey();
    if (!self->key) {
        PyErr_Format(PyExc_RuntimeError,
                     "Error setting up data source (mapping)");
        return -1;
    }

    PyOS_snprintf(filebuf, sizeof(filebuf), "%s://%s",
                  seeking ?"pyfile" :"pypipe",
                  PyBytes_AsString(self->key));
    ret = PyrFileProto_AddMappedFile(self->key, rawiobase);
    if (ret != 0) {
        PyErr_Format(PyExc_RuntimeError,
                     "Error setting up data source (binding)");
        return -1;
    }

    ret = av_open_input_file(&(self->ic), filebuf, ifmt, 0, NULL);
    if (ret != 0) {
        char errmsg[Pyr_ERROR_MESSAGE_LEN] = { '\0' };
        int averr = av_strerror(ret, errmsg, sizeof(errmsg));
        PyErr_Format(PyrExc_SetupError,
                    "libavformat error: %s (at open=%i:%i, filebuf=%s)",
                    errmsg, ret, averr, filebuf);
        return -1;
    }

    ret = av_find_stream_info(self->ic);
    if (ret < 0) {
        /* close it */
        PyErr_Format(PyrExc_SetupError,
                     "cannot find any streams in data source");
        return -1;
    }
    return 0;
}


static PyGetSetDef Demuxer_get_set[] =
{
    { STREAMS, (getter)Demuxer_GetStreams, NULL, Demuxer_Streams__doc__ },
    { NULL }, /* Sentinel */
};


static PyType_Slot DemuxerSlots[] =
{
    { Py_tp_dealloc,    Demuxer_Dealloc     },
    { Py_tp_iter,       Demuxer_GetIter     },
    { Py_tp_iternext,   Demuxer_Next        },
    { Py_tp_init,       Demuxer_Init        },
    { Py_tp_methods,    Demuxer_methods     },
    { Py_tp_getset,     Demuxer_get_set     },
    { Py_tp_doc,        Demuxer__doc__      },
    { Py_tp_new,        PyType_GenericNew   },
    { 0,                NULL                }
};

static PyType_Spec DemuxerSpec =
{
    DEMUXER_NAME,
    sizeof(PyrDemuxerObject),
    0,
    Py_TPFLAGS_DEFAULT|Py_TPFLAGS_BASETYPE,
    DemuxerSlots
};

/*************************************************************************/

static PyObject *DemuxerType = NULL;

int
PyrDemuxer_Check(PyObject *o)
{
    return (((void *)Py_TYPE(o)) == (void *)DemuxerType);
}

int
PyrDemuxer_Setup(PyObject *m)
{
    DemuxerType = PyType_FromSpec(&DemuxerSpec);
    PyModule_AddObject(m, DEMUXER_NAME, DemuxerType);
    return 0;
}

/*************************************************************************/
/* vim: set ts=4 sw=4 et */

