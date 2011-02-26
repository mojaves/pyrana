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


#ifndef PYRANA_SAMPLES_H
#define PYRANA_SAMPLES_H

#include "pyrana/pyrana_internal.h"
#include "pyrana/audio/audio.h"

#include <libavcodec/avcodec.h>



PyObject *PyrAudio_NewSampleFormats(void);
PyObject *PyrAudio_NewUserSampleFormats(void);


typedef struct {
    int16_t *data;
    int size_bytes;
    enum SampleFormat sample_fmt;
    int sample_rate;
    int channels;
} PyrSamples;


int PyrSamples_FrameSize(enum SampleFormat sample_fmt,
                         int sample_rate, int channels);
int PyrSamples_Init(PyrSamples *S, 
                    enum SampleFormat sample_fmt,
                    int sample_rate, int channels);
int PyrSamples_Fini(PyrSamples *S);
int PyrSamples_Len(PyrSamples *S);


typedef struct pyraframeobject_ PyrAFrameObject;
struct pyraframeobject_ {
    PyObject_HEAD
    PyrSamples samples;
    PyrFrameOrigin origin;
    int64_t pts;
};


PyrAFrameObject *PyrAFrame_NewEmpty(enum SampleFormat sample_fmt,
			            int sample_rate, int channels);
PyrAFrameObject *PyrAFrame_NewFromSamples(const PyrSamples *S);

int PyrAFrame_Check(PyObject *o);

int PyrAFrame_Setup(PyObject *m);


#endif /* PYRANA_SAMPLES_H */

/* vim: set ts=4 sw=4 et */

