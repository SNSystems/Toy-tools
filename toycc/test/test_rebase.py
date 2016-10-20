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

from toycc import rebase
from toyvm.instruction import Number, Procedure, SourceLocation


class test_rebaser (unittest.TestCase):
    def test_empty_procedure_no_location (self):
        body = []
        proc = Procedure (body, locn=None)
        result = rebase.rebase_source_info (proc)
        self.assertEqual (result.procedure, Procedure (body))
        self.assertEqual (result.line_base, None)

    def test_empty_procedure (self):
        filename = 'filename'
        first = 47
        locn = SourceLocation (srcfile=filename, line=first, column=7)
        proc = Procedure ([], locn=locn)

        result = rebase.rebase_source_info (proc)

        expected_proc = Procedure ([], locn=SourceLocation (srcfile=filename, line=0, column=7))
        self.assertEqual (result.procedure, expected_proc)
        self.assertEqual (result.line_base, first)

    def _make_body (self, srcfile, first):
        return [
            Number (1.0, locn=SourceLocation (srcfile, line=first + 1, column=1)),
            Number (2.0, locn=SourceLocation (srcfile, line=first + 1, column=9)),
            Number (3.0, locn=SourceLocation (srcfile, line=first + 2, column=3)),
            Number (4.0, locn=SourceLocation (srcfile, line=first + 3, column=1)),
        ]

    def test_procedure_with_contents (self):
        filename = 'filename'
        first = 16
        proc = Procedure (self._make_body (srcfile=filename, first=first),
                          locn=SourceLocation (srcfile=filename, line=first, column=1))

        result = rebase.rebase_source_info (proc)

        expected_proc = Procedure (self._make_body (srcfile=filename, first=0),
                                   locn=SourceLocation (srcfile=filename, line=0, column=1))
        self.assertEqual (result.procedure, expected_proc)
        self.assertEqual (result.line_base, first)

# eof toycc/test/test_rebase.py
