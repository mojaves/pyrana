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

#include "pyrana/format/packet.h"

/* TODO:
 * - move pts, dts, is_key, ... as kwds?
 */



static PyTypeObject Packet_Type;



int
PyrPacket_Check(PyObject *o)
{
    return PyObject_TypeCheck(o, &Packet_Type);
}


PyrPacketObject *
PyrPacket_NewEmpty(int size)
{
    PyrPacketObject *self = NULL;
    
    if (size) {
        self = PyObject_New(PyrPacketObject, &Packet_Type);
        if (self) {
            int err = av_new_packet(&(self->pkt), size);
            if (!err) {
                self->len = 0;
            }
            else {
                Py_DECREF(self);
                self = NULL;
            }
        }
    }
    return self;

}


PyrPacketObject *
PyrPacket_NewFromData(const uint8_t *data, int size)
{
    PyrPacketObject *self = PyrPacket_NewEmpty(size);
    if (self) {
        memcpy(self->pkt.data, data, size);
        self->len = size;
    }
    return self;
}


PyrPacketObject * 
PyrPacket_NewFromAVPacket(AVPacket *pkt)
{
    PyrPacketObject *self = NULL;
    
    if (pkt && pkt->size) {
        self = PyrPacket_NewFromData(pkt->data, pkt->size);
        if (self) {
            self->pkt.pts = pkt->pts;
            self->pkt.dts = pkt->dts;
            self->pkt.pos = pkt->pos;
            self->pkt.flags = pkt->flags;
            self->pkt.duration = pkt->duration;
            self->pkt.stream_index = pkt->stream_index;
            /* FIXME: Is anything else needed? */
        }
    }
    return self;
}


static void
Packet_Dealloc(PyrPacketObject *self)
{
    av_free_packet(&self->pkt);
    PyObject_Del((PyObject *)self);
}


#define PACKET_NAME "Packet"
PyDoc_STRVAR(Packet__doc__,
PACKET_NAME" - is an object to represent a packet.\n"
"It stores the raw packed data, and it has convertion\n"
"routines to/from regular Python strings.\n"
"Packet objects are immutable."
);
static int
Packet_Init(PyrPacketObject *self, PyObject *args, PyObject *kwds)
{
    char *buf = NULL;
    int err, ret = -1, stream_id = 0, len = 0, is_key = 0;
    PY_LONG_LONG pts = AV_NOPTS_VALUE, dts = AV_NOPTS_VALUE;

    if (!PyArg_ParseTuple(args, "is#|LLi:init",
                          &stream_id, &buf, &len,
                          &pts, &dts, &is_key)) {
        return -1; 
    }
    err = av_new_packet(&self->pkt, len);
    if (!err) {
        memcpy(self->pkt.data, buf, len);

        self->pkt.stream_index = stream_id;
        self->pkt.pts = pts;
        self->pkt.dts = dts;
        if (is_key) {
            self->pkt.flags |= PKT_FLAG_KEY;
        }

        ret = 0;
    }
    return ret;
}


static Py_ssize_t
Packet_GetBuf(PyrPacketObject *self, Py_ssize_t segment, void **ptrptr)
{
    Py_ssize_t ret = -1;
    if (segment != 0) {
        PyErr_Format(PyExc_SystemError,
                     "accessing non-existent string segment");
    }
    else {
        *ptrptr = self->pkt.data;
        ret = self->pkt.size;
    }
    return ret;
}


static Py_ssize_t
Packet_GetSegCount(PyrPacketObject *self, Py_ssize_t *lenp)
{
    if (lenp) {
        *lenp = self->pkt.size;
    }
    return 1;
}


static PyBufferProcs Packet_as_buffer = {
    (readbufferproc)Packet_GetBuf,    /* bg_getreadbuffer  */
    0,                                /* bf_getwritebuffer */
    (segcountproc)Packet_GetSegCount, /* bf_getsegcount    */
    (charbufferproc)Packet_GetBuf,    /* bf_getcharbuffer  */
};



