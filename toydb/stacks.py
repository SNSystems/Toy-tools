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
Implements the debugger commands that dump the contents of the three machine stacks.
"""

import logging
import pprint
from typing import Optional, Sequence

from toyvm.machine import Machine
from toyvm.stack import Stack

_logger = logging.getLogger (__name__)
_MAX_DEPTH = 20


class _StackDumper:
    def __init__ (self, stack:Stack, max_rows:int=_MAX_DEPTH) -> None:
        self.__iterator = enumerate (stack, start=1)
        self.__max_rows = max_rows
        self.__max_depth = 0

    def __call__ (self) -> Optional['_StackDumper']:
        self.__max_depth += self.__max_rows
        for depth, op in self.__iterator:
            obj = pprint.pformat (object=op)
            _logger.info ("{depth}: {obj}".format (depth=depth, obj=obj))
            if depth > self.__max_depth:
                _logger.info ('...')
                return self
        return None


def _dump_stack (stack:Stack) -> Optional['_StackDumper']:
    """
    Dumps the contents of the stack.
    :param stack:The stack to be dumped
    :return:
    """
    if len (stack) == 0:
        _logger.info ('<empty>')
    dumper = _StackDumper (stack)
    return dumper ()


# TODO: the return value is intended to be an optional object which, when called, will perform the correct action
# if the user simply repeats the command.

def operand_stack_handler (machine:Machine, tokens:Sequence[str]) -> None:
    """
    Dumps the contents of the machine's operand stack.
    :param machine: The virtual machine whose stack is to be dumped.
    :param tokens:
    :return:
    """
    if len (tokens) != 0:
        _logger.warning  ('Unexpected arguments')
    return _dump_stack (machine.operand_s)


def execution_stack_handler (machine:Machine, tokens:Sequence[str]) -> None:
    """
    Dumps the contents of the machine's execution stack.
    :param machine: The virtual machine whose stack is to be dumped.
    :param tokens:
    :return:
    """
    if len (tokens) != 0:
        _logger.warning  ('Unexpected arguments')
    return _dump_stack (machine.exec_s)


def dict_stack_handler (machine:Machine, tokens:Sequence[str]) -> None:
    """
    Dumps the contents of the machine's dictionary stack.
    :param machine: The virtual machine whose stack is to be dumped.
    :param tokens:
    :return:
    """
    if len (tokens) != 0:
        _logger.warning  ('Unexpected arguments')
    return _dump_stack (machine.dict_s)

#eof toydb/stacks.py
