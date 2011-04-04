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


#include "pyrana/video/encoder.h"
#include "pyrana/video/picture.h"
#include "pyrana/format/packet.h"

typedef struct pyrencoderobject_ PyrEncoderObject;
struct pyrencoderobject_ {
    PyrCodecObject C;
    /* TODO */
    AVPacket *pkt; /* for the output buffer */
};



#define VENCODER_PARAMS "params"
PyDoc_STRVAR(VEncoder_Params__doc__,
VENCODER_PARAMS" -> params\n"
"Returns dictionary containing the encoder configuration parameters.\n"
"The content depends by the format being encoded.\n"
);
static PyObject *
VEncoder_GetParams(PyrCodecObject *self, void *closure)
{
    /* TODO */
    return NULL;
}

#define VENCODER_EXTRADATA "extra_data"
PyDoc_STRVAR(VEncoder_ExtraData__doc__,
"TODO"
);
static PyObject *
VEncoder_GetExtraData(PyrCodecObject *self, void *closure)
{
    /* TODO */
    return NULL;
}


static void
VEncoder_SetupFrame(PyrEncoderObject *self, AVFrame *frame)
{
    if (!self || !frame) {
        return;
    }
    /* TODO */
    return;
}

static void
VEncoder_SetupPacket(PyrEncoderObject *self, PyrPacketObject *pkt)
{
    if (!self || !pkt) {
        return;
    }
    /* TODO */
    return;
}

static PyObject *
VEncoder_EncodePacket(PyrEncoderObject *self, PyrVFrameObject *vframe)
{
    PyrPacketObject *pkt = NULL;
    PyrImage *img = &vframe->image->image;
    int size = avpicture_get_size(img->pix_fmt, img->width, img->height);
    int len = 0;
    AVFrame frame;

    avcodec_get_frame_defaults(&frame);

    if (!self->pkt) {
        av_new_packet(self->pkt, size);
    } else if (self->pkt->size < size) {
        av_grow_packet(self->pkt, size - self->pkt->size);
    }

    avpicture_softref((AVPicture *)&frame, &img->picture);
    VEncoder_SetupFrame(self, &frame);

    len = avcodec_encode_video(self->C.ctx,
                               self->pkt->data, self->pkt->size,
                               &frame);
    if (len > 0) {
        pkt = PyrPacket_NewFromData(self->pkt->data, len);
        VEncoder_SetupPacket(self, pkt);
    }
    return (PyObject *)pkt;
}


#define VENCODER_ENCODE "encode"
PyDoc_STRVAR(VEncoder_Encode__doc__,
VENCODER_ENCODE"(Frame) -> Packet Object\n"
"encode a Frame into a single Packet.\n"
);
static PyObject *
VEncoder_Encode(PyrEncoderObject *self, PyObject *args)
{
    PyrVFrameObject *vframe = NULL;

    if (!PyArg_ParseTuple(args, "O:"VENCODER_ENCODE, &vframe)) {
        return NULL;
    }

    if (!PyrVFrame_Check((PyObject *)vframe)) {
        PyErr_Format(PyrExc_ProcessingError, "Invalid video frame");
        return NULL;
    }
    return VEncoder_EncodePacket(self, vframe);
}

#define VENCODER_FLUSH "flush"
PyDoc_STRVAR(VEncoder_Flush__doc__,
VENCODER_FLUSH"() -> Packet Object\n"
"flushes any internal buffered packets (see encode() doc) and returns\n"
"the corresponding Packets, one per call.\n"
"\n"
"Raises ProcessingError when all buffers have been flushed."
);
static PyObject *
VEncoder_Flush(PyrEncoderObject *self, PyObject *args)
{
    /* always */
    PyErr_Format(PyrExc_ProcessingError, "All buffers flushed");
    return NULL;
}

