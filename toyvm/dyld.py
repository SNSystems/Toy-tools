#!/usr/bin/env python3
# -*- coding: utf-8 -*-
## Copyright (c) 2016 by SN Systems Ltd., Sony Interactive Entertainment Inc.
## 
## Permission is hereby granted, free of charge, to any person obtaining a copy
## of this software and associated documentation files (the "Software"), to deal
## in the Software without restriction, including without limitation the rights
## to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
## copies of the Software, and to permit persons to whom the Software is
## furnished to do so, subject to the following conditions:
## 
## The above copyright notice and this permission notice shall be included in
## all copies or substantial portions of the Software.
## 
## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
## IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
## FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
## AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
## LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
## OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
## THE SOFTWARE.

"""
A dynamic loading which reads a program from an executable image and returns it for running on
the virtual machine.
"""

import io
import logging
from typing import Mapping

from store.exetypes import Executable
from store.types import SectionType
from toyvm.instruction import Instruction

_logger = logging.getLogger (__name__)


def load (content: Executable) -> Mapping [str, Instruction]:
    program = dict ()
    for symbol in content.symbols:
        name = symbol.name
        _logger.debug ('Loading %s', name)
        start = symbol.address
        end = start + symbol.size
        sections = {
            SectionType.text: io.BytesIO (content.data [SectionType.text] [start:end])
        }

        # TODO: change the read() method so that it will only ever load the target data. The debug loading code
        # should be in the debugger.
        program [name] = Instruction.read (sections)

    # FIXME: Now the second pass: check that all of the fixups are resolved.
    # for name, fixups in content.items ():
    #    if name [0] == '_':
    #        name = name [1:]
    #        for reference in fixups:
    #            if reference not in program:
    #                _logger.warn ("Name '{ndef}' not defined by '{by}'".format (ndef=reference, by=name))
    return program

# eof toyvm.dyld
