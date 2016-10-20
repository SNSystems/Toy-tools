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

import io
import struct
from typing import Any, BinaryIO

from store.types import SectionType


class SourceLocation:
    __struct = struct.Struct ('>IIII')

    def __init__ (self, srcfile: str = '<unknown>', line: int = 0, column: int = 0) -> None:
        self.srcfile = srcfile
        self.line = line
        self.column = column

    def write (self, debug_line: BinaryIO, offset: int) -> None:
        srcfile_encoded = self.srcfile.encode ()  # The full path of the source file as UTF-8
        debug_line.write (SourceLocation.__struct.pack (offset, self.line, self.column, len (srcfile_encoded)))
        debug_line.write (srcfile_encoded)

    @classmethod
    def construct (cls, debug_line: BinaryIO):
        b = debug_line.read (SourceLocation.__struct.size)
        offset, line, column, length = SourceLocation.__struct.unpack (b)
        srcfile = debug_line.read (length).decode ()
        return cls (srcfile=srcfile, line=line, column=column)

    def digest (self, hasher) -> None:
        hasher.update (self.srcfile.encode ())
        hasher.update (self.line.to_bytes (4, byteorder='big'))
        hasher.update (self.column.to_bytes (4, byteorder='big'))

    def __eq__ (self, other: Any) -> bool:
        return (isinstance (other,
                            SourceLocation) and self.srcfile == other.srcfile and self.line == other.line and
                self.column == other.column)

    def __ne__ (self, other: Any) -> bool:
        return not self.__eq__ (other)

    def __repr__ (self) -> str:
        return ("{classname}(['{file}' ({line},{col})])"
                .format (classname=self.__class__.__name__,
                         file=self.srcfile,
                         line=self.line,
                         col=self.column))

    def __str__ (self) -> str:
        return "['{file}' ({line},{col})]".format (file=self.srcfile, line=self.line, col=self.column)

# eof toyvm/instruction/source_location.py
