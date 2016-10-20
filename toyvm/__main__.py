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

import argparse
import logging
from typing import Iterable
import yaml
import sys

from toyvm import dyld
from toyvm import errors
from toyvm import machine

_logger = logging.getLogger (__name__)

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

def _options (args:Iterable [str]):
    parser = argparse.ArgumentParser (description='Toy Virtual Machine.')
    parser.add_argument ('executable', type=argparse.FileType ('rt'), help='The executable file to be run.')
    parser.add_argument ('--debug', action='store_true', help='Emit debug messages.')
    parser.add_argument ('--trace', action='store_true', help='Enable VM instruction tracing.')
    parser.add_argument ('-v', '--verbose', action='count', default=0,
                         help='Produce verbose output (repeat for more output).')
    options = parser.parse_args (args)
    return options


def main (args = sys.argv [1:]) -> int:
    options = _options (args)
    try:
        # Set the root logger's level: this allows logging messages to be logged to the default console.
        logging.getLogger ().setLevel ((logging.WARNING, logging.INFO, logging.DEBUG) [min (options.verbose, 2)])

        contents = yaml.load (options.executable)
        program = dyld.load (contents)

        m = machine.Machine ()
        m.trace (options.trace)
        m.run (program)
    except errors.VMError as ex:
        _logger.error (ex)
        return EXIT_FAILURE
    except Exception as ex:
        if options.debug:
            raise
        else:
            _logger.error (ex)
        return EXIT_FAILURE
    return EXIT_SUCCESS

if __name__ == '__main__':
    logging.basicConfig (level=logging.DEBUG, format='  %(levelname)s: %(message)s')
    sys.exit (main ())


#eof toyvm.__main__
