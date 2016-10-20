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
Adjusts source correspondence so that it is relative to the first line of a function.
"""

from toyvm.instruction import Instruction, SourceLocation
from .types import ProcedureRecord

class _LineRebaser:
    """
    A simple class which rebases the source line numbers for a procedure so that they start at
    zero. The offset that must be applied to restore the original numbers is returned by the base()
    method.
    """

    def __init__ (self) -> None:
        self.__base = None

    def base (self) -> int:
        """
        :return: The offset that must be added to the source line numbers to make them absolute values once again.
        """

        return self.__base

    def update (self, procedure: Instruction) -> None:
        """
        Re-bases the given procedure and any nested procedures.
        :param procedure: The procedure to be re-based.
        :return: Nothing
        """

        self.__rebase_instruction (procedure)
        for inst in procedure.instructions ():
            self.update (inst)

    def __rebase_instruction (self, inst: Instruction) -> None:
        """
        Modifies an individual instruction so that its line number is relative to the start of its containing
        procedure. If this is the first instruction of the procedure, then it establishes the base value to be
        subtracted from subsequent instructions.

        :param inst: The instruction to be re-based.
        :return: Nothing
        """

        locn = inst.locn ()
        if locn is not None:
            assert isinstance (locn, SourceLocation)
            if self.__base is None:
                assert locn.line is not None
                self.__base = locn.line
            assert locn.line >= self.__base
            locn.line -= self.__base


def rebase_source_info (procedure: Instruction) -> ProcedureRecord:
    """
    Re-bases the source-line correspondence for a procedure such that all of the instructions are relative rather
    than absolute.

    That is, the original line numbers can be recovered by adding the 'base' line number to the source lines
    store in the instruction's location.

    :param procedure:
    :return: ProcedureRecord containing of the rebased instruction and the first line of its source code.
    """

    rebaser = _LineRebaser ()
    rebaser.update (procedure)
    return ProcedureRecord (procedure=procedure, line_base=rebaser.base ())

# eof toycc/rebase.py
