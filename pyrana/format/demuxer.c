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


#define DEMUXER_NAME "Demuxer"

#define READ_FRAME "readFrame"
PyDoc_STRVAR(readFrame_doc,
READ_FRAME"(streamid=ANY) -> Packet Object\n"
"reads and returns a new complete encoded frame (enclosed in a Packet)\n"
"from the demuxer. if the optional `streamid' argument is !ANY,\n"
"then returns a frame belonging to the specified streams.\n"
"\n"
"raises EndOfStreamError if either\n"
"- a stream id is specified, and such streams doesn't exists.\n"
"- the streams ends.");

#define OPEN_DECODER "openDecoder"
PyDoc_STRVAR(openDecoder_doc,
OPEN_DECODER"(streamid) -> Decoder instance\n"
"\n"
"create and returns a full-blown decoder Instance capable to decode the selected\n"
"stream. Like doing things manually, just easily.");

#define STREAMS "streams"
PyDoc_STRVAR(streams_doc,
STREAMS" -> streams\n"
"Returns list of streams within after the header is read in order they listed in a master stream.\n"
"It may contain the following attributes:\n"
"    type    - stream type ('audio' or 'video' or 'extra')\n"
"    bitrate - stream bitrate\n"
"    width   - picture width if any\n"
"    height  - picture height if any");

PyDoc_STRVAR(Demuxer_doc,
DEMUXER_NAME"(file [, name]) -> demuxer\n"
"Returns demuxer objecte.");




static PyTypeObject DemuxerType;



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
get_codec_name(AVCodecContext *ctx)
{
    AVCodec *c = avcodec_find_decoder(ctx->codec_id);
    if (c->name) {
        return c->name;
    }
    return ctx->codec_name;
} 

static void
Demuxer_FillStreamInfo(PyObject *streaminfo, AVCodecContext *ctx)
{
    Demuxer_SetAttribute(streaminfo, "name",
                         PyString_FromString(get_codec_name(ctx)));
    Demuxer_SetAttribute(streaminfo, "bitrate",
                         PyInt_FromLong(ctx->bit_rate));

    if (ctx->codec_type == CODEC_TYPE_VIDEO) {
        Demuxer_SetAttribute(streaminfo, "type",
                             PyString_FromString("video"));
        Demuxer_SetAttribute(streaminfo, "pixfmt",
                             PyString_FromString(avcodec_get_pix_fmt_name(ctx->pix_fmt)));
        if (ctx->width) {
            Demuxer_SetAttribute(streaminfo, "width",
                                 PyInt_FromLong(ctx->width));
            Demuxer_SetAttribute(streaminfo, "height",
                                 PyInt_FromLong(ctx->height));
        }
    }
    if (ctx->codec_type == CODEC_TYPE_AUDIO) {
        Demuxer_SetAttribute(streaminfo, "type",
                             PyString_FromString("audio"));
        Demuxer_SetAttribute(streaminfo, "channels",
                             PyInt_FromLong(ctx->channels));
        Demuxer_SetAttribute(streaminfo, "samplerate",
                             PyInt_FromLong(ctx->sample_rate));
        Demuxer_SetAttribute(streaminfo, "samplebytes",
                             PyInt_FromLong(2));
        // FIXME: BPP is hardcoded
    }
    if (ctx->extradata && ctx->extradata_size) {
        PyObject *obj = (PyObject *)PyrPacket_NewFromData(ctx->extradata,
                                                          ctx->extradata_size);
        Demuxer_SetAttribute(streaminfo, "extradata", obj);
    }
    return;
}


static PyObject *
Demuxer_GetStreams(PyrDemuxerObject *self)
{
    if (!self->streams) {    
        self->streams = PyTuple_New(self->ic->nb_streams);
        if (self->streams) {
            int i;

            for (i = 0; i < self->ic->nb_streams; i++) {
                PyObject *streaminfo = Py_None;
                AVCodecContext *ctx = self->ic->streams[i]->codec;

                if (ctx->codec_id) {
                    streaminfo = PyDict_New();
                    if (!streaminfo) {
                        PyErr_Format(PyExc_RuntimeError,
                                     "Unable to allocate stream info data");
                        return NULL;
                    }

                    Demuxer_FillStreamInfo(streaminfo, ctx);
                }
                PyTuple_SetItem(self->streams, i, streaminfo);
            }
        }
    }
    Py_INCREF(self->streams);
    return self->streams;
}


static PyObject *
Demuxer_OpenDecoder(PyrDemuxerObject *self, PyObject *args)
{
    PyObject *params = NULL;
    int streamid = 0;

    if (!PyArg_ParseTuple(args, "i|O", &streamid, &params)) { 
        PyErr_Format(PyrExc_SetupError, "Wrong arguments");
        return NULL; 
    }
    if (params && !PyDict_Check(params)) {
        PyErr_Format(PyExc_TypeError, "'params' argument has to be a dict");
        return NULL;
    }
 
    return NULL;
//    not yet
//    return (PyObject *)PyrDecoder_NewFromDemuxer(self, streamid, params);
}

static int
Demuxer_NextPacket(PyrDemuxerObject *self, int streamid, AVPacket *pkt)
{
    int ret = 0;

    while (pkt) {
        ret = av_read_frame(self->ic, pkt);

        if (ret < 0) {
            break;
        }
        if (streamid == PYRANA_STREAM_ANY || (pkt->stream_index == streamid)) {
            break;
        }

        av_free_packet(pkt);
    }

    return ret;
}

