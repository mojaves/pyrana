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


static const enum PixelFormat g_pix_fmts[] = {
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

static const enum PixelFormat g_user_pix_fmts[] = {
    PIX_FMT_NONE,
    PIX_FMT_YUV420P,
    PIX_FMT_RGB24,
    PIX_FMT_BGR24,
    PIX_FMT_YUV422P,
    PIX_FMT_YUV444P,
    PIX_FMT_ARGB,
    PIX_FMT_RGBA,
    PIX_FMT_ABGR,
    PIX_FMT_BGRA,
    PIX_FMT_NB,
};

#define FILL_INFO(INF, W, H, BPP) do { \
    (INF)->width = (W); \
    (INF)->height = (H); \
    (INF)->size = (W) * (H) * (BPP); \
} while (0)


static int
GetPlanesInfo(enum PixelFormat pix_fmt, int width, int height,
              PyrPlaneInfo *info)
{
    int err = 0;
    if (!info || width <= 0 || height <= 0) {
        err = -1;
    }
    else {
        switch (pix_fmt) {
          case PIX_FMT_YUV420P:
            info->plane_num = 3;
            FILL_INFO(&(info->infos[0]), width, height, 1);
            FILL_INFO(&(info->infos[1]), width/2, height/2, 1);
            FILL_INFO(&(info->infos[2]), width/2, height/2, 1);
            break;
/*          case PIX_FMT_YUV422P:
            break;
          case PIX_FMT_YUV444P:
            break;
*/
          case PIX_FMT_RGB24: /* fallback */
          case PIX_FMT_BGR24:
            info->plane_num = 1;
            FILL_INFO(&(info->infos[0]), width, height, 3);
            break;
          case PIX_FMT_ARGB: /* fallback */
          case PIX_FMT_RGBA: /* fallback */
          case PIX_FMT_ABGR: /* fallback */
          case PIX_FMT_BGRA:
            info->plane_num = 1;
            FILL_INFO(&(info->infos[0]), width, height, 4);
            break;
          case PIX_FMT_NB: /* fallback */
          case PIX_FMT_NONE: /* fallback */
          default:
            err = -1;
            break;
        }
    }
    return err;
}

const char *
GetPixFmtName(enum PixelFormat fmt)
{
    const char *name = NULL;
    int i = 0;

    for (i = 0; !name && g_pix_fmts[i] != PIX_FMT_NB; i++) {
        if (fmt == g_pix_fmts[i]) {
            name = avcodec_get_pix_fmt_name(g_pix_fmts[i]);
        }
    }

    return name;
}

static PyObject *
BuildPixelFormatSet(const enum PixelFormat g_pix_fmts[])
{
    PyObject *ret = NULL;
    PyObject *names = PySet_New(NULL);
    int i = 0;
    /* PIX_FMT_NONE deserves a special treatment */
    PyObject *fmt_none = PyString_FromString("none");
    int err = PySet_Add(names, fmt_none);
    if (err) {
        Py_DECREF(names);
        return NULL;
    }

    for (i = 1; !err && g_pix_fmts[i] != PIX_FMT_NB; i++) { /* FIXME */
        const char *fmt_name = avcodec_get_pix_fmt_name(g_pix_fmts[i]);
        PyObject *name = PyString_FromString(fmt_name);
        err = PySet_Add(names, name);
        if (err) {
            Py_DECREF(names);
            return NULL;
        }
    }
 
    ret = PyFrozenSet_New(names);
    Py_DECREF(names);
    return ret;
}


PyObject *
PyrVideo_NewPixelFormats(void)
{
    return BuildPixelFormatSet(g_pix_fmts);
}

PyObject *
PyrVideo_NewUserPixelFormats(void)
{
    return BuildPixelFormatSet(g_user_pix_fmts);
}



static enum PixelFormat
FindPixFmtByName(const char *name)
{
    enum PixelFormat fmt = PIX_FMT_NB;
    if (name) {
        int i;
        /* FIXME */
        for (i = 1; fmt == PIX_FMT_NB && g_pix_fmts[i] != PIX_FMT_NB; i++) {
            const char *fmt_name = avcodec_get_pix_fmt_name(g_pix_fmts[i]);
            if (!strcmp(fmt_name, name)) {
                fmt = g_pix_fmts[i];
            }
        }
    }
    return fmt;
}


