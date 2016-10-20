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

# System imports
import functools
import logging

# Local imports
import toyvm.instruction as instruction
from toyvm import errors
from toydb import list_cmd


_logger = logging.getLogger (__name__)

def _interrupt (machine):
    machine.interrupt ()


def _interrupt_and_remove (machine, instructions, index):
    # Tell the VM to stop executing instructions.
    machine.interrupt ()

    # Kill the instruction that step_handler() inserted into the procedure.
    assert isinstance (instructions [index], instruction.BuiltinState)
    del instructions [index]


def step_handler (machine, tokens, over=False):
    if len (tokens) != 0:
        _logger.warning ('Unexpected arguments')
    if len (machine.exec_s) == 0:
        _logger.error ('No instruction to execute')
        return

    patched = False
    try:
        instr = machine.exec_s.pop ()

        # Examine the instruction. If it's a user-defined operator (i.e. results in the body of a
        # Procedure instruction being pushed onto the execution stack, then I modify that procedure so that
        # the first instruction issues a machine interrupt to stop the processor and commit suicide
        # to ensure that the user sees an unmodified program.

        if not over and isinstance (instr, instruction.Operator):
            operator = machine.find_operator (instr.name ())
            if isinstance (operator, instruction.Procedure):
                instructions = operator.instructions ()
                callback = functools.partial (_interrupt_and_remove,
                                              instructions=instructions,
                                              index=0)
                instructions [0:0] = [ instruction.BuiltinState (callback) ]

                patched = True

        # If we didn't patch a user-defined operator then this is a simple instruction: simply stop the
        # machine after it has been executed.

        if not patched:
            machine.exec_s.push (instruction.BuiltinState (_interrupt))

        # Finally push this instruction and execute it.
        machine.exec_s.push (instr)
        machine.run_all ()

        if len (machine.exec_s) > 0:
            instr = machine.exec_s.peek ()
            list_cmd.show_location (instr.locn ())

    except errors.VMError as ex:
        _logger.error ('Exception: %s', str (ex))


def next_handler (machine, tokens):
    return step_handler (machine, tokens, over=True)

#eof toydb/step_cmd.py
