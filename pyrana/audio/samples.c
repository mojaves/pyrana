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

#include "pyrana/audio/samples.h"

/* TODO:
 * N/A
 */


/*************************************************************************/

typedef struct {
    enum SampleFormat fmt;
    const char *name;
} SampleFormatDesc;

static const SampleFormatDesc g_sample_fmts[] = {
    { SAMPLE_FMT_NONE, "none" },
    { SAMPLE_FMT_U8, "u8" },
    { SAMPLE_FMT_S16, "s16" },
    { SAMPLE_FMT_S32, "s32" },
    { SAMPLE_FMT_FLT, "float" },
    { SAMPLE_FMT_DBL, "double" },
    { SAMPLE_FMT_NB, NULL },
};


const char *
GetSampleFormatName(enum SampleFormat fmt)
{
    const char *name = NULL;
    int i = 0;

    for (i = 0; !name && g_sample_fmts[i].name != NULL; i++) {
        if (fmt == g_sample_fmts[i].fmt) {
            name = g_sample_fmts[i].name;
        }
    }

    return name;
}

static PyObject *
BuildSampleFormatSet(const SampleFormatDesc g_sample_fmts[])
{
    PyObject *ret = NULL;
    PyObject *names = PySet_New(NULL);
    int i = 0, err = 0;

    for (i = 0; !err && g_sample_fmts[i].name != NULL; i++) { /* FIXME */
        PyObject *name = PyString_FromString(g_sample_fmts[i].name);
        err = PySet_Add(names, name);
        if (err) {
            Py_DECREF(names);
            return NULL;
        }
    }
 
    ret = PyFrozenSet_New(names);
    Py_DECREF(names);
    return ret;
}


static enum SampleFormat
FindSampleFormatByName(const char *name)
{
    enum SampleFormat fmt = PIX_FMT_NB;
    if (name) {
        int i;
        /* FIXME */
        for (i = 0; fmt == PIX_FMT_NB && g_sample_fmts[i].name != NULL; i++) {
            if (!strcmp(g_sample_fmts[i].name, name)) {
                fmt = g_sample_fmts[i].fmt;
            }
        }
    }
    return fmt;
}


int PyrSamples_Init(PyrSamples *S,
                    enum SampleFormat sample_fmt, int size_bytes)
{
    int ret = -1;
    if (S) {
        memset(S, 0, sizeof(*S));
        S->data = av_malloc(size_bytes);
        if (S->data) {
            S->size_bytes = size_bytes;
            S->sample_fmt = sample_fmt;
            ret = 0;
        }
    }
    return ret;
}

int PyrSamples_Fini(PyrSamples *S)
{
    int ret = -1;
    if (S && S->data) {
        av_freep(S->data);
    }
    return ret;
}


PyObject *
PyrAudio_NewSampleFormats(void)
{
    return BuildSampleFormatSet(g_sample_fmts);
}

PyObject *
PyrAudio_NewUserSampleFormats(void)
{
    return BuildSampleFormatSet(g_sample_fmts);
}


/*************************************************************************/


static PyTypeObject AFrame_Type;



int
PyrAFrame_Check(PyObject *o)
{
    return PyObject_TypeCheck(o, &AFrame_Type);
}


static void
AFrame_Dealloc(PyrAFrameObject *self)
{
    PyrSamples_Fini(&(self->samples));
    PyObject_Del((PyObject *)self);
}


#define AFRAME_NAME "Frame"
PyDoc_STRVAR(AFrame__doc__,
AFRAME_NAME" - N/A\n"
""
);
static int
AFrame_Init(PyrAFrameObject *self, PyObject *args, PyObject *kwds)
{
    int ret = 0, len = 0;
    char *buf = NULL;
    PY_LONG_LONG pts = 0;
    PyObject *sample_fmt_obj = NULL;

    if (!PyArg_ParseTuple(args, "s#LO:init",
                          &buf, &len, &pts, &sample_fmt_obj)) {
        ret = -1; 
    }
    else {
        const char *name = PyString_AsString(sample_fmt_obj); /* FIXME */
        enum SampleFormat sample_fmt = FindSampleFormatByName(name);

        if (sample_fmt == SAMPLE_FMT_NB) {
            PyErr_Format(PyrExc_SetupError,
                         "unrecognized sample format 0x%X", sample_fmt);
            ret = -1;
        }
        else {
            self->origin = Pyr_FRAME_ORIGIN_USER;
            self->pts = pts;
            ret = PyrSamples_Init(&(self->samples), sample_fmt, len);

            if (ret == 0) {
                memcpy(self->samples.data, buf, len); /* FIXME */
            }
        }
    }

    return ret;
}

static PyObject *
AFrame_Repr(PyrAFrameObject *self)
{
    return NULL;
} 


PyrAFrameObject *
PyrAFrame_NewEmpty(int size_bytes)
{
    PyrAFrameObject *self = NULL;

    if (size_bytes) {
        self = PyObject_New(PyrAFrameObject, &AFrame_Type);
        if (self) {
            int err = PyrSamples_Init(&(self->samples),
                                      SAMPLE_FMT_S16, size_bytes);
            if (!err) {
                self->origin = Pyr_FRAME_ORIGIN_UNKNOWN;
                self->pts = 0;
            }
            else {
                Py_DECREF(self);
                self = NULL;
            }
        }
    }
    return self;
}

