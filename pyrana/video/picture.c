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

#include "pyrana/video/picture.h"

/* TODO:
 * N/A
 */


/*
 * Overview: the relationship between Frame, Image and Plane(s).
 * -------------------------------------------------------------
 * 
 * Image is the central Object here. An Image objects represent the picture
 * which is ultimately seen, and it has methods for the supported
 * transformations.
 *
 * Every Frame has-an Image, and it enriches that with
 * the metadata needed to properly place it into the video stream (e.g.
 * timing informations et.al.). A Frame has-an Image, so a Frame is
 * meaningless without an Image; however, the opposite is NOT true.
 * It makes perfectly sense to construct, deal and manipulate Images
 * without frames, and maybe eventually construct a Frame around them
 * to feed an Encoder.
 *
 * Planes are different beasts. They represent view of the parent Image,
 * so they are tighly bound to it. Every Plane carries an internal reference
 * to the generating Image. The Lifecycle of an Image MUST BE
 * at least equal to any of its spawned Planes. So, an Image cannot be
 * garbage collected until all Planes originated from it are.
 */

/*************************************************************************/

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

const char *
PyrVideo_GetPixFmtName(enum PixelFormat fmt)
{
    const char *name = NULL;
    int i = 0;

    for (i = 0; !name && Pyr_PixFmts[i] != PIX_FMT_NB; i++) {
        if (fmt == Pyr_PixFmts[i]) {
            name = avcodec_get_pix_fmt_name(Pyr_PixFmts[i]);
        }
    }

    return name;
}


PyObject *
PyrVideo_NewPixelFormatList(void)
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


/*************************************************************************/

/*
static int
PyrImage_setup(PyrImage *img, AVFrame *frame)
{
    return 0;
}

static int
PyrImage_clean(PyrImage *img)
{
    return 0;
}
*/

/*************************************************************************/


#define IMAGE_NAME "Image"
PyDoc_STRVAR(Image_doc,
IMAGE_NAME" - N/A\n"
"");

#define PLANE "plane"
PyDoc_STRVAR(plane_doc,
PLANE" - N/A\n"
"");

#define CONVERT "convert"
PyDoc_STRVAR(convert_doc,
CONVERT" - N/A\n"
"");



static PyTypeObject ImageType;



int
PyrImage_Check(PyObject *o)
{
    return PyObject_TypeCheck(o, &ImageType);
}


static void
Image_dealloc(PyrImageObject *self)
{
    if (self->parent) {
        Py_DECREF(self->parent);
    }
    PyObject_Del((PyObject *)self);
}


static int
Image_init(PyrImageObject *self, PyObject *args, PyObject *kwds)
{
    int ret = 0, width = 0, height = 0;
    PyObject *pixFmt = NULL;
    PyObject *data = NULL;

    self->parent = NULL;

    if (!PyArg_ParseTuple(args, "iiOO:init",
                          &width, &height, &pixFmt, &data)) {
        ret = -1; 
    } else {
    }
    return ret;
}

PyrImageObject *PyrImage_NewFromImage(const PyrImage *image)
{
    return NULL;
}

PyrImageObject *PyrImage_NewFromFrame(PyrVFrameObject *frame)
{
    PyrImageObject *self = PyObject_New(PyrImageObject, &ImageType);
    if (self) {
        Py_INCREF((PyObject*)frame);
        self->parent = frame;
        /* init img */
    }
    return self;
}

static PyObject *
Image_repr(PyrImageObject *self)
{
    return PyString_FromFormat("<Image>");
} 




static Py_ssize_t
Image_getbuf(PyrImageObject *self, Py_ssize_t segment, void **ptrptr)
{
    Py_ssize_t ret = -1;
    return ret;
}


static Py_ssize_t
Image_getsegcount(PyrImageObject *self, Py_ssize_t *lenp)
{
    return 0;
}


static PyBufferProcs Image_as_buffer = {
    (readbufferproc)Image_getbuf,    /* bg_getreadbuffer  */
    0,                               /* bf_getwritebuffer */
    (segcountproc)Image_getsegcount, /* bf_getsegcount    */
    (charbufferproc)Image_getbuf,    /* bf_getcharbuffer  */
};



static PyObject *
PyrImage_getwidth(PyrImageObject *self)
{
    return PyInt_FromLong(self->img.width);
}

static PyObject *
PyrImage_getheight(PyrImageObject *self)
{
    return PyInt_FromLong(self->img.height);
}

