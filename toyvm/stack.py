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
Whilst the python list type has pop() and append() methods to implement a stack, they operate from the _end_ of the
list. Our procedures are stored in the order in which the user wrote them and must execute in that order so to avoid
having to reverse all of the procedures, I use a stack in which pushes and pops operate on the
_front_ of the list. That's what this module provides.
"""

from typing import Any, Iterable

from . import errors


class Stack:
    """
    A stack implementation which implements push and pop as operations which manipulate the front of the list.
    """

    def __init__ (self) -> None:
        self.__members = list ()

    def push (self, v: Any) -> None:
        """
        Pushes the value 'v' onto the front of the stack
        """
        self.__members.insert (0, v)

    def pushall (self, v: Iterable) -> None:
        """
        Pushes each of the members of the iterable value 'v' onto the front of the stack.
        """
        self.__members [0:0] = v

    def pop (self) -> Any:
        """
        Pops the front value from the stack and returns it. If the stack is empty, a StackUnderflowError
        exception is raised.
        """
        if len (self.__members) < 1:
            raise errors.StackUnderflowError ()
        return self.__members.pop (0)

    def peek (self, depth=0) -> Any:
        """
        Peeks at the top value on the stack and returns it: the stack contents are not affected. If the stack
        was empty, a StackUnderflowError exception is raised.
        """
        if len (self.__members) < depth + 1:
            raise errors.StackUnderflowError ()
        return self.__members [depth]

    def empty (self) -> bool:
        """
        Return True if the stack is empty, False otherwise.
        """
        return len (self.__members) == 0

    def __len__ (self) -> int:
        """
        Used by the Python built-in len() method to return the number of items on the stack.
        """
        return len (self.__members)

    def __iter__ (self):
        """
        Returns an generator which will enumerate the items on the stack starting at the top.
        """
        for v in self.__members:
            yield v

# eof toyvm.stack