PyrAFrameObject *
PyrAFrame_NewFromSamples(const PyrSamples *samp)
{
    PyrAFrameObject *self = NULL;
    if (samp) {
        self = PyrAFrame_NewEmpty(samp->size_bytes);

        if (self) {
            memcpy(self->samples.data, samp->data, samp->size_bytes);
            self->samples.sample_fmt = samp->sample_fmt;
        }
    }
    return self;
}


static Py_ssize_t
AFrame_GetBuf(PyrAFrameObject *self, Py_ssize_t segment, void **ptrptr)
{
    /* TODO */
    Py_ssize_t ret = -1;
    return ret;
}


static Py_ssize_t
AFrame_GetSegCount(PyrAFrameObject *self, Py_ssize_t *lenp)
{
    /* TODO */
    return 0;
}


static PyBufferProcs AFrame_as_buffer = {
    (readbufferproc)AFrame_GetBuf,    /* bf_getreadbuffer  */
    0,                                /* bf_getwritebuffer */
    (segcountproc)AFrame_GetSegCount, /* bf_getsegcount    */
    (charbufferproc)AFrame_GetBuf,    /* bf_getcharbuffer  */
};


static PyObject *
PyrAFrame_GetKey(PyrAFrameObject *self)
{
    return PyInt_FromLong(1); /* FIXME */
}


static PyObject *
PyrAFrame_GetPts(PyrAFrameObject *self)
{
    return PyLong_FromLongLong(self->pts);
}

static PyObject *
PyrAFrame_GetData(PyrAFrameObject *self)
{
    /* FIXME: is that correct? */
    return PyString_FromStringAndSize((char *)self->samples.data,
                                      self->samples.size_bytes);
}

static PyObject *
PyrAFrame_GetSize(PyrAFrameObject *self)
{
    return PyInt_FromLong(self->samples.size_bytes);
}

static PyObject *
PyrAFrame_GetSampleFormat(PyrAFrameObject *self)
{
    const char *fmt_name = GetSampleFormatName(self->samples.sample_fmt);
    return PyString_FromString(fmt_name);
}


static PyGetSetDef AFrame_get_set[] =
{
    { "is_key", (getter)PyrAFrame_GetKey, NULL, "reference frame flag" },
    { "pts", (getter)PyrAFrame_GetPts, NULL, "frame presentation timestamp." },
    { "data", (getter)PyrAFrame_GetData, NULL, "frame data as binary string." },
    { "size", (getter)PyrAFrame_GetSize, NULL, "frame size in bytes." }, 
    { "sample_format", (getter)PyrAFrame_GetSampleFormat, NULL,
                        "frame sample format." }, 
    { NULL }, /* Sentinel */
};


#define AFRAME_RESAMPLE_NAME "resample"
PyDoc_STRVAR(AFrame_Resample__doc__,
AFRAME_RESAMPLE_NAME" - N/A\n"
"");
static PyObject *
AFrame_Resample(PyrAFrameObject *self, PyObject *args)
{
    /* TODO */
    PyErr_Format(PyExc_NotImplementedError, "not yet");
    return NULL;
}


static PyMethodDef AFrame_methods[] =
{
    {
        AFRAME_RESAMPLE_NAME,
        (PyCFunction)AFrame_Resample,
        METH_VARARGS,
        AFrame_Resample__doc__
    },
    { NULL, NULL }, /* Sentinel */
};




static PyTypeObject AFrame_Type =
{
    PyObject_HEAD_INIT(NULL)
    0,
    AFRAME_NAME,
    sizeof(PyrAFrameObject),
    0,
    (destructor)AFrame_Dealloc,             /* tp_dealloc */
    0,                                      /* tp_print */
    0,                                      /* tp_getattr */
    0,                                      /* tp_setattr */
    0,                                      /* tp_compare */
    (reprfunc)AFrame_Repr,                  /* tp_repr */
    0,                                      /* tp_as_number */
    0,                                      /* tp_as_sequence */
    0,                                      /* tp_as_mapping */
    0,                                      /* tp_hash */
    0,                                      /* tp_call */
    0,                                      /* tp_str */
    0,                                      /* tp_getattro */
    0,                                      /* tp_setattro */
    &AFrame_as_buffer,                      /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT|Py_TPFLAGS_BASETYPE, /* tp_flags */
    AFrame__doc__,                          /* tp_doc */
    0,                                      /* tp_traverse */
    0,                                      /* tp_clear */
    0,                                      /* tp_richcompare */
    0,                                      /* tp_weaklistoffset */
    0,                                      /* tp_iter */
    0,                                      /* tp_iternext */
    AFrame_methods,                         /* tp_methods */
    0,                                      /* tp_members */
    AFrame_get_set,                         /* tp_getset */
    0,                                      /* tp_base */
    0,                                      /* tp_dict */
    0,                                      /* tp_descr_get */
    0,                                      /* tp_descr_set */
    0,                                      /* tp_dictoffset */
    (initproc)AFrame_Init,                  /* tp_init */
    PyType_GenericAlloc,                    /* tp_alloc */
    PyType_GenericNew,                      /* tp_new */
};


int
PyrAFrame_Setup(PyObject *m)
{
    if (PyType_Ready(&AFrame_Type) < 0)
        return -1;

    AFrame_Type.ob_type = &PyType_Type;
    Py_INCREF((PyObject *)&AFrame_Type);
    PyModule_AddObject(m, AFRAME_NAME, (PyObject *)&AFrame_Type);
    return 0;
}



/* vim: set ts=4 sw=4 et */

