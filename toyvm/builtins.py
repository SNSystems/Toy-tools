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
Implements the virtual machine's built-in operators.
"""

import functools
import numbers

from toyvm import errors
from toyvm.instruction import BuiltinState, Procedure


def _check_type (value, expected) -> None:
    if not isinstance (value, expected):
        raise errors.TypeCheckError (str (expected))


def op_print (m: 'machine.Machine') -> None:
    """
    str _print_ -

    Prints the object on the top of the operand stack to stdout.

    :param m: The virtual machine on which the instruction is to be executed.
    """
    print (m.operand_s.pop ())


def op_add (m: 'machine.Machine') -> None:
    """
    num_1 num_2 _add_ sum
    :param m: The virtual machine on which the instruction is to be executed.
    """
    num2 = m.operand_s.pop ()
    num1 = m.operand_s.pop ()
    _check_type (num2, numbers.Number)
    _check_type (num1, numbers.Number)
    m.operand_push (num1 + num2)


def op_def (m: 'machine.Machine') -> None:
    """
    key value _def_ --
    :param m: The virtual machine on which the instruction is to be executed.
    """
    value = m.operand_s.pop ()
    key = m.operand_s.pop ()
    d = m.dict_s.peek ()
    d [key] = value


def op_get (m: 'machine.Machine') -> None:
    """
    dict key _get_ any

    :param m: The virtual machine on which the instruction is to be executed.
    """
    key = m.operand_s.pop ()
    d = m.operand_s.pop ()
    _check_type (d, dict)
    result = d.get (key, None)
    if result is None:
        raise errors.NameNotFound (key)
    m.operand_push (result)


def op_known (m: 'machine.Machine') -> None:
    """
    dict key _known_ bool

    Returns true if there is an entry in the dictionary dict whose key is key; otherwise, it
    returns false. dict does not have to be on the dictionary stack.

    :param m: The virtual machine on which the instruction is to be executed.
    """
    key = m.operand_s.pop ()
    d = m.operand_s.pop ()
    _check_type (d, dict)
    m.operand_push (d.get (key) is not None)


def op_begin (m: 'machine.Machine') -> None:
    """

    :param m: The virtual machine on which the instruction is to be executed.
    """
    d = m.operand_s.pop ()
    _check_type (d, dict)
    m.dict_s.push (d)


def op_end (m: 'machine.Machine') -> None:
    """
    Pops the object from the top of the operand stack.

    :param m: The virtual machine on which the instruction is to be executed.
    """
    m.dict_s.pop ()


def op_dict (m: 'machine.Machine') -> None:
    """
    -- _dict_ dict
    Creates a new dictionary and pushes it onto the operand stack.

    :param m: The virtual machine on which the instruction is to be executed.
    """
    m.operand_push (dict ())


def op_currentdict (m: 'machine.Machine') -> None:
    """
    -- currentdict dict

    :param m: The virtual machine on which the instruction is to be executed.
    """
    m.operand_push (m.dict_s.peek ())


def op_sub (m: 'machine.Machine') -> None:
    """
    num_1 num_2 _sub_ difference
    :param m: The virtual machine on which the instruction is to be executed.
    """
    num2 = m.operand_s.pop ()
    num1 = m.operand_s.pop ()
    _check_type (num2, numbers.Number)
    _check_type (num1, numbers.Number)
    m.operand_push (num1 - num2)


def op_mul (m: 'machine.Machine') -> None:
    """
    num_1 num_2 _mul_ product
    :param m: The virtual machine on which the instruction is to be executed.
    """
    num2 = m.operand_s.pop ()
    num1 = m.operand_s.pop ()
    _check_type (num2, numbers.Number)
    _check_type (num1, numbers.Number)
    m.operand_push (num1 * num2)


def op_div (m: 'machine.Machine') -> None:
    """
    num_1 num_2 _div_ quotient
    :param m: The virtual machine on which the instruction is to be executed.
    """
    numerator = m.operand_s.pop ()
    denom = m.operand_s.pop ()
    _check_type (numerator, numbers.Number)
    _check_type (denom, numbers.Number)
    m.operand_push (numerator / denom)


def op_eq (m: 'machine.Machine') -> None:
    """
    :param m: The virtual machine on which the instruction is to be executed.
    """
    op1 = m.operand_s.pop ()
    op2 = m.operand_s.pop ()
    m.operand_push (op1 == op2)


def op_ne (m: 'machine.Machine') -> None:
    """
    :param m: The virtual machine on which the instruction is to be executed.
    """
    op1 = m.operand_s.pop ()
    op2 = m.operand_s.pop ()
    m.operand_push (op1 != op2)


def op_exec (m: 'machine.Machine') -> None:
    """
    :param m: The virtual machine on which the instruction is to be executed.
    """
    proc = m.operand_s.pop ()
    _check_type (proc, Procedure)
    m.execution_push_proc (proc)


def op_if (m: 'machine.Machine') -> None:
    """
    bool proc _if_ --

    Removes both operands from the stack, then executes proc if bool is true. The if operator pushes no results of
    its own on the operand stack, but proc may do so.

    :param m: The virtual machine on which the instruction is to be executed.
    """

    proc = m.operand_s.pop ()
    b = m.operand_s.pop ()  # the condition boolean
    _check_type (proc, Procedure)
    _check_type (b, bool)
    if b:
        m.execution_push_proc (proc)


def op_ifelse (m: 'machine.Machine') -> None:
    """
    bool proc1 proc2 _ifelse_ --

    Removes all three operands from the stack, then executes proc1 if bool is true or proc2 if bool is false. The
    ifelse operator pushes no results of its own on the operand stack, but the procedure it executes may do so.

    :param m: The virtual machine on which the instruction is to be executed.
    """

    false_proc = m.operand_s.pop ()
    true_proc = m.operand_s.pop ()
    b = m.operand_s.pop ()  # the condition boolean

    _check_type (true_proc, Procedure)
    _check_type (false_proc, Procedure)
    _check_type (b, bool)

    m.execution_push_proc (true_proc if b else false_proc)


def _push_for (m: 'machine.Machine', control: float, increment: float, limit: float, proc: Procedure) -> None:
    # Create a function which will handle the end of this iteration of the loop by invoking
    # self.__for_next() again.
    next_iteration = functools.partial (_for_next,
                                        control=control,
                                        limit=limit,
                                        increment=increment,
                                        proc=proc)

    m.operand_push (control)
    # FIXME: I set the source location to that of the procedure. It really ought to be the location of the
    # original 'for'.
    m.exec_s.push (BuiltinState (next_iteration, locn=proc.locn ()))
    m.execution_push_proc (proc)


def _for_next (m: 'machine.Machine', control: float, increment: float, limit: float, proc: Procedure) -> None:
    """
    This method is called when an iteration of a for loop is complete. It is responsible for incrementing the
    control variable, deciding whether the loop should terminate and, if not, pushing the next iteration onto
    the execution stack.

    :param control: The for loop's control variable value
    :param increment:  The for loop's increment
    :param limit:  The for loop's limit
    :param proc: The for loop's procedure.
    """
    if increment > 0:
        control += increment
        if control > limit:
            return
    else:
        control -= increment
        if control < limit:
            return
    _push_for (m, control, increment, limit, proc)


def op_for (m: 'machine.Machine') -> None:
    """
    initial increment limit proc _for_ --

    Executes the procedure 'proc' repeatedly, passing it a sequence of values from initial by steps of increment
    to limit. The 'for' operator expects initial, increment, and limit to be numbers. It maintains a temporary
    internal variable, known as the control variable, which it first sets to initial. Then, before each repetition,
    it compares the control variable to the termination value limit. If limit has not been exceeded, for pushes
    the control variable on the operand stack, executes proc, and adds increment to the control variable.

    The termination condition depends on whether increment is positive or negative. If increment is positive, 'for'
    terminates when the control variable becomes greater than 'limit'. If 'increment' is negative, for terminates
    when the control variable becomes less than 'limit'. If initial meets the termination condition, for does
    not execute 'proc' at all.

    :param m: The virtual machine on which the instruction is to be executed.
    """

    proc = m.operand_s.pop ()
    limit = m.operand_s.pop ()
    increment = m.operand_s.pop ()
    initial = m.operand_s.pop ()

    _check_type (proc, Procedure)
    _check_type (limit, numbers.Number)
    _check_type (increment, numbers.Number)
    _check_type (initial, numbers.Number)

    if (increment > 0 and initial < limit) or (increment < 0 and initial > limit):
        _push_for (m, initial, increment, limit, proc)


def op_dup (m: 'machine.Machine') -> None:
    """
    any _dup_ any any

    Duplicates the top element on the operand stack.

    :param m: The virtual machine on which the instruction is to be executed.
    """
    m.operand_push (m.operand_s.peek ())


def op_exch (m: 'machine.Machine') -> None:
    """
    :param m: The virtual machine on which the instruction is to be executed.
    """
    v1 = m.operand_s.pop ()
    v2 = m.operand_s.pop ()
    m.operand_push (v1)
    m.operand_push (v2)


def op_pop (m: 'machine.Machine') -> None:
    """
    any _pop_ --

    Removes the top element from the operand stack and discards it.

    :param m: The virtual machine on which the instruction is to be executed.
    """
    m.operand_s.pop ()


def op_stack (m: 'machine.Machine') -> None:
    """
    :param m: The virtual machine on which the instruction is to be executed.
    """
    for obj in m.operand_s:
        print (obj)


def op_currenttrace (m: 'machine.Machine') -> None:
    """
    -- _currenttrace_ bool

    Pushes the current tracing state (on or off) onto the operand stack

    :param m: The virtual machine on which the instruction is to be executed.
    """
    m.operand_push (m.trace ())


def op_systemdict (m: 'machine.Machine') -> None:
    """
    -- _systemdict_ dict

    Pushes the system dictionary onto the operand stack.

    :param m: The virtual machine on which the instruction is to be executed.
    """
    m.operand_push (m.systemdict ())


def op_trace (m: 'machine.Machine') -> None:
    """
    bool _trace_ --

    Sets the current tracing state to the given boolean. When enabled, the machine will emit a description
    of each instruction as it is executed.

    :param m: The virtual machine on which the instruction is to be executed.
    """
    b = m.operand_s.pop ()
    _check_type (b, bool)
    m.trace (b)

# eof toyvm/builtins.py