/*************************************************************************/


static PyTypeObject Image_Type;



int
PyrImage_Check(PyObject *o)
{
    return PyObject_TypeCheck(o, &Image_Type);
}


static void
Image_Dealloc(PyrImageObject *self)
{
    if (self->parent) {
        Py_XDECREF(self->parent);
    }
    PyObject_Del((PyObject *)self);
}

typedef int (*PlaneWorker)(PyrImageObject *self,
                           int plane_idx,
                           const PyrPlaneInfo *plane_info,
                           Py_buffer *plane_view,
                           void *user_data);


static int
Image_FillPlane(PyrImageObject *self,
                int plane_idx,
                const PyrPlaneInfo *plane_info,
                Py_buffer *plane_view,
                void *user_data)
{
    int err = 0;
    if (plane_view->len != plane_info->infos[plane_idx].size) {
        PyErr_Format(PyrExc_SetupError,
                    "data size mismatch on plane #%i (found=%i expected=%ld)",
                    plane_idx, plane_info->infos[plane_idx].size, plane_view->len);
        err = -1;
    }
    else {
        PyErr_Format(PyExc_NotImplementedError, "Not yet");
        err = -1;
    }
    return err;
}

static int
Image_DataForeachPlane(PyrImageObject *self,
                       const PyrPlaneInfo *plane_info,
                       PyObject *data_obj,
                       PlaneWorker plane_worker,
                       void *user_data)
{
    int i, err = 0;

    for (i = 0; !err && i < plane_info->plane_num; i++) {
        PyObject *plane = PySequence_GetItem(data_obj, i);
        if (!plane || !PyObject_CheckBuffer(plane)) {
            PyErr_Format(PyrExc_ProcessingError, "invalid data plane #%i", i);
            err = -1;
        }
        else {
            Py_buffer plane_view;
            err = PyObject_GetBuffer(plane, &plane_view, PyBUF_SIMPLE);
            if (err) {
                PyErr_Format(PyrExc_ProcessingError, "can't access to data plane #%i", i);
            }
            else {
                err = plane_worker(self, i, plane_info, &plane_view, user_data);
                PyBuffer_Release(&plane_view);
            }
        }
    }
    return err;
}


static int
Image_AreParamsValid(PyrImageObject *self,
                     int width, int height, enum PixelFormat pix_fmt)
{
    int valid = 1;
    if (width <= 0) {
        PyErr_Format(PyrExc_SetupError, "invalid width");
        valid = 0;
    }
    else if (height <= 0) {
        PyErr_Format(PyrExc_SetupError, "invalid height");
        valid = 0;
    }
    else if (pix_fmt == PIX_FMT_NB || pix_fmt == PIX_FMT_NONE) {
        PyErr_Format(PyrExc_SetupError, "invalid pixel format");
        valid = 0;
    }
    return valid;
}


static int
Image_FillFromPlanes(PyrImageObject *self,
                     const PyrPlaneInfo *plane_info,
                     PyObject *data_obj)
{
    int err = avpicture_alloc(&(self->image.picture), self->image.pix_fmt,
                              self->image.width, self->image.height);
    if (!err) {
        err = Image_DataForeachPlane(self, plane_info, data_obj, Image_FillPlane, NULL);
        if (err) {
            avpicture_free(&(self->image.picture));
        }
    }
    return err;
}

static int
Image_FillFromData(PyrImageObject *self,
                   const PyrPlaneInfo *plane_info,
                   PyObject *data_obj)
{
    Py_buffer plane_view;
    int ret = 0;
    int size = avpicture_get_size(self->image.pix_fmt,
                                  self->image.width, self->image.height);
    int err = PyObject_GetBuffer(data_obj, &plane_view, PyBUF_SIMPLE);

    if (err) {
        PyErr_Format(PyrExc_SetupError, "cannot access data");
        ret = -1;
    }
    else if (plane_view.len != size) {
        PyErr_Format(PyrExc_SetupError,
                    "data size mismatch (found=%i expected=%ld)",
                    size, plane_view.len);
        ret = -1;
    }
    else {
        int s = avpicture_fill((AVPicture *)&(self->image), plane_view.buf,
                               self->image.pix_fmt,
                               self->image.width, self->image.height);
        if (s != size) { /* can't happen */
            PyErr_Format(PyrExc_SetupError,
                        "copy data size mismatch (found=%i expected=%i)",
                        s, size);
        }
    }
    PyBuffer_Release(&plane_view);
    return ret;
}

