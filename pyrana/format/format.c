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


#define SUB_MODULE_PYDOC "Not yet"

#define SUB_MODULE_NAME MODULE_NAME".format"

#define IS_STREAMING_NAME "is_streaming"
PyDoc_STRVAR(is_streaming_doc,
IS_STREAMING_NAME"(name) - returns a boolean telling if format name is streamable"
);



static PyObject *InputFormats = NULL;
static PyObject *OutputFormats = NULL;

/*************************************************************************/

static PyObject *
BuildFormatNamesInput(void)
{
    PyObject *names = PyList_New(0);
    AVInputFormat *fmt = av_iformat_next(NULL);

    for (; fmt != NULL; fmt = av_iformat_next(fmt)) {
        PyObject *name = PyString_FromString(fmt->name);
        int err = PyList_Append(names, name);
        if (err) {
            Py_DECREF(names);
            return NULL;
        }
    }
    return names;
}

static PyObject *
BuildFormatNamesOutput(void)
{
    PyObject *names = PyList_New(0);
    AVOutputFormat *fmt = av_oformat_next(NULL);

    for (; fmt != NULL; fmt = av_oformat_next(fmt)) {
        PyObject *name = PyString_FromString(fmt->name);
        int err = PyList_Append(names, name);
        if (err) {
            Py_DECREF(names);
            return NULL;
        }
    }
    return names;
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
is_streaming(PyObject *self, PyObject *args)
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

/*************************************************************************/
static PyMethodDef format_functions[] =
{
	{
		IS_STREAMING_NAME,
		(PyCFunction)is_streaming,
		METH_VARARGS,
        is_streaming_doc
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

        PyModule_AddObject(m, "format", sm);
        ret = 0;
    }
    return ret;
}

/*************************************************************************/

/* vim: set ts=4 sw=4 et */

