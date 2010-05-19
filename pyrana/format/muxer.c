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

#include "pyrana/format/muxer.h"
#include "pyrana/format/packet.h"

#include "pyrana/format/pyfileproto.h"


static PyTypeObject MuxerType;


#define MUXER_NAME "Muxer"
PyDoc_STRVAR(Muxer_doc,
MUXER_NAME"(name) -> Muxer\n"
"\n"
"WRITEME."
);

#define ADD_STREAM_NAME "addStream" 
PyDoc_STRVAR(addStream_doc,
ADD_STREAM_NAME"(codec_id, [codec_params]) -> stream index\n"
"\n"
"Adds a stream to muxer. codec_params is an optional"
"codec parameters dictionary.\n"
);

#define WRITE_FRAME_NAME "writeFrame"
PyDoc_STRVAR(writeFrame_doc,
WRITE_FRAME_NAME"(Packet) -> None\n"
"\n"
"Write frame into on of the streams in muxer.\n"
);

#define GET_STREAM_PTS_NAME "getStreamPTS"
PyDoc_STRVAR(getStreamPTS_doc,
GET_STREAM_PTS_NAME"(stream_index) -> tuple of pts_val, pts_num, pts_den for stream\n"
);

#define FLUSH_NAME "flush"
PyDoc_STRVAR(flush_doc,
FLUSH_NAME"() -> flush muxer buffers\n"
);

#define WRITE_HEADER_NAME "writeHeader"
PyDoc_STRVAR(writeHeader_doc,
WRITE_HEADER_NAME"() -> write the header into the underlying stream\n"
"\n"
"If the format being muxed doesn't require an header, do nothing.\n"
);

#define WRITE_TRAILER_NAME "writeTrailer"
PyDoc_STRVAR(writeTrailer_doc,
WRITE_HEADER_NAME"() -> write the trailer into the underlying stream\n"
"\n"
"If the format being muxed doesn't require a trailer, do nothing.\n"
);



static int
Muxer_SetupCheck(PyrMuxerObject *self)
{
    if (!self->oc->nb_streams) {
        PyErr_Format(PyrExc_SetupError, "Muxer not properly initialized");
        return 0;
    }
    return 1;
}


static PyObject *
Muxer_AddStream(PyrMuxerObject *self, PyObject *args)
{
    PyObject *params = NULL;
    int streamid = -1;

    if (!PyArg_ParseTuple(args, "i|O:addStream", &streamid, &params)) {
        return NULL;
    }

    /* TODO */

    Py_RETURN_NONE;
}


static PyObject *
Muxer_GetStreamPTS(PyrMuxerObject *self, PyObject *args)
{
    PyObject *PTS = NULL;
    int streamid = -1;

    if (!Muxer_SetupCheck(self)) {
        /* exception already set, if any */
        return NULL;
    }

    if (!PyArg_ParseTuple(args, "i:getStreamPTS", &streamid)) {
        /* TODO exception? */
        return NULL;
    }

    if (streamid > self->oc->nb_streams || streamid < 0) {
        PyErr_Format(PyrExc_SetupError,  "Bad stream index");
    } else {
        PTS = Py_BuildValue("i,i,i",
                            self->oc->streams[streamid]->pts.val,
                            self->oc->streams[streamid]->pts.num,
                            self->oc->streams[streamid]->pts.den);
    }
    return PTS;
}


static PyObject *
Muxer_WriteHeader(PyrMuxerObject *self)
{
    if (!self->header_written) {
        int err = av_write_header(self->oc);
        if (!err) {
            self->header_written = 1;
        } else {
            /* FIXME: IOError can be also raised by lower levels of the stack */
            PyErr_Format(PyExc_IOError, "Error writing stream header");
            return NULL;
        }
    }
    Py_RETURN_NONE;
}


