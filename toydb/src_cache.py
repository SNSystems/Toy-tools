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
Cache lines from files.
"""

import abc
import codecs
import logging
import os

from typing import Iterable, List, Optional

_logger = logging.getLogger (__name__)


class ReaderBase (metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def stat (self, path: str) -> os.stat_result:
        pass

    @abc.abstractmethod
    def readlines (self, path: str) -> List [str]:
        return []


class FileReader (ReaderBase):
    def stat (self, path: str) -> os.stat_result:
        return os.stat (path)

    def readlines (self, path: str) -> List [str]:
        # TODO: use something like the chardet library to determine the real file encoding?
        encoding = 'utf-8'
        with open (path, 'rb') as file:
            info = codecs.lookup (encoding)
            reader = info.streamreader (file)
            return reader.readlines (keepends=False)


def get_line (filename: str, lineno: int, reader: ReaderBase = FileReader ()) -> str:
    lines = get_lines (filename, reader)
    if 1 <= lineno <= len (lines):
        return lines [lineno - 1]
    else:
        return ''


# The cache
class _CacheEntry:
    def __init__ (self, reader: ReaderBase, size: int, mtime: int, lines: Iterable [str], fullname: str) -> None:
        self.reader = reader
        self.size = size
        self.mtime = mtime
        self.lines = lines
        self.fullname = fullname


_cache = dict ()  # The cache


def clear_cache () -> None:
    """Clear the cache entirely."""

    global _cache
    _cache = dict ()


def get_lines (filename: str, reader: ReaderBase = FileReader ()) -> List [str]:
    """Get the lines for a file from the cache.
    Update the cache if it doesn't contain an entry for this file already."""

    return _cache [filename].lines if filename in _cache else _update_cache (filename, reader)


def check_cache (filename: Optional [str] = None) -> None:
    """Discard cache entries that are out of date.
    (This is not checked upon each call!)"""

    if filename is None:
        filenames = list (_cache.keys ())
    elif filename in _cache:
        filenames = [filename]
    else:
        return

    for filename in filenames:
        entry = _cache [filename]
        try:
            stat = entry.reader.stat (filename)
        except OSError:
            _logger.debug ('Removing "%s" from the cache [stat() error]', filename)
            del _cache [filename]
            continue

        if entry.size != stat.st_size or entry.mtime != stat.st_mtime:
            _logger.debug ('Removing "%s" from the cache [size/time changed]', filename)
            del _cache [filename]


def _update_cache (filename: str, reader: ReaderBase) -> List [str]:
    """Update a cache entry and return its list of lines.
    If something's wrong, discard the cache entry and return an empty list."""

    if filename in _cache:
        del _cache [filename]

    if not filename:
        return []

    try:
        stat = reader.stat (filename)
    except OSError:
        _logger.warning ("Could not stat '%s'", filename)

    try:
        lines = reader.readlines (filename)
    except OSError:
        _logger.debug ('Read from "%s" failed.', filename)
        return []

    if lines and not lines [-1].endswith ('\n'):
        lines [-1] += '\n'

    _cache [filename] = _CacheEntry (reader=reader, size=stat.st_size, mtime=stat.st_mtime, lines=lines,
                                     fullname=filename)
    return lines

# eof src_cache.py
