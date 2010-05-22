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

/* FIXME: ugly */
#include "pyrana/format/demuxer.h"

#include "pyrana/video/decoder.h"
#include "pyrana/video/picture.h"
#include "pyrana/format/packet.h"



static PyTypeObject VDecoder_Type;


int
PyrCodec_Check(PyObject *o)
{
    return PyObject_TypeCheck(o, &VDecoder_Type);
}


#define VDECODER_PARAMS "params"
PyDoc_STRVAR(VDecoder_Params__doc__,
VDECODER_PARAMS" -> params\n"
"Returns dictionary containing the decoder configuration parameters.\n"
"The content depends by the format being decoded.\n"
);
static PyObject *
VDecoder_GetParams(PyrCodecObject *self)
{
    return NULL;
}


static PyObject *
VDecoder_DecodePacket(PyrCodecObject *self, AVPacket *pkt)
{
    int ret = 0, got_picture = 0, failed = 0;
    PyrVFrameObject *frame = NULL;
    AVFrame *pict = avcodec_alloc_frame();
    if (pict) {
        ret = avcodec_decode_video2(self->ctx, pict, &got_picture, pkt);

        if (ret < 0) {
            PyErr_Format(PyrExc_ProcessingError, "Decode error (%i)", ret);
            failed = 1;
        }
        else if (!got_picture) {
            PyErr_Format(PyrExc_NeedFeedError, "Bytes consumed (%i)", ret);
            failed = 1;
        }
        else {
            PyrImage img;
            memset(&img, 0, sizeof(PyrImage));
            img.width  = self->ctx->width;
            img.height = self->ctx->height;
            img.pix_fmt = self->ctx->pix_fmt;

            frame = PyrVFrame_NewFromAVFrame(pict, &img);
            if (!frame) {
                failed = 1;
            }
        }
    }
    if (failed) {
        av_free(pict);
    }
    return (PyObject *)frame;
}


#define VDECODER_DECODE "decode"
PyDoc_STRVAR(VDecoder_Decode__doc__,
VDECODER_DECODE"(Packet) -> Frame Object\n"
"decodes a complete encoded frame, enclosed in a Packet, into a Frame.\n"
"\n"
"Raises a NeedFeedError if fed with a Packet which doesn't contain a\n"
"complete frame. In that case the partial Packet is buffered internally."
);
static PyObject *
VDecoder_Decode(PyrCodecObject *self, PyObject *args)
{
    PyrPacketObject *packet = NULL;

    if (!PyArg_ParseTuple(args, "O:decode", &packet)) {
        return NULL;
    }

    if (!PyrPacket_Check((PyObject *)packet)) {
        PyErr_Format(PyrExc_ProcessingError, "Invalid packet");
        return NULL;
    }
    return VDecoder_DecodePacket(self, &(packet->pkt));
}

#define VDECODER_FLUSH "flush"
PyDoc_STRVAR(VDecoder_Flush__doc__,
VDECODER_FLUSH"() -> Frame Object\n"
"flushes any internal buffered Packets (see decode() doc) and returns\n"
"the corresponding Frame, one per call.\n"
"\n"
"Raises ProcessingError when all buffers have been flushed."
);
static PyObject *
VDecoder_Flush(PyrCodecObject *self, PyObject *args)
{
    PyObject *frame = NULL;
    AVPacket pkt;

    av_init_packet(&pkt);
    pkt.data = NULL;
    pkt.size = 0;

    frame = VDecoder_DecodePacket(self, &pkt);
    if (!frame) {
        PyErr_Format(PyrExc_ProcessingError, "All buffers flushed");
    }
    return frame;
}



static PyMethodDef VDecoder_methods[] =
{
    {
        VDECODER_DECODE,
        (PyCFunction)VDecoder_Decode,
        METH_VARARGS,
        VDecoder_Decode__doc__
    },
    {
        VDECODER_FLUSH,
        (PyCFunction)VDecoder_Flush,
        METH_VARARGS,
        VDecoder_Flush__doc__
    },
    { NULL, NULL }, /* Sentinel */
};


static void
VDecoder_Dealloc(PyrCodecObject *self)
{
    int ret = 0;
    /* FIXME: is that needed? Is that needed *here*? */
    /* avcodec_flush_buffers(self->ctx); */
    Py_XDECREF(self->params);

    if (self->codec) {
        ret = avcodec_close(self->ctx);
    }

    if (self->parent) {
        Py_DECREF(self->parent);
    }
    else if (self->ctx) {
        av_free(self->ctx);
    }
    PyObject_Del((PyObject *)self);
}

static void
VDecoder_SetParamsDefault(PyrCodecObject *self)
{
    if (self->codec->capabilities & CODEC_CAP_TRUNCATED) {
        self->ctx->flags |= CODEC_FLAG_TRUNCATED;
    }
    
    self->ctx->error_recognition = FF_ER_COMPLIANT;
    self->ctx->error_concealment = FF_EC_GUESS_MVS|FF_EC_DEBLOCK;

    return;
}

static void
VDecoder_SetParamsUser(PyrCodecObject *self, PyObject *params)
{
    /* TODO */
    return;
}

/* FIXME: ugly, inexpressive name */
static int
VDecoder_InitCodec(PyrCodecObject *self, AVCodec *codec, PyObject *params)
{
    int ret = -1;

    if (codec) {
        self->codec = codec;

        VDecoder_SetParamsDefault(self);
        VDecoder_SetParamsUser(self, params);

        ret = avcodec_open(self->ctx, self->codec);
        if (ret < 0) {
            PyErr_Format(PyrExc_SetupError,
                         "Could not initialize the '%s' codec.",
                         self->codec->name);
        }
    }
    return ret;
}

