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

import struct
from typing import Any, BinaryIO, Mapping

from store.types import SectionType
from .instruction import Instruction
from .source_location import SourceLocation

class String (Instruction):
    """
    An instruction which, when executed, will push a string object onto the execution stack
    """
    __struct = struct.Struct ('>I')

    def __init__ (self, value:str, locn:SourceLocation=None) -> None:
        super ().__init__ (locn)
        assert isinstance (value, str)
        self.__v = value

    def execute (self, machine:'Machine') -> None:
        """
        Executing a string instructions simply pushes its value onto the operand stack.
        :param machine: The virtual machine executing this instruction.
        """
        machine.operand_push (self.__v)

    def _digest_impl (self, hasher) -> None:
        hasher.update (self.__v.encode ())

    def _write (self, sections:Mapping [SectionType, BinaryIO]) -> None:
        text_stream = sections [SectionType.text]
        encoded_str = self.__v.encode ()
        text_stream.write (String.__struct.pack (len (encoded_str)))
        text_stream.write (encoded_str)

    def _read (self, sections:Mapping [SectionType, BinaryIO]) -> None:
        text_stream = sections [SectionType.text]
        b = text_stream.read (String.__struct.size)
        (length,) = String.__struct.unpack (b)
        self.__v = text_stream.read (length).decode ()

    def __eq__ (self, other:Any) -> bool:
        return (isinstance (other, String) and super().__eq__ (other) and self.__v == other.__v)

    def __str__ (self) -> str:
        return 'string:"{value}"'.format (value=self.__v)
    def __repr__ (self) -> str:
        return '{classname}("{value}" {locn})'.format (classname=self.__class__.__name__,
                                                       value=self.__v,
                                                       locn=self._locn_str ())
String.add_class ()

#eof toyvm/instruction/string.py
