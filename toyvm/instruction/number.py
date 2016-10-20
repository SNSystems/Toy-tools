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

import numbers
import struct
from typing import Any, BinaryIO, Mapping, Optional

from store.types import SectionType
from .instruction import Instruction
from .source_location import SourceLocation


class Number (Instruction):
    """
    A floating number literal object.
    """

    __struct = struct.Struct ('>d')

    def __init__ (self, value: float, locn: Optional [SourceLocation] = None) -> None:
        """
        :param value: The number associated with this instruction.
        :param locn: The source location for this instruction if known or None if not.
        """
        super ().__init__ (locn)
        assert isinstance (value, numbers.Number)
        self.__v = float (value)

    def value (self) -> float:
        """
        Returns the value represented by this instruction.
        """
        return self.__v

    def execute (self, machine: 'Machine') -> None:
        """
        Executing a number pushes it onto the machine's operand stack
        :param machine: The virtual machine which is executing this instruction.
        """
        machine.operand_push (self.__v)

    def _digest_impl (self, hasher) -> None:
        hasher.update (self.__v.hex ().encode ())

    def _read (self, sections: Mapping [SectionType, BinaryIO]) -> None:
        b = sections [SectionType.text].read (Number.__struct.size)
        (self.__v,) = Number.__struct.unpack (b)

    def _write (self, sections: Mapping [SectionType, BinaryIO]) -> None:
        sections [SectionType.text].write (Number.__struct.pack (self.__v))

    def __eq__ (self, other: Any) -> bool:
        return (isinstance (other, Number)
                and super ().__eq__ (other)
                and self.__v == other.__v)

    def __str__ (self) -> str:
        return 'number:' + str (self.__v)

    def __repr__ (self) -> str:
        return ('{classname}({number} {locn})'
                .format (classname=self.__class__.__name__,
                         number=self.__v,
                         locn=self._locn_str ()))

    def __hash__ (self):
        return hash (self.__v)


Number.add_class ()

# eof toyvm/instruction/number.py
