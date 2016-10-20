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
from toyvm.instruction.boolean import Boolean

class TestBoolean (unittest.TestCase):

    # TODO: test the read and write methods

    def test_equal (self):
        btrue = Boolean (True)
        bfalse = Boolean (False)
        self.assertEqual (btrue, Boolean (True))
        self.assertEqual (bfalse, Boolean (False))
        self.assertNotEqual (bfalse, btrue)

    def test_execute (self):
        m = Mock (spec=Machine)
        Boolean (True).execute (m)
        Boolean (False).execute (m)
        m.operand_push.assert_has_calls ([ call (True), call (False) ])

    def test_digest (self):
        htrue = hashlib.new ('md5')
        Boolean (True).digest (htrue)
        hfalse = hashlib.new ('md5')
        Boolean (False).digest (hfalse)
        self.assertNotEqual (htrue.digest (), hfalse.digest ())

#eof toyvm/instruction/test/test_boolean.py