static PyObject *
PyrImage_getpixfmt(PyrImageObject *self)
{
    const char *fmt_name = avcodec_get_pix_fmt_name(self->img.pixFmt);
    return PyString_FromString(fmt_name);
}


static PyGetSetDef Image_getsetlist[] =
{
    { "width",  (getter)PyrImage_getwidth,  NULL, "width."   },
    { "height", (getter)PyrImage_getheight, NULL, "height."  },
    { "pixFmt", (getter)PyrImage_getpixfmt, NULL, "pixel format as string." },
    { NULL }, /* Sentinel */
};


static PyObject *
Image_Plane(PyrImageObject *self, PyObject *args)
{
    PyErr_Format(PyExc_NotImplementedError, "not yet");
    return NULL;
}

static PyObject *
Image_Convert(PyrImageObject *self, PyObject *args)
{
    PyErr_Format(PyExc_NotImplementedError, "not yet");
    return NULL;
}


static PyMethodDef Image_methods[] =
{
    {
        PLANE,
        (PyCFunction)Image_Plane,
        METH_VARARGS,
        plane_doc
    },
    {
        CONVERT,
        (PyCFunction)Image_Convert,
        METH_VARARGS,
        convert_doc
    },
    { NULL, NULL }, /* Sentinel */
};



static PyTypeObject ImageType =
{
    PyObject_HEAD_INIT(NULL)
    0,
    IMAGE_NAME,
    sizeof(PyrImageObject),
    0,
    (destructor)Image_dealloc,              /* tp_dealloc */
    0,                                      /* tp_print */
    0,                                      /* tp_getattr */
    0,                                      /* tp_setattr */
    0,                                      /* tp_compare */
    (reprfunc)Image_repr,                   /* tp_repr */
    0,                                      /* tp_as_number */
    0,                                      /* tp_as_sequence */
    0,                                      /* tp_as_mapping */
    0,                                      /* tp_hash */
    0,                                      /* tp_call */
    0,                                      /* tp_str */
    0,                                      /* tp_getattro */
    0,                                      /* tp_setattro */
    &Image_as_buffer,                       /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT|Py_TPFLAGS_BASETYPE, /* tp_flags */
    Image_doc,                              /* tp_doc */
    0,                                      /* tp_traverse */
    0,                                      /* tp_clear */
    0,                                      /* tp_richcompare */
    0,                                      /* tp_weaklistoffset */
    0,                                      /* tp_iter */
    0,                                      /* tp_iternext */
    Image_methods,                          /* tp_methods */
    0,                                      /* tp_members */
    Image_getsetlist,                       /* tp_getset */
    0,                                      /* tp_base */
    0,                                      /* tp_dict */
    0,                                      /* tp_descr_get */
    0,                                      /* tp_descr_set */
    0,                                      /* tp_dictoffset */
    (initproc)Image_init,                   /* tp_init */
    PyType_GenericAlloc,                    /* tp_alloc */
    PyType_GenericNew,                      /* tp_new */
};


int
PyrImage_Setup(PyObject *m)
{
    if (PyType_Ready(&ImageType) < 0)
        return -1;

    ImageType.ob_type = &PyType_Type;
    Py_INCREF((PyObject *)&ImageType);
    PyModule_AddObject(m, IMAGE_NAME, (PyObject *)&ImageType);
    return 0;
}

/*************************************************************************/

#define VFRAME_NAME "Frame"
PyDoc_STRVAR(VFrame_doc,
IMAGE_NAME" - N/A\n"
"");


static PyTypeObject VFrameType;



int
PyrVFrame_Check(PyObject *o)
{
    return PyObject_TypeCheck(o, &VFrameType);
}


static void
VFrame_dealloc(PyrVFrameObject *self)
{
    PyObject_Del((PyObject *)self);
}


static int
VFrame_init(PyrVFrameObject *self, PyObject *args, PyObject *kwds)
{
    int ret = 0;
    return ret;
}

static PyObject *
VFrame_repr(PyrVFrameObject *self)
{
    return PyString_FromFormat("<Video Frame #%i/%i type=%s key=%s ilace=%s>",
                               self->frame.coded_picture_number,
                               self->frame.display_picture_number,
                               "", "", "");
} 


PyrVFrameObject *
PyrVFrame_NewFromAVFrame(AVFrame *frame)
{
    return NULL;
}


