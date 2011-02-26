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

#include "pyrana/format/packet.h"

/* TODO:
 * - move pts, dts, is_key, ... as kwds?
 */



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
    Py_buffer pybuf;
    int err, ret = -1, stream_id = 0, is_key = 0;
    PY_LONG_LONG pts = AV_NOPTS_VALUE, dts = AV_NOPTS_VALUE;

    if (!PyArg_ParseTuple(args, "is*|LLi:init",
                          &stream_id, &pybuf,
                          &pts, &dts, &is_key)) {
        return -1;
    }
    /* TODOpy3: ndim > 0 */
    err = av_new_packet(&self->pkt, pybuf.len);
    if (!err) {
        memcpy(self->pkt.data, pybuf.buf, pybuf.len);

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


static int
Packet_GetBuffer(PyrPacketObject *self,
                 Py_buffer *view, int flags)
{
    if (flags != PyBUF_SIMPLE) {
        PyErr_Format(PyExc_BufferError, "unsupported request");
        return -1;
    }

    memset(view, 0, sizeof(Py_buffer));
    view->buf = self->pkt.data;
    view->len = self->pkt.size;
    view->readonly = 1;
    view->format = "B";
    view->ndim = 0;

    return 0;
}


static PyObject *
PyrPacket_GetData(PyrPacketObject *self, void *closure)
{
    /* FIXME: is that correct? */
    return PyBytes_FromStringAndSize((char *)self->pkt.data, self->pkt.size);
}


static PyObject *
PyrPacket_GetSize(PyrPacketObject *self, void *closure)
{
    return PyLong_FromLong(self->pkt.size);
}


static PyObject *
PyrPacket_GetKey(PyrPacketObject *self, void *closure)
{
    int is_key = 0;
    if (self->pkt.flags & PKT_FLAG_KEY) {
        is_key = 1;
    }
    return PyLong_FromLong(is_key);
}

static PyObject *
PyrPacket_GetStreamId(PyrPacketObject *self, void *closure)
{
    return PyLong_FromLong(self->pkt.stream_index);
}

static PyObject *
PyrPacket_GetPts(PyrPacketObject *self, void *closure)
{
    return PyLong_FromLongLong(self->pkt.pts);
}

static PyObject *
PyrPacket_GetDts(PyrPacketObject *self, void *closure)
{
    return PyLong_FromLongLong(self->pkt.dts);
}


static PyObject *
Packet_Repr(PyrPacketObject *self)
{
    /* TODOpy3: is that correct? */
    return PyUnicode_FromFormat("<Packet idx=%i key=%s size=%i>",
                                self->pkt.stream_index,
                                (self->pkt.flags & PKT_FLAG_KEY) ?"T" :"F",
                                self->pkt.size);
}


static PyBufferProcs Packet_AsBuffer = {
    (getbufferproc)Packet_GetBuffer, /* bf_getbuffer     */
    NULL /* bf_releasebuffer */
};

static PyGetSetDef Packet_GetSet[] =
{
    {
        "data",
        (getter)PyrPacket_GetData,
        NULL,
        "packet data as bytes (copy)."
    },
    {
        "size",
        (getter)PyrPacket_GetSize,
        NULL,
        "packet data length."
    },
    {
        "is_key",
        (getter)PyrPacket_GetKey,
        NULL,
        "is it a reference packet?"
    },
    {
        "stream_id",
        (getter)PyrPacket_GetStreamId,
        NULL,
        "packet stream index."
    },
    {
        "pts",
        (getter)PyrPacket_GetPts,
        NULL,
        "packet presentation timestamp."
    },
    {
        "dts",
        (getter)PyrPacket_GetDts,
        NULL,
        "packet decoding timestamp."
    },
    {
        NULL, NULL, NULL, NULL
    }, /* Sentinel */
};

static PyType_Slot Packet_Slots[] =
{
    { Py_tp_dealloc,    Packet_Dealloc       },
    { Py_tp_init,       Packet_Init          },
    { Py_tp_repr,       Packet_Repr          },
/*    { Py_tp_as_buffer,  &Packet_AsBuffer    },*/
    { Py_tp_getset,     Packet_GetSet        },
    { Py_tp_doc,        Packet__doc__        },
    { Py_tp_alloc,      PyType_GenericAlloc, },
    { Py_tp_new,        PyType_GenericNew    },
    { 0,                NULL                 }
};

static PyType_Spec Packet_Spec =
{
    PACKET_NAME,
    sizeof(PyrPacketObject),
    0,
    Py_TPFLAGS_DEFAULT|Py_TPFLAGS_BASETYPE,
    Packet_Slots
};

/*************************************************************************/

static PyObject *Packet_Type = NULL;

int
PyrPacket_Check(PyObject *o)
{
    return (((void *)Py_TYPE(o)) == (void *)Packet_Type);
}

int
PyrPacket_Setup(PyObject *m)
{
    int ret = -1;
    Packet_Type = PyType_FromSpec(&Packet_Spec);
    if (Packet_Type) {
        /* UGLY hack. But we really need the Buffer Protocol. */
        Packet_Type->ob_type->tp_as_buffer = &Packet_AsBuffer;
        PyType_Ready((PyTypeObject *)Packet_Type);
        PyModule_AddObject(m, PACKET_NAME, Packet_Type);
        ret = 0;
    }
    return ret;
}

/*************************************************************************/

PyrPacketObject *
PyrPacket_NewEmpty(int size)
{
    PyrPacketObject *self = NULL;

    if (size) {
        self = PyObject_New(PyrPacketObject, (PyTypeObject*)Packet_Type);
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

/*************************************************************************/
/* vim: set ts=4 sw=4 et */

