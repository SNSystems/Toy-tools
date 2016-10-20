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

from typing import Callable, Optional, Union

from toyvm import errors, stack
from . import systemdict


class Machine:
    """
    Represents the virtual machine with its state, the main run loop, and the built-in operators.

    There are two public instance variables:

    operand_s: the machine's operand stack
    exec_s: the machine's execution stack
    """

    def __init__ (self) -> None:
        """
        Creates the operand, execution, and dictionary stacks.
        """
        self.__trace = False
        self.operand_s = stack.Stack ()
        self.exec_s = stack.Stack ()
        self.dict_s = stack.Stack ()
        self.__running = True

        self.dict_s.push (systemdict.systemdict ())

    def reset (self) -> None:
        """
        Resets the VM to its initial state creating empty operand, execution, and dictionary stacks.
        """
        self.__trace = False
        self.operand_s = stack.Stack ()
        self.exec_s = stack.Stack ()
        self.dict_s = stack.Stack ()
        self.dict_s.push (systemdict.systemdict ())
        self.__running = True

    def find_operator (self, name: str) -> Optional [Callable]:
        for index in range (0, len (self.dict_s)):
            d = self.dict_s.peek (index)
            value = d.get (name, None)
            if value is not None:
                assert callable (value)
                return value
        return None

    def execute_operator (self, name: str):
        """
        :param name: The name of the operator or procedure to be run.
        """
        value = self.find_operator (name)
        if value is None:
            raise errors.NameNotFound (name)
        assert callable (value)
        return value (self)

    def operand_push (self, v) -> None:
        """
        Pushes the value 'v' onto the operand stack.
        :param v: The value to be pushed.
        :return: None
        """
        self.operand_s.push (v)

    def execution_push_proc (self, proc) -> None:
        """
        Pushes the instructions contained within 'proc' onto the execution stack
        :param proc: An iterable containing instructions to be pushed onto the execution stack.
        :return: None
        """
        self.exec_s.pushall (proc)

    def systemdict (self):
        return systemdict.systemdict ()

    def interrupt (self) -> None:
        self.__running = False

    def trace (self, enabled: Union [None, bool] = None) -> bool:
        """
        Enables or disables the VM instruction trace.
        This is equivalent to the program executing the 'trace' builtin.
        :param enabled: If not None, the new trace state for the machine.
        :returns: The machine's trace state
        """
        if enabled is not None:
            self.__trace = bool (enabled)
        return self.__trace

    def run_all (self) -> None:
        """
        Pops instructions from the execution stack until it is exhausted or the interrupt() method is called.
        """
        while self.__running and not self.exec_s.empty ():
            op = self.exec_s.pop ()
            if self.__trace:
                print (str (op))
            op.execute (self)
        self.__running = True

    def run (self, program) -> None:
        """
        Runs the given program.
        """
        self.dict_s.push (program)
        self.execute_operator ('main')
        self.run_all ()
        self.dict_s.pop ()

# eof toyvm.machine.py