static int
Image_InitData(PyrImageObject *self, PyObject *data_obj)
{
    int ret = 0;
    PyrPlaneInfo plane_info;
    int err = GetPlanesInfo(self->image.pix_fmt,
                            self->image.width, self->image.height,
                            &plane_info);
 
    if (err) {
        PyErr_Format(PyrExc_UnsupportedError, "unknown Pixel Format");
    }
    
    if (PySequence_Check(data_obj)
     && PySequence_Size(data_obj) == plane_info.plane_num) {
        ret = Image_FillFromPlanes(self, &plane_info, data_obj);
    }
    else if (PyObject_CheckBuffer(data_obj)) {
        ret = Image_FillFromData(self, &plane_info, data_obj);
    }
    else {
        PyErr_Format(PyrExc_SetupError, "bad Image data");
        ret = -1;
    }

    return ret;
}

#define IMAGE_NAME "Image"
PyDoc_STRVAR(Image__doc__,
IMAGE_NAME" - N/A\n"
""
);
static int
Image_Init(PyrImageObject *self, PyObject *args, PyObject *kwds)
{
    int ret = 0, width = 0, height = 0;
    PyObject *pix_fmt_obj = NULL;
    PyObject *data_obj = NULL;

    self->parent = NULL;

    if (!PyArg_ParseTuple(args, "iiOO:init",
                          &width, &height, &pix_fmt_obj, &data_obj)) {
        ret = -1; 
    }
    else {
        const char *name = PyString_AsString(pix_fmt_obj);
        enum PixelFormat pix_fmt = FindPixFmtByName(name);
        if (!Image_AreParamsValid(self, width, height, pix_fmt)) {
            ret = -1;
        }
        else {
            self->image.width = width;
            self->image.height = height;
            self->image.pix_fmt = pix_fmt;

            ret = Image_InitData(self, data_obj);
        }
    }
    return ret;
}

/* This name mimics the libav* ones */
static void
avpicture_softref(AVPicture *pict, AVFrame *frame)
{
    pict->data[0] = frame->data[0];
    pict->data[1] = frame->data[1];
    pict->data[2] = frame->data[2];
    pict->data[3] = frame->data[3];

    pict->linesize[0] = frame->linesize[0];
    pict->linesize[1] = frame->linesize[1];
    pict->linesize[2] = frame->linesize[2];
    pict->linesize[3] = frame->linesize[3];
}

static void
Image_InitFromFrame(PyrImageObject *self, PyrVFrameObject *frame,
                    const PyrImage *img)
{
    avpicture_softref(&(self->image.picture), frame->frame);
    self->image.width = img->width;
    self->image.height = img->height;
    self->image.pix_fmt = img->pix_fmt;
}

PyrImageObject *PyrImage_NewFromImage(const PyrImage *image)
{
    /* TODO */
    return NULL;
}

PyrImageObject *PyrImage_NewFromFrame(PyrVFrameObject *frame,
                                      const PyrImage *img)
{
    PyrImageObject *self = PyObject_New(PyrImageObject, &Image_Type);
    if (self) {
        Py_INCREF((PyObject*)frame);
        self->parent = frame;

        Image_InitFromFrame(self, frame, img);
    }
    return self;
}

static PyObject *
Image_Repr(PyrImageObject *self)
{
    PyrPlaneInfo plane_info;
    int err = GetPlanesInfo(self->image.pix_fmt,
                            self->image.width, self->image.height,
                            &plane_info);
    return PyString_FromFormat("<Image size=%ix%i pix_fmt=%s hasPlanes=%s>",
                               self->image.width, self->image.height,
                               avcodec_get_pix_fmt_name(self->image.pix_fmt),
                               (!err && plane_info.plane_num > 1) ?"Y" :"N");
} 




