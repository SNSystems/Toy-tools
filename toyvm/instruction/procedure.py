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

import itertools
import struct
from typing import Any, BinaryIO, Dict, Iterable, List

from store.types import SectionType
from .instruction import Instruction
from .source_location import SourceLocation

class Procedure (Instruction):
    """
    Represents a procedure, that is, a brace-encoded list of instructions (which may include nested
    procedures).
    """

    def __init__ (self, v: Iterable [Instruction], locn: SourceLocation = None) -> None:
        super ().__init__ (locn)
        self.__v = list (v)

    def instructions (self) -> List [Instruction]:
        """
        :return: The list of instructions in this procedure.
        """
        return self.__v

    def execute (self, machine:'Machine') -> None:
        """
        'Executing' a procedure simply pushes it onto the VM's operand stack.
        :param machine: The virtual machine executing this instruction.
        """
        machine.operand_push (self)

    def __call__ (self, machine:'Machine') -> None:
        """
        Calling a procedure -- like calling a built-in function -- runs it. To do this, we push the body of the
        function onto the VM's execution stack.
        :param machine: The virtual machine executing this instruction.
        """
        machine.execution_push_proc (self.__v)

    def _digest_impl (self, hasher) -> None:
        """Adds a procedure array to the supplied hash instance."""

        hasher.update (len (self.__v).to_bytes (4, byteorder='big'))
        for f in self.__v:
            f.digest (hasher)

    __struct = struct.Struct ('>I')

    def _write (self, sections: Dict [SectionType, BinaryIO]) -> None:
        """
        Writes the contents of a procedure 'instruction' including all of the instrucitons making up its body.
        :param sections:
        :return: None
        """
        sections [SectionType.text].write (Procedure.__struct.pack (len (self.__v)))
        for instr in self.__v:
            instr.write (sections)

    def _read (self, sections: Dict [SectionType, BinaryIO]) -> None:
        text_stream = sections [SectionType.text]
        b = text_stream.read (Procedure.__struct.size)
        (length,) = Procedure.__struct.unpack (b)
        self.__v = [Instruction.read (sections) for _ in range (length)]

    def read_debug (self, binary:BinaryIO, line_base:int) -> None:
        for instr in self.__v:
            instr.read_debug (binary, line_base)
        super ().read_debug (binary, line_base)

    def __eq__ (self, other: Any) -> bool:
        return (isinstance (other, Procedure) and super ().__eq__ (other) and all (
                a == b for a, b in itertools.zip_longest (self.__v, other.__v, fillvalue=None)))

    def __iter__ (self) -> None:
        """
        Returns an generator which will enumerate the members of the procedure.
        """
        for member in self.__v:
            yield member

    _MAX_LENGTH = 60

    def __str__ (self) -> str:
        result = '{ ' + ' '.join (str (member) for member in self.__v) + ' }'
        if len (result) > Procedure._MAX_LENGTH:
            result = result [:Procedure._MAX_LENGTH] + '...'
        return result

    def __repr__ (self) -> str:
        members = '{ ' + ' '.join (str (member) for member in self.__v) + ' }'
        if len (members) > Procedure._MAX_LENGTH:
            members = members [:Procedure._MAX_LENGTH] + '...'
        return '{classname}({members} {locn})'.format (classname=self.__class__.__name__,
                                                       members=members,
                                                       locn=self._locn_str ())


Procedure.add_class ()

# eof toyvm/instruction/procedure
