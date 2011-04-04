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

/* FIXME: ugly */
#include "pyrana/format/demuxer.h"

#include "pyrana/video/decoder.h"
#include "pyrana/video/picture.h"
#include "pyrana/format/packet.h"



#define VDECODER_PARAMS "params"
PyDoc_STRVAR(VDecoder_Params__doc__,
"a dictionary containing the decoder configuration parameters.\n"
"The content depends by the format being decoded.\n"
);
static PyObject *
VDecoder_GetParams(PyrCodecObject *self, void *closure)
{
    /* TODO */
    return NULL;
}

#define VDECODER_EXTRADATA "extra_data"
PyDoc_STRVAR(VDecoder_ExtraData__doc__,
"TODO"
);
static PyObject *
VDecoder_GetExtraData(PyrCodecObject *self, void *closure)
{
    /* TODO */
    return NULL;
}

static void
VDecoder_SetExtraData(PyrCodecObject *self, PyObject *value, void *closure)
{
    /* TODO */
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

    if (!PyArg_ParseTuple(args, "O:"VDECODER_DECODE, &packet)) {
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

static int
VDecoder_SetParamsDefault(PyrCodecObject *self)
{
    if (self->codec->capabilities & CODEC_CAP_TRUNCATED) {
        self->ctx->flags |= CODEC_FLAG_TRUNCATED;
    }
    
    self->ctx->error_recognition = FF_ER_COMPLIANT;
    self->ctx->error_concealment = FF_EC_GUESS_MVS|FF_EC_DEBLOCK;

    return 0;
}

static int
VDecoder_SetParamsUser(PyrCodecObject *self, PyObject *params)
{
    /* TODO */
    return 0;
}

static int
VDecoder_AreValidParams(PyrCodecObject *self, PyObject *params)
{
    /* just delegate it */
    return PyrVCodec_AreValidParams(self, params);
}

#define VDECODER_NAME "Decoder"
PyDoc_STRVAR(VDecoder__doc__,
VDECODER_NAME"(format_name [, params]) -> decoder\n"
"Returns decoder object."
);
static int
VDecoder_Init(PyrCodecObject *self, PyObject *args, PyObject *kwds)
{
    self->SetParamsDefault = VDecoder_SetParamsDefault;
    self->SetParamsUser = VDecoder_SetParamsUser;
    self->AreValidParams = VDecoder_AreValidParams;
        
    self->FindAVCodecByName = avcodec_find_decoder_by_name;

    self->tag = "decoder";

    return PyrVCodec_Init(self, args, kwds);
}


static PyMethodDef VDecoder_Methods[] =
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


static PyGetSetDef VDecoder_GetSet[] =
{
    {
        VDECODER_PARAMS,
        (getter)VDecoder_GetParams,
        NULL,
        VDecoder_Params__doc__
    },
    {
        VDECODER_EXTRADATA,
        (getter)VDecoder_GetExtraData,
        (setter)VDecoder_SetExtraData,
        VDecoder_ExtraData__doc__
    },
    { NULL }, /* Sentinel */
};

static PyType_Slot VDecoder_Slots[] =
{
    { Py_tp_dealloc,    PyrVCodec_Dealloc    },
    { Py_tp_init,       VDecoder_Init        },
    { Py_tp_methods,    VDecoder_Methods     },
    { Py_tp_getset,     VDecoder_GetSet      },
    { Py_tp_doc,        VDecoder__doc__      },
    { Py_tp_alloc,      PyType_GenericAlloc, },
    { Py_tp_new,        PyType_GenericNew    },
    { 0,                NULL                 }
};

static PyType_Spec VDecoder_Spec =
{
    VDECODER_NAME,
    sizeof(PyrCodecObject),
    0,
    Py_TPFLAGS_DEFAULT|Py_TPFLAGS_BASETYPE,
    VDecoder_Slots
};

/*************************************************************************/

static PyObject *VDecoder_Type = NULL;

int
PyrVDecoder_Check(PyObject *o)
{
    return (((void *)Py_TYPE(o)) == (void *)VDecoder_Type);
}

int
PyrVDecoder_Setup(PyObject *m)
{
    VDecoder_Type = PyType_FromSpec(&VDecoder_Spec);
    PyType_Ready((PyTypeObject *)VDecoder_Type);
    PyModule_AddObject(m, VDECODER_NAME, VDecoder_Type);
    return 0;
}

/*************************************************************************/


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

    if (demux && VDecoder_AreValidParams(self, params)) {
        self = PyObject_New(PyrCodecObject, (PyTypeObject *)VDecoder_Type);
        if (self) {
            AVCodec *codec = NULL;
            int err = 0;

            self->params = NULL;
            self->parent = dmx;
            self->ctx = demux->ic->streams[stream_id]->codec;
            
            codec = avcodec_find_decoder(self->ctx->codec_id);
            if (!codec) {
                PyErr_Format(PyrExc_SetupError,
                            "unkown decoder 0x%X",
                            self->ctx->codec_id);
            }
            else {
                err = PyrVCodec_Open(self, params, codec);
                /* exception already set, if failed */
                if (!err) {
                    Py_INCREF(self->parent);
                }
            }
        }
    }
    return self;
}

/* vim: set ts=4 sw=4 et */