static Py_ssize_t
Image_GetBuf(PyrImageObject *self, Py_ssize_t segment, void **ptrptr)
{
    /* TODO */
    Py_ssize_t ret = -1;
    return ret;
}


static Py_ssize_t
Image_GetSegCount(PyrImageObject *self, Py_ssize_t *lenp)
{
    /* TODO */
    return 0;
}


static PyBufferProcs Image_as_buffer = {
    (readbufferproc)Image_GetBuf,    /* bf_getreadbuffer  */
    0,                               /* bf_getwritebuffer */
    (segcountproc)Image_GetSegCount, /* bf_getsegcount    */
    (charbufferproc)Image_GetBuf,    /* bf_getcharbuffer  */
};



static PyObject *
PyrImage_GetWidth(PyrImageObject *self)
{
    return PyInt_FromLong(self->image.width);
}

static PyObject *
PyrImage_GetHeight(PyrImageObject *self)
{
    return PyInt_FromLong(self->image.height);
}

static PyObject *
PyrImage_GetPixFmt(PyrImageObject *self)
{
    const char *fmt_name = avcodec_get_pix_fmt_name(self->image.pix_fmt);
    return PyString_FromString(fmt_name);
}


static PyGetSetDef Image_get_set[] =
{
    { "width",        (getter)PyrImage_GetWidth,  NULL, "width."   },
    { "height",       (getter)PyrImage_GetHeight, NULL, "height."  },
    { "pixel_format", (getter)PyrImage_GetPixFmt, NULL, "pixel format as string." },
    { NULL }, /* Sentinel */
};


#define IMAGE_PLANE_NAME "plane"
PyDoc_STRVAR(Image_Plane__doc__,
IMAGE_PLANE_NAME" - N/A\n"
"");
static PyObject *
Image_Plane(PyrImageObject *self, PyObject *args)
{
    /* TODO */
    PyErr_Format(PyExc_NotImplementedError, "not yet");
    return NULL;
}

#define IMAGE_CONVERT_NAME "convert"
PyDoc_STRVAR(Image_Convert__doc__,
IMAGE_CONVERT_NAME" - N/A\n"
"");
static PyObject *
Image_Convert(PyrImageObject *self, PyObject *args)
{
    /* TODO */
    PyErr_Format(PyExc_NotImplementedError, "not yet");
    return NULL;
}


static PyMethodDef Image_Methods[] =
{
    {
        IMAGE_PLANE_NAME,
        (PyCFunction)Image_Plane,
        METH_VARARGS,
        Image_Plane__doc__
    },
    {
        IMAGE_CONVERT_NAME,
        (PyCFunction)Image_Convert,
        METH_VARARGS,
        Image_Convert__doc__
    },
    { NULL, NULL }, /* Sentinel */
};



static PyTypeObject Image_Type =
{
    PyObject_HEAD_INIT(NULL)
    0,
    IMAGE_NAME,
    sizeof(PyrImageObject),
    0,
    (destructor)Image_Dealloc,              /* tp_dealloc */
    0,                                      /* tp_print */
    0,                                      /* tp_getattr */
    0,                                      /* tp_setattr */
    0,                                      /* tp_compare */
    (reprfunc)Image_Repr,                   /* tp_repr */
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
    Image__doc__,                           /* tp_doc */
    0,                                      /* tp_traverse */
    0,                                      /* tp_clear */
    0,                                      /* tp_richcompare */
    0,                                      /* tp_weaklistoffset */
    0,                                      /* tp_iter */
    0,                                      /* tp_iternext */
    Image_Methods,                          /* tp_methods */
    0,                                      /* tp_members */
    Image_get_set,                          /* tp_getset */
    0,                                      /* tp_base */
    0,                                      /* tp_dict */
    0,                                      /* tp_descr_get */
    0,                                      /* tp_descr_set */
    0,                                      /* tp_dictoffset */
    (initproc)Image_Init,                   /* tp_init */
    PyType_GenericAlloc,                    /* tp_alloc */
    PyType_GenericNew,                      /* tp_new */
};


