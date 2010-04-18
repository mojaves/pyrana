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


#include "pyrana/video/decoder.h"
#include "pyrana/video/picture.h"
#include "pyrana/format/packet.h"



#define VDECODER_NAME "Decoder"

#define VDECODE "decode"
PyDoc_STRVAR(vDecode_doc,
VDECODE"(Packet) -> Frame Object\n"
"decodes a complete encoded frame, enclosed in a Packet, into a Frame.\n"
"\n"
"Raises a NeedFeedError if fed with a Packet which doesn't contain a\n"
"complete frame. In that case the partial Packet is buffered internally.");

#define VDFLUSH "flush"
PyDoc_STRVAR(vdFlush_doc,
VDFLUSH"() -> Frame Object\n"
"flushes any internal buffered Packets (see decode() doc) and returns\n"
"he corresponding Frames.\n"
"\n"
"Raises ProcessingError when all buffers have been flushed.");

#define VDPARAMS "params"
PyDoc_STRVAR(vdParams_doc,
VDPARAMS" -> params\n"
"Returns dictionary containing the decoder configuration parameters.\n"
"The content depends by the format being decoded.\n");


PyDoc_STRVAR(VDecoder_doc,
VDECODER_NAME"(file [, name]) -> demuxer\n"
"Returns demuxer objecte.");




static PyTypeObject VDecoderType;


int
PyrCodec_Check(PyObject *o)
{
    return PyObject_TypeCheck(o, &VDecoderType);
}


static PyObject *
VDecoder_GetParams(PyrCodecObject *self)
{
    return NULL;
}


static PyObject *
VDecoder_Decode(PyrCodecObject *self, PyObject *args)
{
    int ret = 0, got_picture = 0;
    PyrPacketObject *packet = NULL;
    PyrVFrameObject *frame = NULL;
    AVFrame pict;

    avcodec_get_frame_defaults(&pict);

    if (!PyArg_ParseTuple(args, "O:readFrame", &packet)) {
        return NULL;
    }

    if (!PyrPacket_Check((PyObject*)packet)) {
        PyErr_Format(PyrExc_ProcessingError,
                     "Invalid packet");
        return NULL;
    }

    ret = avcodec_decode_video2(self->ctx, &pict,
                                &got_picture, &packet->pkt);
    if (ret < 0) {
        PyErr_Format(PyrExc_ProcessingError, "Decode error (%i)", ret);
    } else if (!got_picture) {
        PyErr_Format(PyrExc_NeedFeedError, "Bytes consumed (%i)", ret);
    } else {
        frame = PyrVFrame_NewFromAVFrame(&pict);
    }
    return (PyObject *)frame;
}

static PyObject *
VDecoder_Flush(PyrCodecObject *self, PyObject *args)
{
    /* libavcodec doesn't do any buffering. Pretty easy, huh? */
    PyErr_Format(PyrExc_ProcessingError, "All buffers flushed");
    return NULL;
}


/* ---------------------------------------------------------------------- */

static PyMethodDef VDecoder_methods[] =
{
    {
        VDECODE,
        (PyCFunction)VDecoder_Decode,
        METH_VARARGS,
        vDecode_doc
    },
    {
        VDFLUSH,
        (PyCFunction)VDecoder_Flush,
        METH_VARARGS,
        vdFlush_doc
    },
    { NULL, NULL }, /* Sentinel */
};

/* ---------------------------------------------------------------------- */
static void
VDecoder_dealloc(PyrCodecObject *self)
{
    /* TODO */
}

/* ---------------------------------------------------------------------- */
static int
VDecoder_init(PyrCodecObject *self, PyObject *args, PyObject *kwds)
{
    return -1;
}

PyrCodecObject *PyrDecoder_NewFromDemuxer(PyObject *dmx,
                                          int streamid, PyObject *params)
{
    return NULL;
}



/* ---------------------------------------------------------------------- */
static PyGetSetDef VDecoder_getsetlist[] =
{
    { VDPARAMS, (getter)VDecoder_GetParams, NULL, vdParams_doc },
    { NULL }, /* Sentinel */
};

/* ---------------------------------------------------------------------- */
static PyTypeObject VDecoderType =
{
    PyObject_HEAD_INIT(NULL)
    0,
    VDECODER_NAME,
    sizeof(PyrCodecObject),
    0,
    (destructor)VDecoder_dealloc,           /* tp_dealloc */
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
    VDecoder_doc,                           /* tp_doc */
    0,                                      /* tp_traverse */
    0,                                      /* tp_clear */
    0,                                      /* tp_richcompare */
    0,                                      /* tp_weaklistoffset */
    0,                                      /* tp_iter */
    0,                                      /* tp_iternext */
    VDecoder_methods,                       /* tp_methods */
    0,                                      /* tp_members */
    VDecoder_getsetlist,                    /* tp_getset */
    0,                                      /* tp_base */
    0,                                      /* tp_dict */
    0,                                      /* tp_descr_get */
    0,                                      /* tp_descr_set */
    0,                                      /* tp_dictoffset */
    (initproc)VDecoder_init,                /* tp_init */
    PyType_GenericAlloc,                    /* tp_alloc */
    PyType_GenericNew,                      /* tp_new */
};


int
PyrCodec_Setup(PyObject *m)
{
    if (PyType_Ready(&VDecoderType) < 0) {
        return -1;
    }

    VDecoderType.ob_type = &PyType_Type;
    Py_INCREF((PyObject *)&VDecoderType);
    PyModule_AddObject(m, VDECODER_NAME, (PyObject *)&VDecoderType);
    return 0;
}


/* vim: set ts=4 sw=4 et */

