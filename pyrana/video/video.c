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

#include "pyrana/video/video.h"


#define SUB_MODULE_PYDOC "Not yet"

#define SUB_MODULE_NAME MODULE_NAME".video"

#define PYR_BUF_SIZE (128)

/*************************************************************************/

static PyObject *
BuildCodecNamesInput(void)
{
    PyObject *names = PyList_New(0);
    AVCodec *codec = av_codec_next(NULL);

    for (; codec != NULL; codec = av_codec_next(codec)) {
        if (codec->type == CODEC_TYPE_VIDEO && codec->decode != NULL) {
            PyObject *name = PyString_FromString(codec->name);
            int err = PyList_Append(names, name);
            if (err) {
                Py_DECREF(names);
                return NULL;
            }
        }
    }

    return names;
}

static PyObject *
BuildCodecNamesOutput(void)
{
    PyObject *names = PyList_New(0);
    AVCodec *codec = av_codec_next(NULL);

    for (; codec != NULL; codec = av_codec_next(codec)) {
        if (codec->type == CODEC_TYPE_VIDEO && codec->encode != NULL) {
            PyObject *name = PyString_FromString(codec->name);
            int err = PyList_Append(names, name);
            if (err) {
                Py_DECREF(names);
                return NULL;
            }
        }
    }

    return names;
}

static const enum PixelFormat Pyr_PixFmts[] = {
    PIX_FMT_NONE,
    PIX_FMT_YUV420P,
    PIX_FMT_YUYV422,
    PIX_FMT_RGB24,
    PIX_FMT_BGR24,
    PIX_FMT_YUV422P,
    PIX_FMT_YUV444P,
    PIX_FMT_YUV410P,
    PIX_FMT_YUV411P,
    PIX_FMT_GRAY8,
    PIX_FMT_MONOWHITE,
    PIX_FMT_MONOBLACK,
    PIX_FMT_PAL8,
    PIX_FMT_YUVJ420P,
    PIX_FMT_YUVJ422P,
    PIX_FMT_YUVJ444P,
    PIX_FMT_XVMC_MPEG2_MC,
    PIX_FMT_XVMC_MPEG2_IDCT,
    PIX_FMT_UYVY422,
    PIX_FMT_UYYVYY411,
    PIX_FMT_BGR8,
    PIX_FMT_BGR4,
    PIX_FMT_BGR4_BYTE,
    PIX_FMT_RGB8,
    PIX_FMT_RGB4,
    PIX_FMT_RGB4_BYTE,
    PIX_FMT_NV12,
    PIX_FMT_NV21,
    PIX_FMT_ARGB,
    PIX_FMT_RGBA,
    PIX_FMT_ABGR,
    PIX_FMT_BGRA,
    PIX_FMT_GRAY16BE,
    PIX_FMT_GRAY16LE,
    PIX_FMT_YUV440P,
    PIX_FMT_YUVJ440P,
    PIX_FMT_YUVA420P,
    PIX_FMT_VDPAU_H264,
    PIX_FMT_VDPAU_MPEG1,
    PIX_FMT_VDPAU_MPEG2,
    PIX_FMT_VDPAU_WMV3,
    PIX_FMT_VDPAU_VC1,
    PIX_FMT_RGB48BE,
    PIX_FMT_RGB48LE,
    PIX_FMT_RGB565BE,
    PIX_FMT_RGB565LE,
    PIX_FMT_RGB555BE,
    PIX_FMT_RGB555LE,
    PIX_FMT_BGR565BE,
    PIX_FMT_BGR565LE,
    PIX_FMT_BGR555BE,
    PIX_FMT_BGR555LE,
    PIX_FMT_VAAPI_MOCO,
    PIX_FMT_VAAPI_IDCT,
    PIX_FMT_VAAPI_VLD,
    PIX_FMT_YUV420P16LE,
    PIX_FMT_YUV420P16BE,
    PIX_FMT_YUV422P16LE,
    PIX_FMT_YUV422P16BE,
    PIX_FMT_YUV444P16LE,
    PIX_FMT_YUV444P16BE,
    PIX_FMT_NB,
};



static PyObject *
BuildPixelFormatNames(void)
{
    PyObject *names = PyList_New(0);
    int i = 0;
    /* PIX_FMT_NONE deserves a special treatment */
    PyObject *fmt_none = PyString_FromString("none");
    int err = PyList_Append(names, fmt_none);
    if (err) {
        Py_DECREF(names);
        return NULL;
    }

    for (i = 1; !err && Pyr_PixFmts[i] != PIX_FMT_NB; i++) { /* FIXME */
        const char *fmt_name = avcodec_get_pix_fmt_name(Pyr_PixFmts[i]);
        PyObject *name = PyString_FromString(fmt_name);
        err = PyList_Append(names, name);
        if (err) {
            Py_DECREF(names);
            return NULL;
        }
    }
 
    return names;
}



int
PyrVideo_Setup(PyObject *m)
{
    int ret = -1;
    PyObject *sm = Py_InitModule3(SUB_MODULE_NAME,
                                  NULL,
                                  SUB_MODULE_PYDOC);
    if (sm) {
        PyModule_AddObject(sm, "input_codecs",  BuildCodecNamesInput());
	    PyModule_AddObject(sm, "output_codecs", BuildCodecNamesOutput());
	    PyModule_AddObject(sm, "pixel_formats", BuildPixelFormatNames());

        PyModule_AddObject(m, "video", sm);
        ret = 0;
    }
    return ret;
}

/* vim: set ts=4 sw=4 et */

