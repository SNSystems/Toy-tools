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
from toydb import commands


class TestGetCandidates (unittest.TestCase):

    def test_match_with_no_candidates (self):
        command_dict = dict ()
        actual = commands.get_candidates ('a', command_dict)
        self.assertEqual (actual, command_dict)
    def test_match_with_no_input_string_and_one_candidate (self):
        command_dict = { 'a' : 1 }
        actual = commands.get_candidates ('', command_dict)
        self.assertEqual (actual, dict ())


    def test_matching_single_letter_with_single_command (self):
        command_dict = { 'opstack': 1 }
        actual = commands.get_candidates ('o', command_dict)
        self.assertEqual (actual, command_dict)
    def test_match_entire_with_single_command (self):
        command_dict = { 'opstack': 1 }
        actual = commands.get_candidates ('opstack', command_dict)
        self.assertEqual (actual, command_dict)


    def test_mismatch_single_letter_with_single_command (self):
        actual = commands.get_candidates ('c', {'opstack': 1})
        self.assertEqual (actual, dict ())
    def test_mismatch_beyond_end_of_single_command (self):
        actual = commands.get_candidates ('opstackQ', {'opstack': 1})
        self.assertEqual (actual, dict ())


    def test_single_letter_with_multiple_matches (self):
        command_dict = { 'start': 1, 'stop': 2, 'nomatch': 3 }
        actual = commands.get_candidates ('s', command_dict)
        self.assertEqual (actual, { 'start': 1, 'stop': 2 })

    def test_single_letter_with_multiple_commands_single_match (self):
        command_dict = { 'start': 1, 'stop': 2, 'match': 3 }
        actual = commands.get_candidates ('m', command_dict)
        self.assertEqual (actual, { 'match': 3 })


class TestCommandFromString (unittest.TestCase):

    def test_one_match (self):
        command_dict = { 'hello': 1, 'world': 2 }
        actual = commands.from_string ('h', command_dict)
        expected = { 'hello': 1 }
        self.assertEqual (actual, expected)

    def test_no_matches (self):
        with self.assertRaises (commands.UnknownCommandError):
            commands.from_string (input_str='a', commands={'hello': 1, 'world': 2})

    def test_multiple_matches (self):
        with self.assertRaises (commands.MultipleCommandError):
            commands.from_string (input_str='st', commands={'start': 1, 'stop': 2})

if __name__ == '__main__':
    unittest.main ()

#eof test_commands.py
