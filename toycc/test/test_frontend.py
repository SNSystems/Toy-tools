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

import pyparsing as pp
import unittest

from toycc import frontend
import toyvm.instruction as instruction

class TestFrontEnd (unittest.TestCase):

    def _as_number (self, string):
        return frontend._number.parseString (string, parseAll=True).asList ()

    def test_number (self):
        Number = instruction.Number
        self.assertEqual (self._as_number (' 0 '), [ Number (0.0) ])
        self.assertEqual (self._as_number ('1'), [ Number (1.0) ])
        self.assertEqual (self._as_number ('3.14'), [ Number (3.14) ])
        self.assertEqual (self._as_number ('73.'), [ Number (73) ])
        self.assertEqual (self._as_number ('-1'), [ Number (-1) ])
        self.assertEqual (self._as_number ('-3.14'), [ Number (-3.14) ])
        self.assertEqual (self._as_number ('-3.14'), [ Number (-3.14) ])
        self.assertEqual (self._as_number ('0.314e1'), [ Number (3.14) ])
        self.assertEqual (self._as_number ('314e-2'), [ Number (3.14) ])
        self.assertEqual (self._as_number ('314E-2'), [ Number (3.14) ])
        self.assertEqual (self._as_number ('  9999999'), [ Number (9999999) ])
        self.assertRaises (pp.ParseException, self._as_number, 'a')
        self.assertRaises (pp.ParseException, self._as_number, '--2.0')
        self.assertRaises (pp.ParseException, self._as_number, '2a1')
        self.assertRaises (pp.ParseException, self._as_number, '214ee-2')


    def _as_operator (self, string):
        return frontend._operator.parseString (string, parseAll=True).asList ()

    def test_operator (self):
        Operator = instruction.Operator
        self.assertEqual (self._as_operator (' ident '), [ Operator ('ident') ])
        self.assertEqual (self._as_operator ('iDENT '), [ Operator ('iDENT') ])
        self.assertEqual (self._as_operator ('under_score'), [ Operator ('under_score') ])
        self.assertRaises (pp.ParseException, self._as_operator, '_leading_underscore')
        self.assertRaises (pp.ParseException, self._as_operator, '2LeadingNumber')
        self.assertRaises (pp.ParseException, self._as_operator, 'badchar%')


    def _as_boolean (self, string):
        return frontend._boolean.parseString (string, parseAll=True).asList ()

    def test_boolean (self):
        self.assertEqual (self._as_boolean ('true'), [ instruction.Boolean (True) ])
        self.assertEqual (self._as_boolean ('false'), [ instruction.Boolean (False) ])
        self.assertRaises (pp.ParseBaseException, self._as_boolean, 'True')
        self.assertRaises (pp.ParseBaseException, self._as_boolean, 'False')
        self.assertRaises (pp.ParseBaseException, self._as_boolean, 'TRUE')
        self.assertRaises (pp.ParseBaseException, self._as_boolean, 'vero')


    def _as_string (self, string):
        return frontend._string.parseString (string, parseAll=True).asList ()

    def test_string (self):
        self.assertEqual (self._as_string ('"str"'), [ instruction.String ('str') ])
        self.assertEqual (self._as_string ('"  az01-=!@&*)Z "'), [ instruction.String ('  az01-=!@&*)Z ') ])


    def _as_procedure (self, string):
        return frontend._procedure.parseString (string, parseAll=True).asList ()

    def test_procedure (self):
        self.assertEqual (self._as_procedure ('{ }'), [ instruction.Procedure ([]) ])
        self.assertEqual (self._as_procedure ('{ 1 }'), [ instruction.Procedure ([ instruction.Number (1) ]) ])

        empty_with_comment = '''{
        # comment 1
        }'''
        self.assertEqual (self._as_procedure (empty_with_comment), [ instruction.Procedure ([]) ])

        body = [ instruction.Procedure ([ instruction.Operator ('operator') ]) ]
        self.assertEqual (self._as_procedure ('{ operator }'), body)

        body = [ instruction.Number (1), instruction.Operator ('operator'), instruction.String ('string') ]
        self.assertEqual (self._as_procedure ('{ 1 operator "string" }'), [ instruction.Procedure (body) ])

#eof toycc/test/test_frontend.py
