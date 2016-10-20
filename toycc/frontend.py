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
import logging
import os.path
from typing import Mapping

import pyparsing as pp

# Local imports
import toyvm.instruction as instruction
from .options import Options

_source_file = None
_debug_info_enabled = False

# This function decides whether to return a SourceLocation or None depending on whether debug
# info generation has been enabled by the user.
def _location (orig_string, locn):
    if not _debug_info_enabled:
        return None

    assert _source_file is not None
    return instruction.SourceLocation (srcfile=os.path.abspath (_source_file),
                                       line=pp.lineno (locn, orig_string),
                                       column=pp.col (locn, orig_string))

#@pp.traceParseAction
def _make_true (src, locn, toks):
    return instruction.Boolean (True, locn=_location (src, locn))

#@pp.traceParseAction
def _make_false (src, locn, toks):
    return instruction.Boolean (False, locn=_location (src, locn))

#@pp.traceParseAction
def _make_operator (src, locn, toks):
    assert len (toks) == 1
    return instruction.Operator (toks [0], locn=_location (src, locn))

#@pp.traceParseAction
def _make_string (src, locn, toks):
    assert len (toks) == 1
    string = toks [0]
    # Check for and strip the leading and trailing quote characters
    assert len (string) >= 2 and string [0] == '"' and string [-1] == '"'
    string = string [1:-1]

    return instruction.String (string, locn=_location (src, locn))

#@pp.traceParseAction
def _make_number (src, locn, toks):
    assert len (toks) == 1
    return instruction.Number (float (toks [0]), locn=_location (src, locn))

#@pp.traceParseAction
def _make_procedure (src, locn, toks):
    assert len (toks) == 1
    return instruction.Procedure (toks [0], locn=_location (src, locn))

# Matches a number which may be negative, include a decimal point or exponential notation.
# e.g. 1, -1, 3.14, 314e-2
_number = pp.Regex (r'-?\d+(\.\d*)?([eE]-?\d+)?').setParseAction (_make_number).setName ('number')

_ident = pp.Word (pp.alphas, pp.alphanums + '_')
_comment = pp.Regex (r'#.*').suppress ()

_operator = _ident.copy ().setParseAction (_make_operator).setName ('operator')
_string = pp.quotedString.setParseAction (_make_string).setName ('string')
_open_brace = pp.Keyword ('{').suppress ()
_close_brace = pp.Keyword ('}').suppress ()

_boolean = (pp.Keyword ('true').setParseAction (_make_true).setName ('true') ^
            pp.Keyword ('false').setParseAction (_make_false).setName ('false'))

_procedure = pp.Forward ()
operation = pp.ZeroOrMore (_comment ^ _boolean ^ _number ^ _procedure ^ _string ^ _operator)
_procedure << pp.Group (_open_brace + operation + _close_brace).setName ('procedure').setParseAction (_make_procedure)

_named_procedure = pp.Group (_ident.copy ().setName ('Procedure name')
                             + pp.Optional (_comment)
                             + _procedure).setName ('Named procedure')

_grammar = pp.Dict (pp.ZeroOrMore (_comment ^ _named_procedure))



_logger = logging.getLogger (__name__)

TUType = Mapping[str, instruction.Procedure]

def front_end (options: Options) -> TUType:
    global _source_file
    _source_file = options.source_file

    global _debug_info_enabled
    _debug_info_enabled = options.debug_info

    with open (options.source_file, 'rt') as f:
        source = f.read ()
    _grammar.setDebug (options.debug_parse)
    program = _grammar.parseString (source, parseAll=True)

    for line in program.dump ().splitlines ():
        _logger.debug (line)

    return program.asDict ()

# eof toycc.frontend
