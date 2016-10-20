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


class Boolean (Instruction):
    """
    A boolean literal object.
    """

    __struct = struct.Struct ('>?')

    def __init__ (self, value: bool, locn: SourceLocation = None) -> None:
        super ().__init__ (locn)
        assert value in (True, False)
        self.__v = value

    def execute (self, machine: 'Machine') -> None:
        """
        Executing a boolean pushes either True or False onto the machine's operand stack
        :param machine: The virtual machine which is executing this instruction.
        """
        machine.operand_push (self.__v)

    def _digest_impl (self, hasher) -> None:
        s = 't' if self.__v else 'f'
        hasher.update (s.encode ())

    def _read (self, sections: Mapping [SectionType, BinaryIO]) -> None:
        b = sections [SectionType.text].read (Boolean.__struct.size)
        (self.__v,) = Boolean.__struct.unpack (b)

    def _write (self, sections: Mapping [SectionType, BinaryIO]) -> None:
        sections [SectionType.text].write (Boolean.__struct.pack (self.__v))

    def __eq__ (self, other: Any) -> bool:
        return (isinstance (other, Boolean) and super ().__eq__ (other) and self.__v == other.__v)

    def __str__ (self) -> str:
        return 'push Bool:' + str (self.__v)

    def __repr__ (self) -> str:
        return '{classname}({value} {locn})'.format (classname=self.__class__.__name__,
                                                     value='true' if self.__v else 'false',
                                                     locn=self._locn_str ())


Boolean.add_class ()

# eof toyvm/instruction/boolean.py