static PyObject *
Demuxer_ReadFrame(PyrDemuxerObject *self, PyObject *args)
{
    int streamid = PYRANA_STREAM_ANY, ret = 0;
    PyrPacketObject *pkt = NULL;
    AVPacket packet;

    if (!PyArg_ParseTuple(args, "|i:readFrame", &streamid)) {
        return NULL;
    }

    if (streamid != PYRANA_STREAM_ANY
     && (streamid < 0 ||  streamid > self->ic->nb_streams)) {
        PyErr_Format(PyrExc_EOSError,
                     "Invalid stream index (%i)", streamid);
        return NULL;
    }

    ret = Demuxer_NextPacket(self, streamid, &packet);

    if (ret < 0) {
        PyErr_Format(PyrExc_EOSError, "Stream end reached");
    } else {
        pkt = PyrPacket_NewFromAVPacket(&packet);
    }
    return (PyObject *)pkt;
}

/* ---------------------------------------------------------------------- */

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

    int ret = Demuxer_NextPacket(self, PYRANA_STREAM_ANY, &packet);

    if (ret < 0) {
        PyErr_Format(PyExc_StopIteration, "Stream end reached");
    } else {
        pkt = PyrPacket_NewFromAVPacket(&packet);
    }
    return (PyObject *)pkt;
}

/* ---------------------------------------------------------------------- */

static PyMethodDef Demuxer_methods[] =
{
    {
        READ_FRAME,
        (PyCFunction)Demuxer_ReadFrame,
        METH_VARARGS,
        readFrame_doc
    },
    {
        OPEN_DECODER,
        (PyCFunction)Demuxer_OpenDecoder,
        METH_VARARGS,
        openDecoder_doc
    },
    { NULL, NULL }, /* Sentinel */
};

/* ---------------------------------------------------------------------- */
static void
Demuxer_dealloc(PyrDemuxerObject *self)
{
    int err;
    
    if (self->ic) {
        av_close_input_file(self->ic); // FIXME
        self->ic = NULL;
    }
    err = PyrFileProto_DelMappedFile(self->key);
    if (!err) {
        Py_XDECREF(self->streams);
        Py_XDECREF(self->key);
        PyObject_Del((PyObject *)self);
    }
}

/* ---------------------------------------------------------------------- */
static int
Demuxer_init(PyrDemuxerObject *self, PyObject *args, PyObject *kwds)
{
    char filebuf[Pyr_FILE_KEY_LEN];
    AVInputFormat *ifmt = NULL;
    const char *name = NULL;
    PyObject *src = NULL;
    int seeking = 0, ret = -1;
    
    if (!PyArg_ParseTuple(args, "O|s:init", &src, &name)) { 
        PyErr_Format(PyrExc_SetupError, "Wrong arguments");
        return -1; 
    }
    
    if (!PyFile_Check(src)) {
        PyErr_Format(PyExc_TypeError,
                     "`File' argument is not a file-like object");
        return -1;
    }

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

    snprintf(filebuf, sizeof(filebuf), "%s://%s",
             seeking ?"pyfile" :"pypipe",
             PyString_AsString(self->key));
    ret = PyrFileProto_AddMappedFile(self->key, src);
    if (ret != 0) {
        PyErr_Format(PyExc_RuntimeError,
                     "Error setting up data source (binding)");
        return -1;
    }

    ret = av_open_input_file(&(self->ic), filebuf, ifmt, 0, NULL);
    if (ret != 0) {
        PyErr_Format(PyrExc_SetupError,
                    "libavformat error (at open=%i, filebuf=%s)",
                    ret, filebuf);
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

/* ---------------------------------------------------------------------- */
static PyGetSetDef Demuxer_getsetlist[] =
{
    { STREAMS, (getter)Demuxer_GetStreams, NULL, streams_doc },
    { NULL }, /* Sentinel */
};

/* ---------------------------------------------------------------------- */
static PyTypeObject DemuxerType =
{
    PyObject_HEAD_INIT(NULL)
    0,
    DEMUXER_NAME,
    sizeof(PyrDemuxerObject),
    0,
    (destructor)Demuxer_dealloc,            /* tp_dealloc */
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
    Demuxer_doc,                            /* tp_doc */
    0,                                      /* tp_traverse */
    0,                                      /* tp_clear */
    0,                                      /* tp_richcompare */
    0,                                      /* tp_weaklistoffset */
    (getiterfunc)Demuxer_GetIter,           /* tp_iter */
    (iternextfunc)Demuxer_Next,             /* tp_iternext */
    Demuxer_methods,                        /* tp_methods */
    0,                                      /* tp_members */
    Demuxer_getsetlist,                     /* tp_getset */
    0,                                      /* tp_base */
    0,                                      /* tp_dict */
    0,                                      /* tp_descr_get */
    0,                                      /* tp_descr_set */
    0,                                      /* tp_dictoffset */
    (initproc)Demuxer_init,                 /* tp_init */
    PyType_GenericAlloc,                    /* tp_alloc */
    PyType_GenericNew,                      /* tp_new */
};


int
PyrDemuxer_Setup(PyObject *m)
{
    if (PyType_Ready(&DemuxerType) < 0) {
        return -1;
    }

    DemuxerType.ob_type = &PyType_Type;
    Py_INCREF((PyObject *)&DemuxerType);
    PyModule_AddObject(m, DEMUXER_NAME, (PyObject *)&DemuxerType);
    return 0;
}


/* vim: set ts=4 sw=4 et */

