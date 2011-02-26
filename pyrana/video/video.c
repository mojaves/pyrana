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

#include "pyrana/video/video.h"
#include "pyrana/video/picture.h"
#include "pyrana/video/decoder.h"


#define VIDEO_SUBMODULE_PYDOC "Not yet"

#define VIDEO_SUBMODULE_NAME MODULE_NAME".video"



static PyObject *
BuildCodecNamesInput(void)
{
    PyObject *ret = NULL;
    PyObject *names = PySet_New(NULL);
    AVCodec *codec = av_codec_next(NULL);

    for (; codec != NULL; codec = av_codec_next(codec)) {
        if (codec->type == CODEC_TYPE_VIDEO && codec->decode != NULL) {
            PyObject *name = PyUnicode_FromString(codec->name);
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
        if (codec->type == CODEC_TYPE_VIDEO && codec->encode != NULL) {
            PyObject *name = PyUnicode_FromString(codec->name);
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


static void
VideoConstants_Setup(PyObject *sm)
{
    /* FIXME:
     * smells wrong, need to figure something better (more coherent?)
     */
    PyModule_AddIntConstant(sm, "PICT_NO_TYPE", Pyr_PICT_NO_TYPE);
    PyModule_AddIntConstant(sm, "PICT_I_TYPE", FF_I_TYPE);
    PyModule_AddIntConstant(sm, "PICT_P_TYPE", FF_P_TYPE);
    PyModule_AddIntConstant(sm, "PICT_B_TYPE", FF_B_TYPE);
    PyModule_AddIntConstant(sm, "PICT_S_TYPE", FF_S_TYPE);
    PyModule_AddIntConstant(sm, "PICT_SI_TYPE", FF_SI_TYPE);
    PyModule_AddIntConstant(sm, "PICT_SP_TYPE", FF_SP_TYPE);
    PyModule_AddIntConstant(sm, "PICT_BI_TYPE", FF_BI_TYPE);
}


static struct PyModuleDef pyranavideomodule = {
    PyModuleDef_HEAD_INIT,
    VIDEO_SUBMODULE_NAME,
    VIDEO_SUBMODULE_PYDOC,
    -1,
    NULL,
    NULL,
    NULL,
    NULL,
    NULL
};


int
PyrVideo_Setup(PyObject *m)
{
    int ret = -1;
    PyObject *sm = PyModule_Create(&pyranavideomodule);
    if (sm) {
        PyModule_AddObject(sm, "input_codecs", BuildCodecNamesInput());
        PyModule_AddObject(sm, "output_codecs", BuildCodecNamesOutput());
        PyModule_AddObject(sm, "pixel_formats", PyrVideo_NewPixelFormats());
        PyModule_AddObject(sm, "user_pixel_formats",
                           PyrVideo_NewUserPixelFormats());

        VideoConstants_Setup(sm);

        PyrImage_Setup(sm);
        PyrVFrame_Setup(sm);
        PyrVDecoder_Setup(sm);

        PyModule_AddObject(m, "video", sm);
        ret = 0;
    }
    return ret;
}

/* vim: set ts=4 sw=4 et */

