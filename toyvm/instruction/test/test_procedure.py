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
from unittest.mock import Mock, call

from toyvm.machine import Machine
from toyvm.instruction import Boolean, Procedure, SourceLocation


class TestProcedure (unittest.TestCase):

    # TODO: test the read and write methods

    def test_equal (self):
        self.assertEqual (Procedure ([]), Procedure ([]))
        self.assertEqual (Procedure ([ Boolean (True) ]), Procedure ([ Boolean (True) ]))
        self.assertNotEqual (Procedure ([ Boolean (True) ]), Procedure ([ Boolean (False) ]))
        self.assertNotEqual (Procedure ([ ]), Procedure ([ Boolean (False) ]))

        self.assertNotEqual (Procedure ([]),
                             Procedure ([], locn=SourceLocation ('path', line=1, column=1)))

    def test_instructions (self):
        self.assertSequenceEqual (Procedure ([ Boolean (True), Boolean (False) ]).instructions (),
                                  [ Boolean (True), Boolean (False) ])

    def test_execute (self):
        m = Mock (spec=Machine)
        Procedure ([ Boolean (True) ]).execute (m)
        m.operand_push.assert_called_once_with (Procedure ([ Boolean (True) ]))

    def test_name (self):
        self.assertEqual (Procedure ([]).name (), None)

    def _get_digest (self, *args, **kwargs):
        h = hashlib.new ('md5')
        Procedure (*args, **kwargs).digest (h)
        return h.digest ()

    def test_digest (self):
        self.assertEqual (self._get_digest ([]), self._get_digest ([]))
        self.assertEqual (self._get_digest ([], locn=SourceLocation ('path', line=2, column=3)),
                          self._get_digest ([], locn=SourceLocation ('path', line=2, column=3)))
        self.assertNotEqual (self._get_digest ([]),
                             self._get_digest ([], locn=SourceLocation ('path', line=2, column=3)))
        self.assertNotEqual (self._get_digest ([], locn=SourceLocation ('path', line=2, column=3)),
                             self._get_digest ([], locn=SourceLocation ('path', line=200, column=3)))

        self.assertNotEqual (self._get_digest ([]), self._get_digest ([ Boolean (False) ]))
        self.assertNotEqual (self._get_digest ([ Boolean (True) ]), self._get_digest ([ Boolean (False) ]))

    def test_iter (self):
        proc = Procedure ([Boolean (True), Boolean (False) ])
        self.assertSequenceEqual (list (p for p in proc), [ Boolean (True), Boolean (False) ])

    def test_call (self):
        m = Mock (spec=Machine)
        body = [ Boolean (True) ]
        proc = Procedure (body)
        proc (m)
        m.execution_push_proc.assert_called_once_with (body)

#eof toyvm/instruction/test/test_procedure.py
