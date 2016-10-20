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

# System modules
import collections
import functools
import unittest
from typing import Iterable, List

# Local modules
from toydb import src_cache

_StatStruct = collections.namedtuple ('_StatStruct', 'st_mtime st_size')

class _StringReader (src_cache.ReaderBase):
    LINES = [ ' line #1\n', ' line #2\n' ]

    def __init__ (self) -> None:
        self.__lines = _StringReader.LINES
        self.__modtime = 0

    def update_content (self, lines:Iterable[str]) -> None:
        self.__lines = lines
        # We're updating the contents of the 'file', so we also need
        # to update the modification time. Add a day (but this could be any
        # value really).
        self.__modtime += 60 * 60 * 24

    def stat (self, path: str) -> _StatStruct:
        return _StatStruct (st_mtime=self.__modtime,
                            st_size=sum (len (l) for l in self.__lines))

    def readlines (self, path: str) -> List [str]:
        return [ path + line for line in self.__lines ]


class _BadFileNameReader (src_cache.ReaderBase):
    def stat (self, path:str) -> _StatStruct:
        return _StatStruct (st_mtime=0, st_size=0)
    def readlines (self, path:str) -> List [str]:
        raise OSError ('bad file name reader')


class LineCacheTests (unittest.TestCase):

    def setUp (self):
        src_cache.clear_cache ()

    def tearDown (self):
        src_cache.clear_cache ()

    def test_get_line_with_bad_file_name (self):
        """
        Bad file names should return an empty string
        """
        self.assertEqual (src_cache.get_line ('invalid name', 1, reader=_BadFileNameReader ()), '')

    def test_get_line_contents (self):
        """
        Check that calls to get_line() return strings that match the contents of the (simulated) files.
        """
        get_line = functools.partial (src_cache.get_line, reader=_StringReader ())

        # Check whether lines correspond to those from file iteration
        for filename in ('file #1', 'file #2'):
            for index, line in enumerate (filename + l for l in _StringReader.LINES):
                self.assertEqual (line, get_line (filename, index + 1))

    def test_get_line_number_out_of_range (self):
        """
        Check the behaviour of src_cache.get_line if line numbers are out-of-range.
        """
        get_line = functools.partial (src_cache.get_line, reader=_StringReader ())

        # Bad values for line number should return an empty string
        self.assertEqual (get_line ('filename', 2**15), '')
        self.assertEqual (get_line ('filename', -1), '')

        # Float values currently raise TypeError, should it?
        self.assertRaises (TypeError, get_line, 'filename', 1.1)

    def test_no_ending_newline (self):
        class StringReaderNoNewline (_StringReader):
            def readlines (self, path):
                return [ 'line' ]

        lines = src_cache.get_lines ('filename', reader=StringReaderNoNewline ())
        self.assertEqual (lines, [ 'line\n' ])

    def test_clearcache (self):
        cached = [ 'file #1', 'file #2' ]
        for filename in cached:
            src_cache.get_line (filename, 1, reader=_StringReader ())

        # Are all files cached?
        cached_empty = [ fn for fn in cached if fn not in src_cache._cache ]
        self.assertEqual (cached_empty, [])

        # Can we clear the cache?
        src_cache.clear_cache ()
        cached_empty = [ fn for fn in cached if fn in src_cache._cache ]
        self.assertEqual (cached_empty, [])

    def test_checkcache (self):
        reader = _StringReader ()
        getline = functools.partial (src_cache.get_line, reader=reader)

        # Create a source file and cache its contents
        source_name = 'source name'
        getline (source_name, 1)

        # Keep a copy of the old contents
        #source_list = []
        for index, line in enumerate (_StringReader.LINES, start=1):
            self.assertEqual (source_name + line, getline (source_name, index))
            #source_list.append (line)

        new_contents = [ ' updated line #1\n', ' updated line #2\n' ]
        reader.update_content (lines=new_contents)

        # Try to update a bogus cache entry
        src_cache.check_cache ('dummy')

        # Check that the cache matches the old contents
        for index, line in enumerate (_StringReader.LINES, start=1):
            self.assertEqual (source_name + line, getline (source_name, index))

        # Update the cache and check whether it matches the new source file
        src_cache.check_cache (source_name)
        for index, line in enumerate (new_contents, start=1):
            self.assertEqual (source_name + line, getline (source_name, index))

if __name__ == "__main__":
    unittest.main ()

#eof test_src_cache.py
