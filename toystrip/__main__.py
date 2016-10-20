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

# System modules
import argparse
import logging
import sys
import uuid
from typing import Iterable, Sequence

# Local modules
from store.types import Repository

EXIT_FAILURE = 1
EXIT_SUCCESS = 0

_logger = logging.getLogger (__name__)


class Options:
    """
    A class to represent the options that can be set on the utility's command line.
    """

    def __init__ (self, opt) -> None:
        self.verbose = opt.verbose
        self.input = opt.input  # The source repository
        self.output = opt.output  # The destination repository
        self.debug = opt.debug


def command_line (args: Iterable [str], program: str = 'toystrip') -> Options:
    """
    Processes options from the command line.

    :param args: A list of arguments to be parsed.
    :param args: The program name to be used in the option help text.
    :return: An instance of Options containing the user's options.
    """

    parser = argparse.ArgumentParser (prog=program, description='Strip fragment bodies from a Toy program repository.')
    parser.add_argument ('-i', '--input', nargs='?', default='repo.yaml',
                         help='the path of the repository to be stripped')
    parser.add_argument ('-o', '--output', default='repoc.yaml',
                         help='the path to which the stripped repository will be written')
    parser.add_argument ('-v', '--verbose', action='count', default=0,
                         help='produce verbose output (repeat for more output)')
    parser.add_argument ('--debug', action='store_true', help='emit debugging trace')
    return Options (parser.parse_args (args))


def main (args: Sequence [str] = sys.argv [1:]) -> int:
    options = command_line (args)
    try:
        # Set the root logger's level: this allows logging messages to be logged to the default console.
        logging.getLogger ().setLevel ((logging.WARNING, logging.INFO, logging.DEBUG) [min (options.verbose, 2)])

        repository = Repository.read (options.input)

        # Now blast the repository fragment values and clear all of the
        # other fields.
        for digest, _ in repository.fragments.items ():
            _logger.debug ("Fragment {0} cleared".format (digest))
            repository.fragments [digest] = None

        repository.links = []
        repository.tickets = {}
        repository.uuid = uuid.uuid4 ()

        # Write the freshly stripped repository
        repository.write (options.output)
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

# eof toystrip/__main__.py
