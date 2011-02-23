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

#include "pyrana/pyrana.h"

#include "pyrana/errors.h"

#include "pyrana/format/format.h"
#include "pyrana/video/video.h"
#include "pyrana/audio/audio.h"


PyDoc_STRVAR(Pyrana_doc,
"Pyrana is a python package designed to provides simple access to multimedia "
"files. Pyrana is based on the FFmpeg libraries, but "
"provides an independent API. Wherever practical, Pyrana aims to "
"be as much backward compatible as is possible to the Pyredia package.");



static void Logger(void* ctx, int level, const char *fmt, va_list ap)
{
    /* discard everything */
    ;
}

static struct PyModuleDef pyranamodule = {
    PyModuleDef_HEAD_INIT,
    "pyrana",
    Pyrana_doc,
    -1,
    NULL,
    NULL,
    NULL,
    NULL,
    NULL
};


PyMODINIT_FUNC
initpyrana(void)
{
    PyObject *m = PyModule_Create(&pyranamodule);
    if (m) {
        avcodec_init();
        avcodec_register_all();
        av_register_all();

        av_log_set_callback(Logger);

        PyModule_AddStringConstant(m, "VERSION", PYRANA_VERSION_STRING);
        PyModule_AddIntConstant(m, "TS_NULL", AV_NOPTS_VALUE);
        PyModule_AddIntConstant(m, "FRAMENUM_NULL", Pyr_FRAMENUM_NULL);

        PyModule_AddIntConstant(m, "MEDIA_ANY", AVMEDIA_TYPE_UNKNOWN);
        PyModule_AddIntConstant(m, "MEDIA_VIDEO", AVMEDIA_TYPE_VIDEO);
        PyModule_AddIntConstant(m, "MEDIA_AUDIO", AVMEDIA_TYPE_AUDIO);

        PyrErrors_Setup(m);
        PyrFormat_Setup(m);
        PyrVideo_Setup(m);
        PyrAudio_Setup(m);
    }
    return m;
}


/* vim: set ts=4 sw=4 et */