static int
VEncoder_SetParamsDefault(PyrCodecObject *self)
{
    avcodec_get_context_defaults(self->ctx);

    self->ctx->mb_qmin                 = 2;
    self->ctx->mb_qmax                 = 31;
    self->ctx->max_qdiff               = 3;
    self->ctx->max_b_frames            = 0;
    self->ctx->me_range                = 0;
    self->ctx->mb_decision             = 0;
    self->ctx->scenechange_threshold   = 0;
    self->ctx->scenechange_factor      = 1;
    self->ctx->b_frame_strategy        = 0;
    self->ctx->b_sensitivity           = 40;
    self->ctx->brd_scale               = 0;
    self->ctx->bidir_refine            = 0;
    self->ctx->rc_strategy             = 2;
    self->ctx->b_quant_factor          = 1.25;
    self->ctx->i_quant_factor          = 0.8;
    self->ctx->b_quant_offset          = 1.25;
    self->ctx->i_quant_offset          = 0.0;
    self->ctx->qblur                   = 0.5;
    self->ctx->qcompress               = 0.5;
    self->ctx->mpeg_quant              = 0;
    self->ctx->rc_initial_cplx         = 0.0;
    self->ctx->rc_qsquish              = 1.0;
    self->ctx->luma_elim_threshold     = 0;
    self->ctx->chroma_elim_threshold   = 0;
    self->ctx->strict_std_compliance   = 0;
    self->ctx->dct_algo                = FF_DCT_AUTO;
    self->ctx->idct_algo               = FF_IDCT_AUTO;
    self->ctx->lumi_masking            = 0.0;
    self->ctx->dark_masking            = 0.0;
    self->ctx->temporal_cplx_masking   = 0.0;
    self->ctx->spatial_cplx_masking    = 0.0;
    self->ctx->p_masking               = 0.0;
    self->ctx->border_masking          = 0.0;
    self->ctx->me_pre_cmp              = 0;
    self->ctx->me_cmp                  = 0;
    self->ctx->me_sub_cmp              = 0;
    self->ctx->ildct_cmp               = FF_CMP_SAD;
    self->ctx->pre_dia_size            = 0;
    self->ctx->dia_size                = 0;
    self->ctx->mv0_threshold           = 256;
    self->ctx->last_predictor_count    = 0;
    self->ctx->pre_me                  = 1;
    self->ctx->me_subpel_quality       = 8;
    self->ctx->refs                    = 1;
    self->ctx->intra_quant_bias        = FF_DEFAULT_QUANT_BIAS;
    self->ctx->inter_quant_bias        = FF_DEFAULT_QUANT_BIAS;
    self->ctx->noise_reduction         = 0;
    self->ctx->quantizer_noise_shaping = 0;
    self->ctx->flags                   = 0;

    return 0;
}

static int
VEncoder_SetParamsUser(PyrCodecObject *self, PyObject *params)
{
    /* TODO */
    return 0;
}

static int
VEncoder_AreValidParams(PyrCodecObject *self, PyObject *params)
{
    /* TODO */
    return 1;
}

#define VENCODER_NAME "Decoder"
PyDoc_STRVAR(VEncoder__doc__,
VENCODER_NAME"(format_name [, params]) -> encoder\n"
"Returns encoder object."
);
static int
VEncoder_Init(PyrCodecObject *self, PyObject *args, PyObject *kwds)
{
    self->SetParamsDefault = VEncoder_SetParamsDefault;
    self->SetParamsUser = VEncoder_SetParamsUser;
    self->AreValidParams = VEncoder_AreValidParams;

    self->FindAVCodecByName = avcodec_find_encoder_by_name;

    self->tag = "encoder";

    return PyrVCodec_Init(self, args, kwds);
}

void
VEncoder_Dealloc(PyrEncoderObject *self)
{
    if (self->pkt) {
        av_free_packet(self->pkt);
    }
    PyrVCodec_Dealloc((PyrCodecObject *)self);
}

static PyMethodDef VEncoder_Methods[] =
{
    {
        VENCODER_ENCODE,
        (PyCFunction)VEncoder_Encode,
        METH_VARARGS,
        VEncoder_Encode__doc__
    },
    {
        VENCODER_FLUSH,
        (PyCFunction)VEncoder_Flush,
        METH_VARARGS,
        VEncoder_Flush__doc__
    },
    { NULL, NULL }, /* Sentinel */
};


static PyGetSetDef VEncoder_GetSet[] =
{
    {
        VENCODER_PARAMS,
        (getter)VEncoder_GetParams,
        NULL,
        VEncoder_Params__doc__
    },
    {
        VENCODER_EXTRADATA,
        (getter)VEncoder_GetExtraData,
        NULL,
        VEncoder_ExtraData__doc__
    },
    { NULL }, /* Sentinel */
};

static PyType_Slot VEncoder_Slots[] =
{
    { Py_tp_dealloc,    VEncoder_Dealloc     },
    { Py_tp_init,       VEncoder_Init        },
    { Py_tp_methods,    VEncoder_Methods     },
    { Py_tp_getset,     VEncoder_GetSet      },
    { Py_tp_doc,        VEncoder__doc__      },
    { Py_tp_alloc,      PyType_GenericAlloc, },
    { Py_tp_new,        PyType_GenericNew    },
    { 0,                NULL                 }
};

static PyType_Spec VEncoder_Spec =
{
    VENCODER_NAME,
    sizeof(PyrEncoderObject),
    0,
    Py_TPFLAGS_DEFAULT|Py_TPFLAGS_BASETYPE,
    VEncoder_Slots
};

/*************************************************************************/

static PyObject *VEncoder_Type = NULL;

int
PyrVEncoder_Check(PyObject *o)
{
    return (((void *)Py_TYPE(o)) == (void *)VEncoder_Type);
}

int
PyrVEncoder_Setup(PyObject *m)
{
    VEncoder_Type = PyType_FromSpec(&VEncoder_Spec);
    PyType_Ready((PyTypeObject *)VEncoder_Type);
    PyModule_AddObject(m, VENCODER_NAME, VEncoder_Type);
    return 0;
}

/* vim: set ts=4 sw=4 et */

