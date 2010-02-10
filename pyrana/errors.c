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

#include "pyrana/errors.h"
 
PyObject *PyrExc_PyranaError      = NULL;
PyObject *PyrExc_EOSError         = NULL;
PyObject *PyrExc_ProcessingError  = NULL;
PyObject *PyrExc_SetupError       = NULL;
PyObject *PyrExc_UnsupportedError = NULL;
 

/**************************************************************************/

int
PyrErrors_Setup(PyObject *m)
{
    PyrExc_PyranaError      = PyErr_NewException("pyrana.PyranaError",      NULL,               NULL);
    PyrExc_EOSError         = PyErr_NewException("pyrana.EOSError",         PyrExc_PyranaError, NULL);
    PyrExc_ProcessingError  = PyErr_NewException("pyrana.ProcessingError",  PyrExc_PyranaError, NULL);
    PyrExc_SetupError       = PyErr_NewException("pyrana.SetupError",       PyrExc_PyranaError, NULL);
    PyrExc_UnsupportedError = PyErr_NewException("pyrana.UnsupportedError", PyrExc_PyranaError, NULL);

    /* FIXME: Do we need to INCREFs here? */
    PyModule_AddObject(m, "PyranaError",      PyrExc_PyranaError);
    PyModule_AddObject(m, "EOSError",         PyrExc_EOSError);
    PyModule_AddObject(m, "ProcessingError",  PyrExc_ProcessingError);
    PyModule_AddObject(m, "SetupError",       PyrExc_SetupError);
    PyModule_AddObject(m, "UnsupportedError", PyrExc_UnsupportedError);

    return 0;
}

/* vim: set ts=4 sw=4 et */

