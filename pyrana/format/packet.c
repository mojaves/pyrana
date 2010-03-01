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
 * - move pts, dts, isKey as kwds?
 */


#define PACKET_NAME "Packet"
PyDoc_STRVAR(Packet_doc,
PACKET_NAME" - is an object to represent a packet.\n"
"It stores the raw packed data, and it has convertion\n"
"routines to/from regular Python strings.\n"
"Packet objects are immutable.");


static PyTypeObject PacketType;



int
PyrPacket_Check(PyObject *o)
{
    return PyObject_TypeCheck(o, &PacketType);
}


PyrPacketObject *
PyrPacket_NewEmpty(int size)
{
    PyrPacketObject *self = NULL;
    
    if (size) {
        self = PyObject_New(PyrPacketObject, &PacketType);
        if (self) {
            int err = av_new_packet(&(self->pkt), size);
            if (!err) {
                self->len = 0;
            } else {
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
            self->pkt.pts          = pkt->pts;
            self->pkt.dts          = pkt->dts;
            self->pkt.pos          = pkt->pos;
            self->pkt.flags        = pkt->flags;
            self->pkt.duration     = pkt->duration;
            self->pkt.stream_index = pkt->stream_index;
            /* FIXME: Is anything else needed? */
        }
    }
    return self;
}


static void
Packet_dealloc(PyrPacketObject *self)
{
    av_free_packet(&self->pkt);
    PyObject_Del((PyObject *)self);
}


static int
Packet_init(PyrPacketObject *self, PyObject *args, PyObject *kwds)
{
    char *buf = NULL;
    int err, ret = -1, streamid = 0, len = 0, isKey = 0;
    PY_LONG_LONG pts = AV_NOPTS_VALUE, dts = AV_NOPTS_VALUE;

    if (!PyArg_ParseTuple(args, "is#|LLi:init",
                          &streamid, &buf, &len,
                          &pts, &dts, &isKey)) {
        return -1; 
    }
    err = av_new_packet(&self->pkt, len);
    if (!err) {
        memcpy(self->pkt.data, buf, len);

        self->pkt.stream_index = streamid;
        self->pkt.pts          = pts;
        self->pkt.dts          = dts;
        if (isKey) {
            self->pkt.flags   |= PKT_FLAG_KEY;
        }

        ret = 0;
    }
    return ret;
}


static Py_ssize_t
Packet_getbuf(PyrPacketObject *self, Py_ssize_t segment, void **ptrptr)
{
    Py_ssize_t ret = -1;
    if (segment != 0) {
        PyErr_SetString(PyExc_SystemError,
                        "accessing non-existent string segment");
    } else {
        *ptrptr = self->pkt.data;
        ret     = self->pkt.size;
    }
    return ret;
}


static Py_ssize_t
Packet_getsegcount(PyrPacketObject *self, Py_ssize_t *lenp)
{
    if (lenp) {
        *lenp = self->pkt.size;
    }
    return 1;
}


static PyBufferProcs Packet_as_buffer = {
    (readbufferproc)Packet_getbuf,    /* bg_getreadbuffer  */
    0,                                /* bf_getwritebuffer */
    (segcountproc)Packet_getsegcount, /* bf_getsegcount    */
    (charbufferproc)Packet_getbuf,    /* bf_getcharbuffer  */
};



static PyObject *
PyrPacket_getdata(PyrPacketObject *self)
{
    /* FIXME: is that correct? */
    return PyString_FromStringAndSize((char *)self->pkt.data, self->pkt.size);
}


static PyObject *
PyrPacket_getsize(PyrPacketObject *self)
{
    return PyInt_FromLong(self->pkt.size);
}


static PyObject *
PyrPacket_getkey(PyrPacketObject *self)
{
    int isKey = 0;
    if (self->pkt.flags & PKT_FLAG_KEY) {
        isKey = 1;
    }
    return PyInt_FromLong(isKey);
}

static PyObject *
PyrPacket_getidx(PyrPacketObject *self)
{
    return PyInt_FromLong(self->pkt.stream_index);
}

static PyObject *
PyrPacket_getpts(PyrPacketObject *self)
{
    return PyLong_FromLongLong(self->pkt.pts);
}

static PyObject *
PyrPacket_getdts(PyrPacketObject *self)
{
    return PyLong_FromLongLong(self->pkt.dts);
}


static PyGetSetDef Packet_getsetlist[] =
{
    { "data",  (getter)PyrPacket_getdata, NULL, "packet data as binary string."  },
    { "size",  (getter)PyrPacket_getsize, NULL, "packet data length."            },
    { "isKey", (getter)PyrPacket_getkey,  NULL, "is it a reference packet?"      },
    { "idx",   (getter)PyrPacket_getidx,  NULL, "packet stream index,"           },
    { "pts",   (getter)PyrPacket_getpts,  NULL, "packet presentation timestamp." },
    { "dts",   (getter)PyrPacket_getdts,  NULL, "packet decoding timestamp."     },
    { NULL }, /* Sentinel */
};


static PyObject *
Packet_repr(PyrPacketObject *self)
{
    return PyString_FromFormat("<Packet idx=%i key=%s size=%i>",
                               self->pkt.stream_index,
                               (self->pkt.flags & PKT_FLAG_KEY) ?"T" :"F",
                               self->pkt.size);
} 


static PyTypeObject PacketType =
{
    PyObject_HEAD_INIT(NULL)
    0,
    PACKET_NAME,
    sizeof(PyrPacketObject),
    0,
    (destructor)Packet_dealloc,             /* tp_dealloc */
    0,                                      /* tp_print */
    0,                                      /* tp_getattr */
    0,                                      /* tp_setattr */
    0,                                      /* tp_compare */
    (reprfunc)Packet_repr,                  /* tp_repr */
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
    Packet_doc,                             /* tp_doc */
    0,                                      /* tp_traverse */
    0,                                      /* tp_clear */
    0,                                      /* tp_richcompare */
    0,                                      /* tp_weaklistoffset */
    0,                                      /* tp_iter */
    0,                                      /* tp_iternext */
    0,                                      /* tp_methods */
    0,                                      /* tp_members */
    Packet_getsetlist,                      /* tp_getset */
    0,                                      /* tp_base */
    0,                                      /* tp_dict */
    0,                                      /* tp_descr_get */
    0,                                      /* tp_descr_set */
    0,                                      /* tp_dictoffset */
    (initproc)Packet_init,                  /* tp_init */
    PyType_GenericAlloc,                    /* tp_alloc */
    PyType_GenericNew,                      /* tp_new */
};


int
PyrPacket_Setup(PyObject *m)
{
    if (PyType_Ready(&PacketType) < 0)
        return -1;

    PacketType.ob_type = &PyType_Type;
    Py_INCREF((PyObject *)&PacketType);
    PyModule_AddObject(m, PACKET_NAME, (PyObject *)&PacketType);
    return 0;
}


/* vim: set ts=4 sw=4 et */

