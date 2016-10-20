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

import logging
from typing import Sequence

from toydb import src_cache
from toyvm import machine
from toyvm.instruction.source_location import SourceLocation

_logger = logging.getLogger (__name__)

def show_location (location:SourceLocation) -> None:
    if location is None:
        _logger.warning ('No source information')
        return

    for ctr in range (max (1, location.line - 5), location.line + 5):
        source = src_cache.get_line (location.srcfile, ctr)
        _logger.info (source)
        if ctr == location.line:
            _logger.info (' ' * (location.column - 1) + '^')


def list_handler (machine:machine.Machine, tokens:Sequence[str]) -> None:
    """
    Handles the 'list' command which takes a single (optional) argument which is the name of the operator to be
    listed or, if '.' or unspecified, the next instruction to be executed is shown.

    :param machine: A machine whose contents are to be inspected.
    :param tokens: A list of command tokens.
    :return: Nothing.
    """

    if len (tokens) == 0:
        tokens = [ '.' ]
    if len (tokens) > 1:
        _logger.warning ('Extra arguments ignored')

    if tokens [0] == '.':
        if machine.exec_s.empty ():
            _logger.error ('Execution stack is empty')
            return
        value = machine.exec_s.peek ()
    else:
        value = machine.find_operator (tokens [0])
        if value is None:
            _logger.error ('Operator "%s" was not found', tokens [0])
            return

    if not hasattr (value, 'locn'):
        _logger.error ('No location for "%s"', tokens [0])
    else:
        show_location (value.locn ())


#eof toydb/list_cmd.py