int
PyrImage_Setup(PyObject *m)
{
    if (PyType_Ready(&Image_Type) < 0)
        return -1;

    Image_Type.ob_type = &PyType_Type;
    Py_INCREF((PyObject *)&Image_Type);
    PyModule_AddObject(m, IMAGE_NAME, (PyObject *)&Image_Type);
    return 0;
}

/*************************************************************************/


static PyTypeObject VFrame_Type;



int
PyrVFrame_Check(PyObject *o)
{
    return PyObject_TypeCheck(o, &VFrame_Type);
}


static void
VFrame_Dealloc(PyrVFrameObject *self)
{
    if (self->frame) {
        av_free(self->frame);
    }
    Py_XDECREF((PyObject*)self->image);
    PyObject_Del((PyObject *)self);
}


#define VFRAME_NAME "Frame"
PyDoc_STRVAR(VFrame__doc__,
IMAGE_NAME" - N/A\n"
""
);
static int
VFrame_Init(PyrVFrameObject *self, PyObject *args, PyObject *kwds)
{
    int ret = 0, is_key = 0, isInterlaced = 0, topFieldFirst = 0;
    PY_LONG_LONG pts = 0;
    PyObject *image = NULL;

    if (!PyArg_ParseTuple(args, "OLiii:init",
                          &image, &pts, &is_key,
                          &isInterlaced, &topFieldFirst)) {
        ret = -1; 
    }
    else if (!PyrImage_Check(image)) {
        PyErr_Format(PyExc_ValueError, "<image> is not a pyrana.video.Image");
        ret = -1;
    }
    else {
        Py_INCREF(image);
        self->image = (PyrImageObject*)image;
       
        self->frame = avcodec_alloc_frame();
        self->frame->pts = pts;
        self->frame->interlaced_frame = isInterlaced;
        self->frame->top_field_first = topFieldFirst;

        /* beware of the following */
        self->frame->key_frame = is_key;
        self->frame->coded_picture_number = Pyr_FRAMENUM_NULL;
        self->frame->display_picture_number = Pyr_FRAMENUM_NULL;
        self->frame->pict_type = Pyr_PICT_NO_TYPE;
    }

    return ret;
}

static const char *
VFrame_GetPictDesc(PyrVFrameObject *self)
{
    const char *p = "N";
    switch (self->frame->pict_type) {
      case FF_I_TYPE:
        p = "I";
        break;
      case FF_P_TYPE:
        p = "P";
        break;
      case FF_B_TYPE:
        p = "B";
        break;
      case FF_S_TYPE:
        p = "S";
        break;
      case FF_SI_TYPE:
        p = "SI";
        break;
      case FF_SP_TYPE:
        p = "SP";
        break;
      case FF_BI_TYPE:
        p = "BI";
        break;
      case Pyr_PICT_NO_TYPE: /* fallthrough */
      default:
        p = "N";
        break;
    }
    return p;
}

static const char *
VFrame_GetILaceDesc(PyrVFrameObject *self)
{
     const char *s = "N";
     if (self->frame->interlaced_frame) {
        if (self->frame->top_field_first) {
            s = "T";
        }
        else {
            s = "B";
        }
     }
     return s;
}

static PyObject *
VFrame_Repr(PyrVFrameObject *self)
{
    return PyString_FromFormat("<Video Frame #%i/%i type=%s key=%s ilace=%s>",
                               self->frame->coded_picture_number,
                               self->frame->display_picture_number,
                               VFrame_GetPictDesc(self), 
                               (self->frame->key_frame) ?"Y" :"N",
                               VFrame_GetILaceDesc(self));
} 


PyrVFrameObject *
PyrVFrame_NewFromAVFrame(AVFrame *frame, const PyrImage *img)
{
    PyrVFrameObject *self = NULL;

    self = PyObject_New(PyrVFrameObject, &VFrame_Type);
    if (self) {
        self->origin = Pyr_FRAME_ORIGIN_LIBAV;
        self->frame = frame;
        self->is_key = frame->key_frame;
        self->image = PyrImage_NewFromFrame(self, img);
        /* TODO: NewFromFrame can fail */
    }
    return self;
}


