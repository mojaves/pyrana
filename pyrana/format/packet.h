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


#ifndef PYRANA_PACKET_H
#define PYRANA_PACKET_H

#define Pyr_PACKET_SIZE_MAX  (8*1024)

#include "pyrana/format/format.h"

#include <libavformat/avformat.h>


typedef struct {
    PyObject_HEAD
    AVPacket pkt;
    int len; /* real size of the data */
} PyrPacketObject;


PyrPacketObject *PyrPacket_NewFromAVPacket(AVPacket *pkt);
PyrPacketObject *PyrPacket_NewFromData(const uint8_t *data, int size);
PyrPacketObject *PyrPacket_NewEmpty(int size);
int PyrPacket_Check(PyObject *o);

int PyrPacket_Setup(PyObject *m);

#endif /* PYRANA_PACKET_H */

/* vim: set ts=4 sw=4 et */

