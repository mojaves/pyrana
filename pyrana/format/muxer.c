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

#include "pyrana/format/muxer.h"
#include "pyrana/format/packet.h"

#include "pyrana/format/pyfileproto.h"




#define MUXER_NAME "Muxer"
PyDoc_STRVAR(Muxer__doc__,
MUXER_NAME"(name) -> Muxer\n"
"\n"
"WRITEME."
);




static int
Muxer_SetupCheck(PyrMuxerObject *self)
{
    int ret = 1;
    if (!self->oc->nb_streams) {
        PyErr_Format(PyrExc_SetupError, "Muxer not properly initialized");
        ret = 0;
    }
    return ret;
}


#define ADD_STREAM "add_stream"
PyDoc_STRVAR(Muxer_AddStream__doc__,
ADD_STREAM"(codec_id, [codec_params]) -> stream index\n"
"\n"
"Adds a stream to muxer. codec_params is an optional"
"codec parameters dictionary.\n"
);
static PyObject *
Muxer_AddStream(PyrMuxerObject *self, PyObject *args)
{
    PyObject *params = NULL;
    int stream_id = -1;

    if (!PyArg_ParseTuple(args, "i|O:"ADD_STREAM, &stream_id, &params)) {
        return NULL;
    }

    /* TODO */

    Py_RETURN_NONE;
}


#define GET_PTS "get_pts"
PyDoc_STRVAR(Muxer_GetPts__doc__,
GET_PTS"(stream_index) -> tuple of pts_val, pts_num, pts_den for stream\n"
);
static PyObject *
Muxer_GetPts(PyrMuxerObject *self, PyObject *args)
{
    PyObject *PTS = NULL;
    int stream_id = -1;

    if (!Muxer_SetupCheck(self)) {
        /* exception already set, if any */
        return NULL;
    }

    if (!PyArg_ParseTuple(args, "i:"GET_PTS, &stream_id)) {
        /* TODO exception? */
        return NULL;
    }

    if (stream_id > self->oc->nb_streams || stream_id < 0) {
        PyErr_Format(PyrExc_SetupError,  "Bad stream index");
    }
    else {
        PTS = Py_BuildValue("i,i,i",
                            self->oc->streams[stream_id]->pts.val,
                            self->oc->streams[stream_id]->pts.num,
                            self->oc->streams[stream_id]->pts.den);
    }
    return PTS;
}


#define WRITE_HEADER "write_header"
PyDoc_STRVAR(Muxer_WriteHeader__doc__,
WRITE_HEADER"() -> write the header into the underlying stream\n"
"\n"
"If the format being muxed doesn't require an header, do nothing.\n"
);
static PyObject *
Muxer_WriteHeader(PyrMuxerObject *self)
{
    if (!self->header_written) {
        int err = av_write_header(self->oc);
        if (!err) {
            self->header_written = 1;
        }
        else {
            /* FIXME: IOError can be also raised by lower levels of the stack */
            PyErr_Format(PyExc_IOError, "Error writing stream header");
            return NULL;
        }
    }
    Py_RETURN_NONE;
}


#define WRITE_TRAILER "write_trailer"
PyDoc_STRVAR(Muxer_WriteTrailer__doc__,
WRITE_TRAILER"() -> write the trailer into the underlying stream\n"
"\n"
"If the format being muxed doesn't require a trailer, do nothing.\n"
);
static PyObject *
Muxer_WriteTrailer(PyrMuxerObject *self)
{
    if (!self->trailer_written) {
        int err = av_write_trailer(self->oc);
        if (!err) {
            self->trailer_written = 1;
        }
        else {
            /* FIXME: IOError can be also raised by lower levels of the stack */
            PyErr_Format(PyExc_IOError, "Error writing stream trailer");
            return NULL;
        }
    }
    Py_RETURN_NONE;
}


#define WRITE_FRAME "write_frame"
PyDoc_STRVAR(Muxer_WriteFrame__doc__,
WRITE_FRAME"(Packet) -> None\n"
"\n"
"Write frame into on of the streams in muxer.\n"
);
static PyObject *
Muxer_WriteFrame(PyrMuxerObject *self, PyObject *args)
{
    PyrPacketObject *pkt = NULL;
    PyObject *obj = NULL;
    int err = 0;

    if (!Muxer_SetupCheck(self)) {
        /* exception already set, if any */
        return NULL;
    }

    if (!PyArg_ParseTuple(args, "O:"WRITE_FRAME, &obj)) {
        return NULL;
    }

    if (!PyrPacket_Check(obj)) {
        PyErr_Format(PyExc_TypeError,
                     WRITE_FRAME" argument must be a Packet object");
        return NULL;
    }

    if (!Muxer_WriteHeader(self)) {
        /* exception already set, if any */
        return NULL;
    }

    pkt = (PyrPacketObject *)obj;
    if (pkt->pkt.stream_index < 0
     || pkt->pkt.stream_index > self->oc->nb_streams) {
        PyErr_Format(PyrExc_ProcessingError,
                     "Invalid stream index in packet data");
        return NULL;
    }

    err = av_write_frame(self->oc, &(pkt->pkt)); /* XXX: I sense danger... */
    if (!err) {
        self->frames++;
    }
    else {
        /* FIXME: IOError can be also raised by lower levels of the stack */
        PyErr_Format(PyExc_IOError, "Error writing frame data");
        return NULL;
    }

    Py_RETURN_NONE;
}



