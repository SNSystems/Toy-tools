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
Tests for the Toy debugger's instruction and debug line information loading.
"""

import unittest

from store.types import SectionType
from toyvm.instruction import Instruction, Number, Procedure, SourceLocation


class LoadTests (unittest.TestCase):
    def setUp (self) -> None:
        self.__sections = dict ()

    def tearDown (self) -> None:
        pass

    def __reset (self) -> None:
        for binary in self.__sections.values ():
            binary.seek (0)

    def test_number_round_trip (self) -> None:
        Number (value=42.0, locn=SourceLocation (srcfile="foo.toy",
                                                 line=23,
                                                 column=29)).write (self.__sections)
        self.__reset ()

        n2 = Instruction.read (self.__sections)
        self.assertIsInstance (n2, Number)
        self.assertEqual (42.0, n2.value ())
        self.assertIsNone (n2.locn ())  # No debug line information yet.

        n2.read_debug (binary=self.__sections [SectionType.debug_line], line_base=0)
        l = n2.locn ()
        self.assertEqual ("foo.toy", l.srcfile)
        self.assertEqual (23, l.line)
        self.assertEqual (29, l.column)

    def test_procedure_round_trip (self) -> None:
        Procedure ([
            Number (value=42.0, locn=SourceLocation (srcfile="foo.toy", line=23, column=29)),
            Number (value=68.0, locn=SourceLocation (srcfile="foo.toy", line=24, column=31))
        ], locn=SourceLocation (srcfile="foo.toy", line=22, column=1)).write (self.__sections)
        self.__reset ()

        n2 = Instruction.read (self.__sections)
        self.assertIsInstance (n2, Procedure)

        expected = [Number (value=42.0), Number (value=68.0)]
        instructions = n2.instructions ()
        self.assertSequenceEqual (expected, instructions)

        n2.read_debug (binary=self.__sections [SectionType.debug_line], line_base=0)
        self.assertEqual (SourceLocation (srcfile="foo.toy", line=23, column=29), instructions [0].locn ())
        self.assertEqual (SourceLocation (srcfile="foo.toy", line=24, column=31), instructions [1].locn ())


if __name__ == "__main__":
    unittest.main ()

# eof toydb.test.test_load_cmd
