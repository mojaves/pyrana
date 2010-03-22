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


#ifndef PYRANA_PICTURE_H
#define PYRANA_PICTURE_H

#include "pyrana/video/video.h"

#include <libavcodec/avcodec.h>



enum {
    PYR_PLANES_NUM  = 4
};


const char *PyrVideo_GetPixFmtName(enum PixelFormat fmt);

PyObject *PyrVideo_NewPixelFormats(void);
PyObject *PyrVideo_NewUserPixelFormats(void);


typedef struct pyrimageobject_ PyrImageObject;
typedef struct pyrvframeobject_ PyrVFrameObject;

typedef struct {
    int planeNum;
    struct {
        int width;
        int height;
        int size;
    } infos[PYR_PLANES_NUM]; 
} PyrPlaneInfo;

typedef struct {
    AVPicture picture;
    int width;
    int height;
    enum PixelFormat pixFmt;
} PyrImage;

struct pyrimageobject_ {
    PyObject_HEAD
    PyrVFrameObject *parent; /* could be NULL */
    PyrImage image;
};



PyrImageObject *PyrImage_NewFromImage(const PyrImage *image);
PyrImageObject *PyrImage_NewFromFrame(PyrVFrameObject *frame);
int PyrImage_Check(PyObject *o);

int PyrImage_Setup(PyObject *m);

struct pyrvframeobject_ {
    PyObject_HEAD
    PyrImageObject *image;
    AVFrame frame;
    int ref_image; /* if != 0, image is a soft-ref to frame */
};


PyrVFrameObject *PyrVFrame_NewFromAVFrame(AVFrame *frame);
int PyrVFrame_Check(PyObject *o);

int PyrVFrame_Setup(PyObject *m);


#endif /* PYRANA_PICTURE_H */