static PyObject *
PyrVFrame_getimage(PyrVFrameObject *self)
{
    PyrImageObject *img = NULL;
    if (self->ref_image) {
        img = PyrImage_NewFromFrame(self);
    } else {
        img = self->image;
    }
    /* here we want an independent reference */
    Py_INCREF((PyObject*)img);
    return (PyObject*)img;
}

static PyObject *
PyrVFrame_getkey(PyrVFrameObject *self)
{
    return PyInt_FromLong(self->frame.key_frame);
}


static PyObject *
PyrVFrame_getpts(PyrVFrameObject *self)
{
    return PyLong_FromLongLong(self->frame.pts);
}

static PyObject *
PyrVFrame_gettopfieldfirst(PyrVFrameObject *self)
{
    return PyInt_FromLong(self->frame.top_field_first);
}

static PyObject *
PyrVFrame_getisinterlaced(PyrVFrameObject *self)
{
    return PyInt_FromLong(self->frame.interlaced_frame);
}

static PyObject *
PyrVFrame_getpictype(PyrVFrameObject *self)
{
    return PyInt_FromLong(self->frame.pict_type);
}

static PyObject *
PyrVFrame_getcodednum(PyrVFrameObject *self)
{
    return PyInt_FromLong(self->frame.coded_picture_number);
}

static PyObject *
PyrVFrame_getdisplaynum(PyrVFrameObject *self)
{
    return PyInt_FromLong(self->frame.display_picture_number);
}


static PyGetSetDef VFrame_getsetlist[] =
{
    { "image",         (getter)PyrVFrame_getimage,         NULL, "frame image data"              },
    { "isKey",         (getter)PyrVFrame_getkey,           NULL, "is it a reference frame?"      },
    { "pts",           (getter)PyrVFrame_getpts,           NULL, "frame presentation timestamp." },
    { "topFieldFirst", (getter)PyrVFrame_gettopfieldfirst, NULL, "interlaced field order."       },
    { "isInterlaced",  (getter)PyrVFrame_getisinterlaced,  NULL, "is it interlaced?"             },
    { "picType",       (getter)PyrVFrame_getpictype,       NULL, "picture type"                  },
    { "codedNum",      (getter)PyrVFrame_getcodednum,      NULL, "encoded sequence number"       },
    { "displayNum",    (getter)PyrVFrame_getdisplaynum,    NULL, "display sequence number"       },
    { NULL }, /* Sentinel */
};


static PyTypeObject VFrameType =
{
    PyObject_HEAD_INIT(NULL)
    0,
    VFRAME_NAME,
    sizeof(PyrVFrameObject),
    0,
    (destructor)VFrame_dealloc,             /* tp_dealloc */
    0,                                      /* tp_print */
    0,                                      /* tp_getattr */
    0,                                      /* tp_setattr */
    0,                                      /* tp_compare */
    (reprfunc)VFrame_repr,                  /* tp_repr */
    0,                                      /* tp_as_number */
    0,                                      /* tp_as_sequence */
    0,                                      /* tp_as_mapping */
    0,                                      /* tp_hash */
    0,                                      /* tp_call */
    0,                                      /* tp_str */
    0,                                      /* tp_getattro */
    0,                                      /* tp_setattro */
    0,                                      /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT|Py_TPFLAGS_BASETYPE, /* tp_flags */
    VFrame_doc,                             /* tp_doc */
    0,                                      /* tp_traverse */
    0,                                      /* tp_clear */
    0,                                      /* tp_richcompare */
    0,                                      /* tp_weaklistoffset */
    0,                                      /* tp_iter */
    0,                                      /* tp_iternext */
    0,                                      /* tp_methods */
    0,                                      /* tp_members */
    VFrame_getsetlist,                      /* tp_getset */
    0,                                      /* tp_base */
    0,                                      /* tp_dict */
    0,                                      /* tp_descr_get */
    0,                                      /* tp_descr_set */
    0,                                      /* tp_dictoffset */
    (initproc)VFrame_init,                  /* tp_init */
    PyType_GenericAlloc,                    /* tp_alloc */
    PyType_GenericNew,                      /* tp_new */
};


int
PyrVFrame_Setup(PyObject *m)
{
    if (PyType_Ready(&VFrameType) < 0)
        return -1;

    VFrameType.ob_type = &PyType_Type;
    Py_INCREF((PyObject *)&VFrameType);
    PyModule_AddObject(m, VFRAME_NAME, (PyObject *)&VFrameType);
    return 0;
}



/* vim: set ts=4 sw=4 et */

