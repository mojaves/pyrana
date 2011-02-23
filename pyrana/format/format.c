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



#include "pyrana/format/format.h"

#include "pyrana/format/pyfileproto.h"
#include "pyrana/format/packet.h"
#include "pyrana/format/demuxer.h"
#include "pyrana/format/muxer.h"


#define FORMAT_SUBMODULE_PYDOC "Not yet"

#define FORMAT_SUBMODULE_NAME MODULE_NAME".format"



static PyObject *g_input_formats = NULL;
static PyObject *g_output_formats = NULL;



static PyObject *
BuildFormatNamesInput(void)
{
    PyObject *ret = NULL;
    PyObject *names = PySet_New(NULL);
    AVInputFormat *fmt = av_iformat_next(NULL);

    for (; fmt != NULL; fmt = av_iformat_next(fmt)) {
        PyObject *name = PyUnicode_FromString(fmt->name);
        int err = PySet_Add(names, name);
        if (err) {
            Py_DECREF(names);
            return NULL;
        }
    }

    ret = PyFrozenSet_New(names);
    Py_DECREF(names);
    return ret;
}

static PyObject *
BuildFormatNamesOutput(void)
{
    PyObject *ret = NULL;
    PyObject *names = PySet_New(NULL);
    AVOutputFormat *fmt = av_oformat_next(NULL);

    for (; fmt != NULL; fmt = av_oformat_next(fmt)) {
        PyObject *name = PyUnicode_FromString(fmt->name);
        int err = PySet_Add(names, name);
        if (err) {
            Py_DECREF(names);
            return NULL;
        }
    }

    ret = PyFrozenSet_New(names);
    Py_DECREF(names);
    return ret;
}


int
PyrFormat_NeedSeeking(const char *fmt)
{
    return 1;
}

static int
IsValidFormat(PyObject *fmts, const char *fmt)
{
    int ret = 0;
    PyObject *name = PyUnicode_FromString(fmt);
    ret = PySequence_Contains(fmts, name);
    Py_XDECREF(name);
    return ret;
}

int
PyrFormat_IsInput(const char *fmt)
{
    return IsValidFormat(g_input_formats, fmt);
}

int
PyrFormat_IsOutput(const char *fmt)
{
    return IsValidFormat(g_output_formats, fmt);
}


#define IS_STREAMABLE "IsStreamable"
PyDoc_STRVAR(IsStreamable__doc__,
IS_STREAMABLE"(name) - returns a boolean telling if format name is streamable"
);
static PyObject *
IsStreamable(PyObject *self, PyObject *args)
{
    const char *name = NULL;
    long res = 0;

    if (PyArg_ParseTuple(args, "s", &name)) {
        res = PyrFormat_NeedSeeking(name);
    }
    if (res) {
        Py_RETURN_TRUE;
    }
    Py_RETURN_FALSE;
}


#define FIND_STREAM "find_stream"
PyDoc_STRVAR(FindStream__doc__,
FIND_STREAM"(streams, streamid, media) - TODO"
);
/* this one should be probably written in python */
static PyObject *
FindStream(PyObject *self, PyObject *args)
{
    int retsid = 0;

    return PyLong_FromLong(retsid);
}


static PyMethodDef FormatFunctions[] =
{
    {
        IS_STREAMABLE,
        (PyCFunction)IsStreamable,
        METH_VARARGS,
        IsStreamable__doc__
    },
    {
        FIND_STREAM,
        (PyCFunction)FindStream,
        METH_VARARGS,
        FindStream__doc__
    },
    { NULL, NULL },
};

static struct PyModuleDef pyranaformatmodule = {
    PyModuleDef_HEAD_INIT,
    FORMAT_SUBMODULE_NAME,
    FORMAT_SUBMODULE_PYDOC,
    -1,
    FormatFunctions,
    NULL,
    NULL,
    NULL,
    NULL
};

int
PyrFormat_Setup(PyObject *m)
{
    int ret = -1;
    PyObject *sm = PyModule_Create(&pyranaformatmodule);
    if (sm) {
        PyrFileProto_Setup();

        g_input_formats  = BuildFormatNamesInput();
        g_output_formats = BuildFormatNamesOutput();

        PyModule_AddIntConstant(sm, "STREAM_ANY", Pyr_STREAM_ANY);
        PyModule_AddObject(sm, "input_formats", g_input_formats);
        PyModule_AddObject(sm, "output_formats", g_output_formats);

        PyrPacket_Setup(sm);
        PyrDemuxer_Setup(sm);
        PyrMuxer_Setup(sm);

        PyModule_AddObject(m, "format", sm);
        ret = 0;
    }
    return ret;
}


/* vim: set ts=4 sw=4 et */

