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

#include "pyrana/pyrana_internal.h"


void
PyrVCodec_Dealloc(PyrCodecObject *self)
{
    int ret = 0;

    Py_XDECREF(self->params);

    if (self->codec) {
        ret = avcodec_close(self->ctx);
    }

    if (self->parent) {
        Py_DECREF(self->parent);
    }
    else if (self->ctx) {
        av_free(self->ctx);
    }
    PyObject_Del((PyObject *)self);
}

int
PyrVCodec_Open(PyrCodecObject *self, PyObject *params, AVCodec *codec)
{
    int err = -1;

    self->codec = codec;
    /* TODO */
    self->SetParamsDefault(self);
    self->SetParamsUser(self, params);

    err = avcodec_open(self->ctx, self->codec);
    if (err < 0) {
        PyErr_Format(PyrExc_SetupError,
                     "Could not initialize the '%s' codec.",
                     self->codec->name);
    }
    return err;
}

int
PyrVCodec_AreValidParams(PyrCodecObject *self, PyObject *params)
{
    int valid = 1;
    if (params) {
        if (!PyMapping_Check(params)) {
            PyErr_Format(PyExc_TypeError,
                         "'params' argument has to be a mapping");
            valid = 0;
        }
    }
    return valid;
}


int
PyrVCodec_Init(PyrCodecObject *self, PyObject *args, PyObject *kwds)
{
    int err = -1;
    const char *name = NULL;
    PyObject *params = NULL;

    if (!PyArg_ParseTuple(args, "s|O:init", &name, &params)) { 
        PyErr_Format(PyrExc_SetupError, "Wrong arguments");
        return err; 
    }

    if (self->AreValidParams(self, params)) {
        AVCodec *codec = self->FindAVCodecByName(name);
        if (!codec) {
            PyErr_Format(PyrExc_SetupError,
                         "unkown %s `%s'", self->tag, name);
        }
        else {
            self->params = NULL;
            self->parent = NULL;
            self->ctx = avcodec_alloc_context();

            if (!self->ctx) {
                PyErr_Format(PyrExc_SetupError,
                            "unable to alloc the avcodec context");
            }
            else {
                err = PyrVCodec_Open(self, params, codec);
            }
        }
    }
    return err;
}

/*************************************************************************/

void
avpicture_softref(AVPicture *dst, AVPicture *src)
{
    dst->data[0] = src->data[0];
    dst->data[1] = src->data[1];
    dst->data[2] = src->data[2];
    dst->data[3] = src->data[3];

    dst->linesize[0] = src->linesize[0];
    dst->linesize[1] = src->linesize[1];
    dst->linesize[2] = src->linesize[2];
    dst->linesize[3] = src->linesize[3];
}

/* vim: set ts=4 sw=4 et */