#define FLUSH "flush"
PyDoc_STRVAR(Muxer_Flush__doc__,
FLUSH"() -> flush muxer buffers\n"
);
static PyObject *
Muxer_Flush(PyrMuxerObject *self)
{
    /* TODO: actually flush packets */
    Muxer_WriteTrailer(self);
    Py_RETURN_NONE;
}


static PyMethodDef Muxer_methods[] =
{
    {
        ADD_STREAM,
        (PyCFunction)Muxer_AddStream,
        METH_VARARGS,
        Muxer_AddStream__doc__
    },
    {
        WRITE_FRAME,
        (PyCFunction)Muxer_WriteFrame,
        METH_VARARGS,
        Muxer_WriteFrame__doc__
    },
    {
        WRITE_HEADER,
        (PyCFunction)Muxer_WriteHeader,
        METH_NOARGS,
        Muxer_WriteHeader__doc__
    },
    {
        WRITE_TRAILER,
        (PyCFunction)Muxer_WriteTrailer,
        METH_NOARGS,
        Muxer_WriteTrailer__doc__
    },
    {
        GET_PTS,
        (PyCFunction)Muxer_GetPts,
        METH_VARARGS,
        Muxer_GetPts__doc__
    },
    {
        FLUSH,
        (PyCFunction)Muxer_Flush,
        METH_NOARGS,
        Muxer_Flush__doc__
    },
    { NULL, NULL }, /* Sentinel */
};


static void
Muxer_Dealloc(PyrMuxerObject *self)
{
    int err = 0;
    Muxer_Flush(self);

    err = PyrFileProto_DelMappedFile(self->key);
    if (!err) {
        Py_XDECREF(self->key);
        PyObject_Del((PyObject *)self);
    }
}


static int
Muxer_Init(PyrMuxerObject *self, PyObject *args, PyObject *kwds)
{
    const char *name = NULL;
    int ret = -1;
    PyObject *src = NULL;

    if (!PyArg_ParseTuple(args, "O|s:init", &src, &name)) {
        /* TODO */
        return -1;
    }

/*  TODOpy3: reimplement the check
    if (!PyFile_Check(src)) {
        return -1;
    }
*/
    self->oc = avformat_alloc_context();
    if (!self->oc) {
        /* TODO */
        return -1;
    }

    self->oc->oformat = av_guess_format(name, NULL, NULL); /* TODO */
    if (!self->oc->oformat) {
        /* TODO */
        return -1;
    }

    av_set_parameters(self->oc, NULL); /* TODO */

    /* open the output file, if needed */
    if (!(self->oc->oformat->flags & AVFMT_NOFILE)) {
        char filebuf[Pyr_FILE_KEY_LEN + 1] = { '\0' };
        int seeking = 0;

        self->key = PyrFileProto_GetFileKey();
        if (!self->key) {
            /* TODO */
            return -1;
        }

        PyOS_snprintf(filebuf, sizeof(filebuf), "%s://%s",
                      seeking ?"pyfile" :"pypipe",
                      PyBytes_AsString(self->key));
        ret = PyrFileProto_AddMappedFile(self->key, src);
        if (ret != 0) {
            return -1;
        }

        strncpy(self->oc->filename, filebuf, Pyr_FILE_KEY_LEN);
        ret = url_fopen(&(self->oc->pb), filebuf, URL_WRONLY);
        if (ret < 0) {
            /* FIXME */
        }
    }
    /* TODO */

    return 0;
}

static PyType_Slot Muxer_Slots[] =
{
    { Py_tp_dealloc,    Muxer_Dealloc       },
    { Py_tp_init,       Muxer_Init          },
    { Py_tp_methods,    Muxer_methods       },
    { Py_tp_doc,        Muxer__doc__        },
    { Py_tp_alloc,      PyType_GenericAlloc },
    { Py_tp_new,        PyType_GenericNew   },
    { 0,                NULL                }
};

static PyType_Spec Muxer_Spec =
{
    MUXER_NAME,
    sizeof(PyrMuxerObject),
    0,
    Py_TPFLAGS_DEFAULT|Py_TPFLAGS_BASETYPE,
    Muxer_Slots
};

/*************************************************************************/

static PyObject *Muxer_Type = NULL;

int
PyrMuxer_Check(PyObject *o)
{
    return (((void *)Py_TYPE(o)) == (void *)Muxer_Type);
}

int
PyrMuxer_Setup(PyObject *m)
{
    Muxer_Type = PyType_FromSpec(&Muxer_Spec);
    PyType_Ready((PyTypeObject *)Muxer_Type);
    PyModule_AddObject(m, MUXER_NAME, Muxer_Type);
    return 0;
}

/*************************************************************************/
/* vim: set ts=4 sw=4 et */

