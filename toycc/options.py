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
Compiler command line options.
"""

import argparse
import os.path
from typing import Iterable

class Options:
    """
    Represents the user options for the compiler.
    """
    def __init__ (self, opt) -> None:
        self.source_file = opt.source_file
        self.out_file = opt.out_file if opt.out_file is not None else os.path.splitext (opt.source_file) [0] + '.o'
        self.repository = opt.repository
        self.debug_info = opt.debug_info
        self.debug = opt.debug
        self.debug_parse = opt.debug_parse
        self.verbose = opt.verbose


def parse_command_line (args:Iterable[str]) -> Options:
    """
    Turns a list of command line arguments into an instance of Options.
    """

    parser = argparse.ArgumentParser (description='Link from a program repository.')
    parser.add_argument ('source_file', help='The source file to be compiled.')
    parser.add_argument ('-o', '--output', default=None, metavar='F', dest='out_file', help='The file to which output will be written.')
    parser.add_argument ('-r', '--repository', default='repo.yaml', help='The program repository to be used for compilation.')
    parser.add_argument ('-g', action='store_true', dest='debug_info', help='Enable generation of debugging information.')
    parser.add_argument ('--debug', action='store_true', help='Enable debug output.')
    parser.add_argument ('--debug-parse', action='store_true', help='Enable parse debugging.')
    parser.add_argument ('-v', '--verbose', action='count', default=0,
                         help='Produce verbose output (repeat for more output).')
    options = parser.parse_args (args)
    return Options (options)

#eof toycc/options.py
