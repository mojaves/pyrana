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


#define SUB_MODULE_PYDOC "Not yet"

#define SUB_MODULE_NAME MODULE_NAME".format"

#define IS_STREAMING_NAME "is_streamable"
PyDoc_STRVAR(is_streamable_doc,
IS_STREAMING_NAME"(name) - returns a boolean telling if format name is streamable"
);

#define FIND_STREAM_NAME "find_stream"
PyDoc_STRVAR(find_stream_doc,
FIND_STREAM_NAME"(streams, streamid, media) - TODO"
);


static PyObject *InputFormats = NULL;
static PyObject *OutputFormats = NULL;

/*************************************************************************/

static PyObject *
BuildFormatNamesInput(void)
{
    PyObject *ret = NULL;
    PyObject *names = PySet_New(NULL);
    AVInputFormat *fmt = av_iformat_next(NULL);

    for (; fmt != NULL; fmt = av_iformat_next(fmt)) {
        PyObject *name = PyString_FromString(fmt->name);
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
        PyObject *name = PyString_FromString(fmt->name);
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


/*************************************************************************/
int
PyrFormat_NeedSeeking(const char *fmt)
{
    return 1;
}

static int
IsValidFormat(PyObject *fmts, const char *fmt)
{
    int ret = 0;
    PyObject *Name = PyString_FromString(fmt);
    ret = PySequence_Contains(fmts, Name);
    Py_XDECREF(Name);
    return ret;
}

int
PyrFormat_IsInput(const char *fmt)
{
    return IsValidFormat(InputFormats, fmt);
}

int
PyrFormat_IsOutput(const char *fmt)
{
    return IsValidFormat(OutputFormats, fmt);
}

/*************************************************************************/
static PyObject *
is_streamable(PyObject *self, PyObject *args)
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

/* this one should be probably written in python */
static PyObject *
find_stream(PyObject *self, PyObject *args)
{
    int retsid = -1;

    return PyInt_FromLong(retsid);
}


/*************************************************************************/
static PyMethodDef format_functions[] =
{
    {
        IS_STREAMING_NAME,
        (PyCFunction)is_streamable,
        METH_VARARGS,
        is_streamable_doc
    },
    {
        FIND_STREAM_NAME,
        (PyCFunction)find_stream,
        METH_VARARGS,
        find_stream_doc
    },
    { NULL, NULL },
};

int
PyrFormat_Setup(PyObject *m)
{
    int ret = -1;
    PyObject *sm = Py_InitModule3(SUB_MODULE_NAME,
                                  format_functions,
                                  SUB_MODULE_PYDOC);
    if (sm) {
        PyrFileProto_Setup();

        InputFormats  = BuildFormatNamesInput();
        OutputFormats = BuildFormatNamesOutput();

        PyModule_AddIntConstant(sm, "STREAM_ANY", PYRANA_STREAM_ANY);
        PyModule_AddObject(sm, "input_formats",  InputFormats);
        PyModule_AddObject(sm, "output_formats", OutputFormats);

        PyrPacket_Setup(sm);
        PyrDemuxer_Setup(sm);
        /*PyrMuxer_Setup(sm);*/
        /* intentionally and temporarily left out */

        PyModule_AddObject(m, "format", sm);
        ret = 0;
    }
    return ret;
}

/*************************************************************************/

/* vim: set ts=4 sw=4 et */

