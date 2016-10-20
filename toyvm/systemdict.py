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

from . import builtins

class ReadOnlyDict (dict):
    def __readonly__ (self, *args, **kwargs):
        raise RuntimeError ('Cannot modify ReadOnlyDict') # FIXME: a subclass of VMerror

    __setitem__ = __readonly__
    __delitem__ = __readonly__
    pop = __readonly__
    popitem = __readonly__
    clear = __readonly__
    update = __readonly__
    setdefault = __readonly__
    del __readonly__


def systemdict ():
    return ReadOnlyDict ({
        'add': builtins.op_add,
        'begin': builtins.op_begin,
        'currentdict': builtins.op_currentdict,
        'currenttrace': builtins.op_currenttrace,
        'def': builtins.op_def,
        'dict': builtins.op_dict,
        'div': builtins.op_div,
        'dup': builtins.op_dup,
        'end': builtins.op_end,
        'eq': builtins.op_eq,
        'exch': builtins.op_exch,
        'exec': builtins.op_exec,
        'for': builtins.op_for,
        'get': builtins.op_get,
        'if': builtins.op_if,
        'ifelse': builtins.op_ifelse,
        'known': builtins.op_known,
        'mul': builtins.op_mul,
        'ne': builtins.op_ne,
        'pop': builtins.op_pop,
        'print': builtins.op_print,
        'sub': builtins.op_sub,
        'stack': builtins.op_stack,
        'systemdict': builtins.op_systemdict,
        'trace': builtins.op_trace,
    })

#eof toyvm/systemdict.py
