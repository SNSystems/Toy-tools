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
Produces the list of names that are referenced by a named procedure.
"""

from typing import Iterable, Set

from toyvm import machine
from toyvm.instruction import Instruction

# Get the set of names that the machine knows and implements. We don't emit fixups for these.
_RUNTIME_BUILTINS = set (machine.Machine ().systemdict ().keys ())


def _procedure_references (procedure: Instruction) -> Set[str]:
    assert isinstance (procedure, Instruction)
    r = set ()
    for instruction in procedure.instructions ():
        r.add (instruction.name ())
        r |= _procedure_references (instruction)
    return r


def procedure_fixups (procedure:Instruction) -> Iterable[str]:
    """
    Produces the list of names that are referenced by a procedure.

    :param procedure: The procedure whose members are to be searched.
    :return: A list of names.
    """

    # Get the set of names referenced by this procedure.
    f = _procedure_references (procedure)

    # Remove the machine's builtin operators from the set that we return: a user doesn't explicitly need
    # to link these names into the program. Here I also remove 'None' from the set; these come from calling
    # the name() method on instructions that don't have a name, such as Numbers. Removing it here
    # simplifies the loop above.

    return list (f.difference (_RUNTIME_BUILTINS | { None }))

#eof toycc.fixups
