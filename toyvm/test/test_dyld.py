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

import unittest

from store.exetypes import Executable, Symbol
from store.types import SectionType
from toyvm.dyld import load
from toyvm.instruction import Boolean, Procedure


class TestDyld (unittest.TestCase):
    def test_empty_image (self):
        exe = Executable.new ()
        self.assertDictEqual (load (Executable.new ()), {})

    # TODO: I could have many more tests with variously malformed executables.

    def test_one_named_procedure (self):
        sections = {}
        # Create a procedure and write it to a new output stream.
        proc = Procedure ([Boolean (True)])
        proc.write (sections)

        # Build the executable image that we'll load.
        content = Executable.new ()
        b = sections [SectionType.text].getbuffer ()
        content.symbols.append (Symbol (name='n1', address=0, size=len (b)))
        content.data [SectionType.text] = b

        self.assertDictEqual (load (content), {'n1': proc})

# eof toyvm/test/test_dyld.py
