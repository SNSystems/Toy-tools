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

# Standard modules
import argparse
import logging
import sys
from typing import Iterable

# Local modules
from store.types import Repository
from toygc.collector import collect

_logger = logging.getLogger (__name__)

def _get_options (program: str, args: Iterable [str]):
    parser = argparse.ArgumentParser (prog=program, description='Program repository garbage collector')
    parser.add_argument ('-r', '--repository', default='repo.yaml',
                         help='The repository to be rewritten')
    parser.add_argument ('-v', '--verbose', action='count', default=0,
                         help='Produce verbose output (repeat for more output).')
    parser.add_argument ('--debug', action='store_true', help='Emit debugging trace.')
    return parser.parse_args (args)


def main (program: str = 'toygc', args: Iterable [str] = sys.argv [1:]) -> int:
    options = _get_options (program, args)
    try:
        # Set the root logger's level: this allows logging messages to be logged to the default console.
        logging.getLogger ().setLevel ((logging.WARNING, logging.INFO, logging.DEBUG) [min (options.verbose, 2)])

        _logger.info ("Performing GC on '%s'", options.repository)
        src_repo = Repository.read (options.repository)
        dest_repo = Repository.new ()
        collect (src_repo, dest_repo)
        dest_repo.write (options.repository)
    except Exception as ex:
        if options.debug:
            raise
        else:
            _logger.error (ex)
        return 1
    return 0


if __name__ == '__main__':
    logging.basicConfig (level=logging.DEBUG, format='  %(levelname)s: %(message)s')
    sys.exit (main ())

# eof toygc/__main__.py
