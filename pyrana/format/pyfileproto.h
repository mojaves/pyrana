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

#ifndef PYRANA_FILE_PROTO_H
#define PYRANA_FILE_PROTO_H

#include "format.h"

#define Pyr_FILE_KEY_LEN	(64)

/* returns a NEW reference */
PyObject *PyrFileProto_GetMappedFile(const char *filename);
/* returns a NEW reference */
PyObject *PyrFileProto_GetFileKey(void);

int PyrFileProto_AddMappedFile(PyObject *key, PyObject *obj);
int PyrFileProto_DelMappedFile(PyObject *key);

int PyrFileProto_Setup(void);

#endif /* PYRANA_FILE_PROTO_H */

