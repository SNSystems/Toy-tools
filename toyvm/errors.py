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

class VMError (Exception):
    pass


class UndefinedReferenceError (VMError):
    def __init__ (self, to, by):
        self.__to = to
        self.__by = by

    def __str__ (self):
        return "Undefined reference from '{by}' to '{to}'".format (by=self.__by, to=self.__to)

    def __repr__ (self):
        return "{0}(by={by},to={to})".format (self.__class__.__name__, by=self.__by, to=self.__to)


class NameNotFound (VMError):
    def __init__ (self, name):
        self.__name = name
    def __str_ (self):
        return "Undefined name {0}".format (self.__name)
    def __repr__ (self):
        return "{0}(name={1})".format (self.__class__.__name__, self.__name)


class TypeCheckError (VMError):
    """
    An exception which is thrown by the VM if the type of a value on the operand stack does not meet
    the requirements of a built-in operator.
    """

    def __init__ (self, name):
        self.__name = name

    def __str__ (self):
        return "typecheck (expected {0})".format (self.__name)

    def __repr__ (self):
        return "{0}(name={name})".format (self.__class__.__name__, name=self.__name)


class StackUnderflowError (VMError):
    """
    An exception which is raised by the VM if an attempt is made to pop a value from an empty stack.
    """

    def __str__ (self):
        return 'stackunderflow'

    def __repr__ (self):
        return self.__class__.__name__

#eof toyvm.errors
