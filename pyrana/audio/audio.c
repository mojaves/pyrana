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

#include "pyrana/audio/audio.h"
#include "pyrana/audio/samples.h"


#define SUB_MODULE_PYDOC "Not yet"

#define SUB_MODULE_NAME MODULE_NAME".audio"


static PyObject *
BuildCodecNamesInput(void)
{
    PyObject *ret = NULL;
    PyObject *names = PySet_New(NULL);
    AVCodec *codec = av_codec_next(NULL);

    for (; codec != NULL; codec = av_codec_next(codec)) {
        if (codec->type == CODEC_TYPE_AUDIO && codec->decode != NULL) {
            PyObject *name = PyString_FromString(codec->name);
            int err = PySet_Add(names, name);
            if (err) {
                Py_DECREF(names);
                return NULL;
            }
        }
    }

    ret = PyFrozenSet_New(names);
    Py_DECREF(names);
    return ret;
}

static PyObject *
BuildCodecNamesOutput(void)
{
    PyObject *ret = NULL;
    PyObject *names = PySet_New(NULL);
    AVCodec *codec = av_codec_next(NULL);

    for (; codec != NULL; codec = av_codec_next(codec)) {
        if (codec->type == CODEC_TYPE_AUDIO && codec->encode != NULL) {
            PyObject *name = PyString_FromString(codec->name);
            int err = PySet_Add(names, name);
            if (err) {
                Py_DECREF(names);
                return NULL;
            }
        }
    }

    ret = PyFrozenSet_New(names);
    Py_DECREF(names);
    return ret;
}


int
PyrAudio_Setup(PyObject *m)
{
    int ret = -1;
    PyObject *sm = Py_InitModule3(SUB_MODULE_NAME,
                                  NULL,
                                  SUB_MODULE_PYDOC);
    if (sm) {
        PyModule_AddObject(sm, "input_codecs", BuildCodecNamesInput());
        PyModule_AddObject(sm, "output_codecs", BuildCodecNamesOutput());
        PyModule_AddObject(sm, "sample_formats", PyrAudio_NewSampleFormats());
        PyModule_AddObject(sm, "user_sample_formats",
                           PyrAudio_NewUserSampleFormats());

/*      not yet
        PyrAFrame_Setup(sm);
*/

        PyModule_AddObject(m, "audio", sm);
        ret = 0;
    }
    return ret;
}

/* vim: set ts=4 sw=4 et */