static int
VDecoder_ValidParams(PyObject *params)
{
    int valid = 1;
    if (params) {
        /* FIXME: relax this constraint. A map-like is enough. */
        if (!PyDict_Check(params)) {
            PyErr_Format(PyExc_TypeError, "'params' argument has to be a dict");
            valid = 0;
        }
    }
    return valid;
}

#define VDECODER_NAME "Decoder"
PyDoc_STRVAR(VDecoder__doc__,
VDECODER_NAME"(file [, name]) -> demuxer\n"
"Returns demuxer object."
);
static int
VDecoder_Init(PyrCodecObject *self, PyObject *args, PyObject *kwds)
{
    int err = -1;
    const char *name = NULL;
    PyObject *params = NULL;

    if (!PyArg_ParseTuple(args, "s|O:init", &name, &params)) { 
        PyErr_Format(PyrExc_SetupError, "Wrong arguments");
        return err; 
    }

    if (VDecoder_ValidParams(params)) {
        AVCodec *codec = avcodec_find_decoder_by_name(name);
        if (!codec) {
            PyErr_Format(PyrExc_SetupError, "unkown decoder `%s'", name);
        }
        else {
            self->parent = NULL;
            self->params = NULL;
            self->codec = NULL;
            self->ctx = avcodec_alloc_context();

            if (!self->ctx) {
                PyErr_Format(PyrExc_SetupError,
                            "unable to alloc the avcodec context");
            }
            else {
                err = VDecoder_InitCodec(self, codec, params);
                /* exception already set */
            }
        }
    }
    return err;
}

static PyrDemuxerObject *
PyrVDecoder_NarrowDemuxer(PyObject *dmx, int stream_id)
{
    PyrDemuxerObject *demux = NULL;

    if (!PyrDemuxer_Check(dmx)) {
        PyErr_Format(PyExc_TypeError, "'dmx' argument has to be a demuxer");
        return NULL;
    }
    demux = (PyrDemuxerObject *)dmx;
   
    if (stream_id < 0 || stream_id > demux->ic->nb_streams) {
        PyErr_Format(PyrExc_SetupError,
                     "'stream_id' value out of range [0,%i]",
                     demux->ic->nb_streams);
        return NULL;
    }

    return demux;
}

PyrCodecObject *
PyrVDecoder_NewFromDemuxer(PyObject *dmx, int stream_id, PyObject *params)
{
    PyrCodecObject *self = NULL;
    PyrDemuxerObject *demux = PyrVDecoder_NarrowDemuxer(dmx, stream_id);

    if (demux && VDecoder_ValidParams(params)) {
        self = PyObject_New(PyrCodecObject, &VDecoder_Type);
        if (self) {
            AVCodec *codec = NULL;
            int err = 0;

            self->params = NULL;
            self->parent = dmx;
            self->codec = NULL;
            self->ctx = demux->ic->streams[stream_id]->codec;
            
            codec = avcodec_find_decoder(self->ctx->codec_id);
            if (!codec) {
                PyErr_Format(PyrExc_SetupError,
                            "unkown decoder 0x%X",
                            self->ctx->codec_id);
            }
            else {
               err = VDecoder_InitCodec(self, codec, params);
                /* exception already set, if failed */
                if (!err) {
                    Py_INCREF(self->parent);
                }
            }
        }
    }
    return self;
}



static PyGetSetDef VDecoder_get_set[] =
{
    {
        VDECODER_PARAMS,
        (getter)VDecoder_GetParams,
        NULL,
        VDecoder_Params__doc__
    },
    { NULL }, /* Sentinel */
};

static PyTypeObject VDecoder_Type =
{
    PyObject_HEAD_INIT(NULL)
    0,
    VDECODER_NAME,
    sizeof(PyrCodecObject),
    0,
    (destructor)VDecoder_Dealloc,           /* tp_Dealloc */
    0,                                      /* tp_print */
    0,                                      /* tp_getattr */
    0,                                      /* tp_setattr */
    0,                                      /* tp_compare */
    0,                                      /* tp_repr */
    0,                                      /* tp_as_number */
    0,                                      /* tp_as_sequence */
    0,                                      /* tp_as_mapping */
    0,                                      /* tp_hash */
    0,                                      /* tp_call */
    0,                                      /* tp_str */
    0,                                      /* tp_getattro */
    0,                                      /* tp_setattro */
    0,                                      /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT|Py_TPFLAGS_BASETYPE, /* tp_flags */
    VDecoder__doc__,                        /* tp_doc */
    0,                                      /* tp_traverse */
    0,                                      /* tp_clear */
    0,                                      /* tp_richcompare */
    0,                                      /* tp_weaklistoffset */
    0,                                      /* tp_iter */
    0,                                      /* tp_iternext */
    VDecoder_methods,                       /* tp_methods */
    0,                                      /* tp_members */
    VDecoder_get_set,                       /* tp_getset */
    0,                                      /* tp_base */
    0,                                      /* tp_dict */
    0,                                      /* tp_descr_get */
    0,                                      /* tp_descr_set */
    0,                                      /* tp_dictoffset */
    (initproc)VDecoder_Init,                /* tp_init */
    PyType_GenericAlloc,                    /* tp_alloc */
    PyType_GenericNew,                      /* tp_new */
};


int
PyrVDecoder_Setup(PyObject *m)
{
    if (PyType_Ready(&VDecoder_Type) < 0) {
        return -1;
    }

    VDecoder_Type.ob_type = &PyType_Type;
    Py_INCREF((PyObject *)&VDecoder_Type);
    PyModule_AddObject(m, VDECODER_NAME, (PyObject *)&VDecoder_Type);
    return 0;
}


/* vim: set ts=4 sw=4 et */