static PyObject *
PyrVFrame_GetImage(PyrVFrameObject *self)
{
    PyrImageObject *image = self->image;
    if (self->origin == Pyr_FRAME_ORIGIN_LIBAV) {
        self->image->parent = self;
        Py_INCREF((PyObject*)self);
    }
    Py_INCREF((PyObject*)image);
    return (PyObject*)image;
}

static PyObject *
PyrVFrame_GetKey(PyrVFrameObject *self)
{
    return PyInt_FromLong(self->frame->key_frame);
}


static PyObject *
PyrVFrame_GetPts(PyrVFrameObject *self)
{
    return PyLong_FromLongLong(self->frame->pts);
}

static PyObject *
PyrVFrame_GetTopFieldFirst(PyrVFrameObject *self)
{
    return PyInt_FromLong(self->frame->top_field_first);
}

static PyObject *
PyrVFrame_GetIsInterlaced(PyrVFrameObject *self)
{
    return PyInt_FromLong(self->frame->interlaced_frame);
}

static PyObject *
PyrVFrame_GetPicType(PyrVFrameObject *self)
{
    return PyInt_FromLong(self->frame->pict_type);
}

static PyObject *
PyrVFrame_GetCodedNum(PyrVFrameObject *self)
{
    return PyInt_FromLong(self->frame->coded_picture_number);
}

static PyObject *
PyrVFrame_GetDisplayNum(PyrVFrameObject *self)
{
    return PyInt_FromLong(self->frame->display_picture_number);
}


static PyGetSetDef VFrame_get_set[] =
{
    { "image", (getter)PyrVFrame_GetImage, NULL, "frame image data" },
    { "is_key", (getter)PyrVFrame_GetKey, NULL, "reference frame flag" },
    { "pts", (getter)PyrVFrame_GetPts, NULL, "frame presentation timestamp." },
    { "top_field_first", (getter)PyrVFrame_GetTopFieldFirst, NULL, "interlaced field order." },
    { "is_interlaced", (getter)PyrVFrame_GetIsInterlaced, NULL, "interlace flag" },
    { "pic_type", (getter)PyrVFrame_GetPicType, NULL, "picture type" },
    { "coded_num", (getter)PyrVFrame_GetCodedNum, NULL, "encoded sequence number" },
    { "display_num", (getter)PyrVFrame_GetDisplayNum, NULL, "display sequence number" },
    { NULL }, /* Sentinel */
};


static PyTypeObject VFrame_Type =
{
    PyObject_HEAD_INIT(NULL)
    0,
    VFRAME_NAME,
    sizeof(PyrVFrameObject),
    0,
    (destructor)VFrame_Dealloc,             /* tp_dealloc */
    0,                                      /* tp_print */
    0,                                      /* tp_getattr */
    0,                                      /* tp_setattr */
    0,                                      /* tp_compare */
    (reprfunc)VFrame_Repr,                  /* tp_repr */
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
    VFrame__doc__,                          /* tp_doc */
    0,                                      /* tp_traverse */
    0,                                      /* tp_clear */
    0,                                      /* tp_richcompare */
    0,                                      /* tp_weaklistoffset */
    0,                                      /* tp_iter */
    0,                                      /* tp_iternext */
    0,                                      /* tp_methods */
    0,                                      /* tp_members */
    VFrame_get_set,                         /* tp_getset */
    0,                                      /* tp_base */
    0,                                      /* tp_dict */
    0,                                      /* tp_descr_get */
    0,                                      /* tp_descr_set */
    0,                                      /* tp_dictoffset */
    (initproc)VFrame_Init,                  /* tp_init */
    PyType_GenericAlloc,                    /* tp_alloc */
    PyType_GenericNew,                      /* tp_new */
};


int
PyrVFrame_Setup(PyObject *m)
{
    if (PyType_Ready(&VFrame_Type) < 0)
        return -1;

    VFrame_Type.ob_type = &PyType_Type;
    Py_INCREF((PyObject *)&VFrame_Type);
    PyModule_AddObject(m, VFRAME_NAME, (PyObject *)&VFrame_Type);
    return 0;
}



/* vim: set ts=4 sw=4 et */