static PyObject *
PyrPacket_GetData(PyrPacketObject *self)
{
    /* FIXME: is that correct? */
    return PyString_FromStringAndSize((char *)self->pkt.data, self->pkt.size);
}


static PyObject *
PyrPacket_GetSize(PyrPacketObject *self)
{
    return PyInt_FromLong(self->pkt.size);
}


static PyObject *
PyrPacket_GetKey(PyrPacketObject *self)
{
    int is_key = 0;
    if (self->pkt.flags & PKT_FLAG_KEY) {
        is_key = 1;
    }
    return PyInt_FromLong(is_key);
}

static PyObject *
PyrPacket_GetStreamId(PyrPacketObject *self)
{
    return PyInt_FromLong(self->pkt.stream_index);
}

static PyObject *
PyrPacket_GetPts(PyrPacketObject *self)
{
    return PyLong_FromLongLong(self->pkt.pts);
}

static PyObject *
PyrPacket_GetDts(PyrPacketObject *self)
{
    return PyLong_FromLongLong(self->pkt.dts);
}


static PyGetSetDef Packet_get_set[] =
{
    { "data", (getter)PyrPacket_GetData, NULL, "packet data as binary string." },
    { "size", (getter)PyrPacket_GetSize, NULL, "packet data length." },
    { "is_key", (getter)PyrPacket_GetKey, NULL, "is it a reference packet?" },
    { "stream_id", (getter)PyrPacket_GetStreamId, NULL, "packet stream index." },
    { "pts", (getter)PyrPacket_GetPts, NULL, "packet presentation timestamp." },
    { "dts", (getter)PyrPacket_GetDts, NULL, "packet decoding timestamp." },
    { NULL }, /* Sentinel */
};


static PyObject *
Packet_Repr(PyrPacketObject *self)
{
    return PyString_FromFormat("<Packet idx=%i key=%s size=%i>",
                               self->pkt.stream_index,
                               (self->pkt.flags & PKT_FLAG_KEY) ?"T" :"F",
                               self->pkt.size);
} 


static PyTypeObject Packet_Type =
{
    PyObject_HEAD_INIT(NULL)
    0,
    PACKET_NAME,
    sizeof(PyrPacketObject),
    0,
    (destructor)Packet_Dealloc,             /* tp_Dealloc */
    0,                                      /* tp_print */
    0,                                      /* tp_getattr */
    0,                                      /* tp_setattr */
    0,                                      /* tp_compare */
    (reprfunc)Packet_Repr,                  /* tp_Repr */
    0,                                      /* tp_as_number */
    0,                                      /* tp_as_sequence */
    0,                                      /* tp_as_mapping */
    0,                                      /* tp_hash */
    0,                                      /* tp_call */
    0,                                      /* tp_str */
    0,                                      /* tp_getattro */
    0,                                      /* tp_setattro */
    &Packet_as_buffer,                      /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT|Py_TPFLAGS_BASETYPE, /* tp_flags */
    Packet__doc__,                          /* tp_doc */
    0,                                      /* tp_traverse */
    0,                                      /* tp_clear */
    0,                                      /* tp_richcompare */
    0,                                      /* tp_weaklistoffset */
    0,                                      /* tp_iter */
    0,                                      /* tp_iternext */
    0,                                      /* tp_methods */
    0,                                      /* tp_members */
    Packet_get_set,                         /* tp_getset */
    0,                                      /* tp_base */
    0,                                      /* tp_dict */
    0,                                      /* tp_descr_get */
    0,                                      /* tp_descr_set */
    0,                                      /* tp_dictoffset */
    (initproc)Packet_Init,                  /* tp_Init */
    PyType_GenericAlloc,                    /* tp_alloc */
    PyType_GenericNew,                      /* tp_new */
};


int
PyrPacket_Setup(PyObject *m)
{
    if (PyType_Ready(&Packet_Type) < 0)
        return -1;

    Packet_Type.ob_type = &PyType_Type;
    Py_INCREF((PyObject *)&Packet_Type);
    PyModule_AddObject(m, PACKET_NAME, (PyObject *)&Packet_Type);
    return 0;
}


/* vim: set ts=4 sw=4 et */

