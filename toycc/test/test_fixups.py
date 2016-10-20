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

from toycc.fixups import procedure_fixups
from toyvm.instruction import Number, Operator, Procedure
from toyvm.machine import Machine

class TestFixups (unittest.TestCase):

    def test_empty_procedure (self):
        fixups = procedure_fixups (Procedure ([]))
        self.assertEqual (fixups, [])

    def test_procedure_with_one_operator (self):
        fixups = procedure_fixups (Procedure ([ Operator ("foo") ]))
        self.assertEqual (fixups, [ 'foo' ])

    def test_procedure_with_one_operator_used_twice (self):
        fixups = procedure_fixups (Procedure ([
            Operator ('foo'),
            Operator ('foo'),
        ]))
        self.assertEqual (fixups, [ 'foo' ])

    def test_procedure_with_two_different_operators (self):
        fixups = procedure_fixups (Procedure ([
            Operator ('foo'),
            Operator ('bar'),
        ]))
        self.assertEqual (sorted (fixups), sorted ([ 'foo', 'bar' ]))

    def test_procedure_with_unnamed_instruction (self):
        fixups = procedure_fixups (Procedure ([
            Operator ('foo'),
            Number (1.0)
        ]))
        self.assertEqual (fixups, [ 'foo' ])

    def test_procedure_with_builtin_operator (self):
        name = list (Machine ().systemdict ().keys ()) [0]
        fixups = procedure_fixups (Procedure ([
            Operator (name),
            Number (1.0)
        ]))
        self.assertEqual (fixups, [ ])

    def test_nested_procedure (self):
        inner_proc = Procedure ([ Operator ('foo') ])
        outer_proc = Procedure ([ Operator ('bar'), inner_proc ])
        fixups = procedure_fixups (outer_proc)
        self.assertEqual (sorted (fixups), sorted ([ 'foo', 'bar' ]))

#eof toycc/test/test_fixups.py
