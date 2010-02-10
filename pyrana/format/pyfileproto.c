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


#include "pyrana/format/pyfileproto.h"

#include <libavutil/avstring.h>
#include <libavformat/avio.h>

#include <unistd.h>
#include <stdlib.h>
#include <stdint.h>

/*************************************************************************/

static PyObject *FileMap = NULL;

/* 
 * Note: those bindings MUST have a lifecycle <= than the wrapping
 * Muxer/Demuxer object, so the INCREF/DECREF pair should'nt be
 * strictly needed.
 */

PyObject *
PyrFileProto_GetMappedFile(const char *filename)
{
    PyObject *obj = PyDict_GetItemString(FileMap, filename);
    Py_XINCREF(obj);
    return obj;
}

PyObject *
PyrFileProto_GetFileKey(void)
{
    static long int i = 0;
    PyObject *key = PyString_FromFormat("%ld", i++);
    return key;
}

int 
PyrFileProto_AddMappedFile(PyObject *key, PyObject *obj)
{
    if (!key || !obj) {
        return -1;
    }
    return PyDict_SetItem(FileMap, key, obj);
}

int 
PyrFileProto_DelMappedFile(PyObject *key)
{
    int ret = 0;
    if (key) {
        ret = PyDict_DelItem(FileMap, key);
    }
    return ret;
}

/*************************************************************************/


static int 
PyrPipe_Open(URLContext *h, const char *filename, int flags)
{
    av_strstart(filename, "pypipe://", &filename);
    PyObject *obj = PyrFileProto_GetMappedFile(filename);
    int ret = -1;
    if (obj) {
        h->priv_data   = obj;
        h->is_streamed = 1;
        ret            = 0;
    }
    return ret;
}

static int 
PyrPipe_Read(URLContext *h, unsigned char *buf, int size)
{
    FILE *f = PyFile_AsFile(h->priv_data);
    size_t r = fread(buf, 1, size, f);
    return (feof(f) || ferror(f)) ?-1 :r;
}

static int 
PyrPipe_Write(URLContext *h, unsigned char *buf, int size)
{
    FILE *f = PyFile_AsFile(h->priv_data);
    size_t w = fwrite(buf, 1, size, f);
    return (ferror(f)) ?-1 :w;
}

static int 
PyrPipe_Close(URLContext *h)
{
    PyObject *obj = h->priv_data;
    Py_XDECREF(obj); /* XDECREF: paranoia */
    return 0;
}

static int64_t
PyrPipe_Seek(URLContext *h, int64_t pos, int whence)
{
    return -1;
}

static URLProtocol PyrPipe_Protocol = {
    "PyrPipe",
    PyrPipe_Open,
    PyrPipe_Read,
    PyrPipe_Write,
    PyrPipe_Seek,
    PyrPipe_Close,
};

static int 
PyrFile_Open(URLContext *h, const char *filename, int flags)
{
    av_strstart(filename, "pyfile://", &filename);
    PyObject *obj = PyrFileProto_GetMappedFile(filename);
    int ret = -1;
    if (obj) {
        h->priv_data   = obj;
        h->is_streamed = 0;
        ret            = 0;
    }
    return ret;
}

/* XXX: use llseek? */
static int64_t
PyrFile_Seek(URLContext *h, int64_t pos, int whence)
{
    FILE *f = PyFile_AsFile(h->priv_data);
    return fseek(f, pos, whence);
}

static URLProtocol PyrFile_Protocol = {
    "PyrFile",
    PyrFile_Open,
    PyrPipe_Read,
    PyrPipe_Write,
    PyrFile_Seek,
    PyrPipe_Close,
};


/*************************************************************************/

int 
PyrFileProto_Setup(void)
{
    int ret = -1;
    FileMap = PyDict_New();
    if (FileMap) {
        av_register_protocol(&PyrFile_Protocol);
        av_register_protocol(&PyrPipe_Protocol);
        ret = 0;
    }
    return ret;
}

/*************************************************************************/

/* vim: set ts=4 sw=4 et */