static PyObject *
Muxer_WriteTrailer(PyrMuxerObject *self)
{
    if (!self->trailer_written) {
        int err = av_write_trailer(self->oc);
        if (!err) {
            self->trailer_written = 1;
        } else {
            /* FIXME: IOError can be also raised by lower levels of the stack */
            PyErr_Format(PyExc_IOError, "Error writing stream trailer");
            return NULL;
        }
    }
    Py_RETURN_NONE;
}


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

    if (!PyArg_ParseTuple(args, "O:writeFrame", &obj)) {
        return NULL;
    }

    if (!PyrPacket_Check(obj)) {
        PyErr_Format(PyExc_TypeError,
                     WRITE_FRAME_NAME" argument must be a Packet object");
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
    } else {
        /* FIXME: IOError can be also raised by lower levels of the stack */
        PyErr_Format(PyExc_IOError, "Error writing frame data");
        return NULL;
    }

    Py_RETURN_NONE;
}



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
        ADD_STREAM_NAME,
        (PyCFunction)Muxer_AddStream,
        METH_VARARGS,
        addStream_doc
    },
    {
        WRITE_FRAME_NAME,
        (PyCFunction)Muxer_WriteFrame,
        METH_VARARGS,
        writeFrame_doc
    },
    {
        WRITE_HEADER_NAME,
        (PyCFunction)Muxer_WriteHeader,
        METH_NOARGS,
        writeHeader_doc
    },
    {
        WRITE_TRAILER_NAME,
        (PyCFunction)Muxer_WriteTrailer,
        METH_NOARGS,
        writeTrailer_doc
    },
    {
        GET_STREAM_PTS_NAME,
        (PyCFunction)Muxer_GetStreamPTS,
        METH_VARARGS,
        getStreamPTS_doc
    },
    {
        FLUSH_NAME,
        (PyCFunction)Muxer_Flush,
        METH_NOARGS,
        flush_doc
    },
    { NULL, NULL }, /* Sentinel */
};


static void
Muxer_dealloc(PyrMuxerObject *self)
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
Muxer_init(PyrMuxerObject *self, PyObject *args, PyObject *kwds)
{
    const char *name = NULL;
    int ret = -1;
    PyObject *src = NULL;

    if (!PyArg_ParseTuple(args, "O|s:init", &src, &name)) { 
        /* TODO */
        return -1; 
    }
    
    if (!PyFile_Check(src)) {
        /* TODO */
        return -1;
    }

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
        char filebuf[PYR_FILE_KEY_LEN + 1] = { '\0' };
        int seeking = 0;

        self->key = PyrFileProto_GetFileKey();
        if (!self->key) {
            /* TODO */
            return -1;
        }    

        snprintf(filebuf, sizeof(filebuf), "%s://%s",
                 seeking ?"pyfile" :"pypipe",
                 PyString_AsString(self->key));
        ret = PyrFileProto_AddMappedFile(self->key, src);
        if (ret != 0) {
            return -1;
        }

        strncpy(self->oc->filename, filebuf, PYR_FILE_KEY_LEN);
        ret = url_fopen(&(self->oc->pb), filebuf, URL_WRONLY);
        if (ret < 0) {
            /* FIXME */
        }
    }
    /* TODO */

    return 0;
}

/* ---------------------------------------------------------------------- */
static PyTypeObject MuxerType =
{
    PyObject_HEAD_INIT(NULL)
    0,
    MUXER_NAME,
    sizeof(PyrMuxerObject),
    0,
    (destructor)Muxer_dealloc,              /* tp_dealloc */
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
    Muxer_doc,                              /* tp_doc */
    0,                                      /* tp_traverse */
    0,                                      /* tp_clear */
    0,                                      /* tp_richcompare */
    0,                                      /* tp_weaklistoffset */
    0,                                      /* tp_iter */
    0,                                      /* tp_iternext */
    Muxer_methods,                          /* tp_methods */
    0,                                      /* tp_members */
    0,                                      /* tp_getset */
    0,                                      /* tp_base */
    0,                                      /* tp_dict */
    0,                                      /* tp_descr_get */
    0,                                      /* tp_descr_set */
    0,                                      /* tp_dictoffset */
    (initproc)Muxer_init,                   /* tp_init */
    0,                                      /* tp_alloc */
    PyType_GenericNew,                      /* tp_new */
};

int 
PyrMuxer_Setup(PyObject *m)
{
    if (PyType_Ready(&MuxerType) < 0) {
        return -1;
    }

    MuxerType.ob_type = &PyType_Type;
    Py_INCREF((PyObject *)&MuxerType);
    PyModule_AddObject(m, MUXER_NAME, (PyObject *)&MuxerType);
    return 0;
}

/* vim: set ts=4 sw=4 et */

