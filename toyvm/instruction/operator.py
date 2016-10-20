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


class Operator (Instruction):

    __struct = struct.Struct ('>I')

    def __init__ (self, name:str, locn:SourceLocation=None):
        super ().__init__ (locn)
        assert isinstance (name, str)
        self.__name = name

    def name (self) -> str:
        """
        :return: The name of the operator.
        """
        return self.__name

    def execute (self, machine:'Machine') -> None:
        """
        Executing an operator runs it.
        :param machine: The virtual machine executing this instruction.
        """
        machine.execute_operator (self.__name)

    def _digest_impl (self, hasher) -> None:
        hasher.update (self.__name.encode ())


    def _read (self, sections:Mapping [SectionType, BinaryIO]) -> None:
        text_stream = sections [SectionType.text]
        b = text_stream.read (Operator.__struct.size)
        (length,) = Operator.__struct.unpack (b)
        self.__name = text_stream.read (length).decode ()

    def _write (self, sections:Mapping [SectionType, BinaryIO]) -> None:
        name = self.__name.encode ()
        text_stream = sections [SectionType.text]
        text_stream.write (Operator.__struct.pack (len (name)))
        text_stream.write (name)


    def __eq__ (self, other:Any) -> bool:
        return (isinstance (other, Operator) and super().__eq__ (other) and self.__name == other.__name)

    def __str__ (self) -> str:
        return 'operator:{0}'.format (self.__name)

    def __repr__ (self) -> str:
        return '{classname}({name} {locn})'.format (classname=self.__class__.__name__,
                                                    name=self.__name,
                                                    locn=self._locn_str ())
Operator.add_class ()
