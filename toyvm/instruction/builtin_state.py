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

import collections
from typing import Any, BinaryIO, Callable, Mapping

from store.types import SectionType
from .instruction import Instruction
from .source_location import SourceLocation


class BuiltinState (Instruction):
    """
    BuiltinState is an unusual instruction in the sense that it has no representation in the user program.
    These instructions are created at runtime by the VM or debugger for the purpose of, for example, performing an
    iteration of a loop.

    The instruction is instantiated with a callable; executing it results in the callable being invoked.
    """

    def __init__ (self, function: Callable, locn: SourceLocation = None) -> None:
        super ().__init__ (locn)
        assert isinstance (function, collections.Callable)
        self.__function = function

    def execute (self, machine:'Machine') -> None:
        """
        Executing a built-in state calls it.
        :param machine: The virtual machine executing this instruction.
        """
        self.__function (machine)

    def _digest_impl (self, hasher) -> None:
        raise NotImplementedError ('BuiltinState._digest_impl')

    def _read (self, sections: Mapping [SectionType, BinaryIO]):
        raise NotImplementedError ('BuiltinState._read')

    def _write (self, sections: Mapping [SectionType, BinaryIO]):
        raise NotImplementedError ('BuiltinState._write')

    def __str__ (self) -> str:
        fn = str (self.__function)
        if len (fn) > 20:
            fn = fn [:20] + '...'
        return "builtin " + fn

    def __repr__ (self) -> str:
        return '{classname}({function} {locn})'.format (classname=self.__class__.__name__,
                                                        function=repr (self.__function),
                                                        locn=self._locn_str ())

    def __eq__ (self, other: Any) -> bool:
        return (isinstance (other, BuiltinState) and super ().__eq__ (other) and self.__function == other.__function)

# eof toyvm/instruciton/builtin_state.py
