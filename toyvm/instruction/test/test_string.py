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

import hashlib
import unittest
from unittest.mock import Mock

from toyvm.instruction import String, SourceLocation
from toyvm.machine import Machine

class TestString (unittest.TestCase):

    # TODO: test the read and write methods

    def test_name (self):
        self.assertEqual (String ('add').name (), None)

    def test_instructions (self):
        self.assertSequenceEqual (String ('add').instructions (), [])

    def test_default_location (self):
        self.assertEqual (String ('str').locn (), None)

    def test_equal (self):
        self.assertEqual (String ('string'), String ('string'))
        self.assertEqual (String ('string', locn=SourceLocation ('path', line=2, column=3)),
                          String ('string', locn=SourceLocation ('path', line=2, column=3)))
        # Differ by value
        self.assertNotEqual (String ('op1'), String ('op2'))
        self.assertNotEqual (String ('string'), String ('String'))

        # Differ only by source location
        self.assertNotEqual (String ('op', locn=SourceLocation ('path', line=2, column=3)),
                             String ('op', locn=SourceLocation ('path', line=2, column=432)))

    def test_execute (self):
        m = Mock (spec=Machine, autospec=True)
        String ('foo').execute (m)
        m.operand_push.assert_called_once_with ('foo')

    def _get_digest (self, *args, **kwargs):
         h = hashlib.new ('md5')
         String (*args, **kwargs).digest (h)
         return h.digest ()

    def test_digest (self):
         self.assertEqual (self._get_digest ('a'), self._get_digest ('a'))
         self.assertEqual (self._get_digest ('a', locn=SourceLocation ('path', line=2, column=3)),
                           self._get_digest ('a', locn=SourceLocation ('path', line=2, column=3)))

        # Differ by value
         self.assertNotEqual (self._get_digest ('a'), self._get_digest ('b'))

         # Differs only by source location
         self.assertNotEqual (self._get_digest ('a', locn=SourceLocation ('path', line=2, column=3)),
                              self._get_digest ('a', locn=SourceLocation ('path', line=200, column=3)))

#eof toyvm/instruction/test/test_string.py
