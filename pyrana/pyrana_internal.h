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


#ifndef PYRANA_INTERNAL_H
#define PYRANA_INTERNAL_H

#include "pyrana/pyrana.h"
#include "pyrana/errors.h"


enum {
    Pyr_BUF_SIZE = 128
};

typedef enum {
    Pyr_FRAME_ORIGIN_UNKNOWN = 0,
    Pyr_FRAME_ORIGIN_USER,
    Pyr_FRAME_ORIGIN_LIBAV
} PyrFrameOrigin;


typedef struct pyrcodecobject_ PyrCodecObject;
struct pyrcodecobject_ {
    PyObject_HEAD
    PyObject *parent; /* for decoders spawned from demuxers */
    AVCodecContext *ctx;
    AVCodec *codec;
    PyObject *params;

    int thread_count;

    /* FIXME: case */
    int (*SetParamsDefault)(PyrCodecObject *self);
    int (*SetParamsUser)(PyrCodecObject *self, PyObject *params);
    int (*AreValidParams)(PyrCodecObject *self, PyObject *params);
    
    AVCodec *(*FindAVCodecByName)(const char *name);

    const char *tag;
};


void PyrInjectBufferProcs(PyObject *obj, PyBufferProcs *procs);


void PyrVCodec_Dealloc(PyrCodecObject *self);
int PyrVCodec_Open(PyrCodecObject *self, PyObject *params, AVCodec *codec);
int PyrVCodec_Init(PyrCodecObject *self, PyObject *args, PyObject *kwds);
int PyrVCodec_AreValidParams(PyrCodecObject *self, PyObject *params);

/*************************************************************************/

void avpicture_softref(AVPicture *dst, AVPicture *src);

/*************************************************************************/

#endif /* PYRANA_INTERNAL_H */

/* vim: set ts=4 sw=4 et */

