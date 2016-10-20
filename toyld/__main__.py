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
The Toy linker's entry point.
"""

# Standard modules
import argparse
import logging
import os
import sys
import uuid
from typing import Iterable

import yaml

import toyld.link
import toyld.log
from store.types import LinksRecord, Repository
from toyld import errors

_logger = toyld.log.get_logger (__name__)

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

def _load_ticket (path: str) -> uuid.UUID:
    _logger.debug ('Loading ticket "%s"', path)
    with open (path, 'rt') as f:
        try:
            ticket = yaml.load (f)
        except (ValueError, yaml.YAMLError):
            raise RuntimeError ("Ticket file '{0}' was not valid".format (path))
        if not isinstance (ticket, uuid.UUID):
            raise RuntimeError ("Ticket file '{0}' was did not contain a valid UUID".format (path))
        return ticket


class Options:
    """
    A class to contain the command-line options.
    """

    def __init__ (self, opt) -> None:
        self.debug = opt.debug
        self.entry_point = opt.entry_point
        self.infile = opt.infile
        self.outfile = opt.outfile
        self.repository = opt.repository
        self.verbose = opt.verbose


def _get_options (program: str, args: Iterable [str]) -> Options:
    parser = argparse.ArgumentParser (prog=program,
                                      description='Link from a program repository.')
    parser.add_argument ('infile', nargs='*',
                         help='The files to be linked.')
    parser.add_argument ('-r', '--repository',
                         default='repo.yaml',
                         help='The program repository to be used for linking.')
    parser.add_argument ('-o', '--output',
                         default='a.out',
                         metavar='F',
                         dest='outfile',
                         help='The file to which output will be written (default=stdout)')
    parser.add_argument ('-E', '--entry-point', nargs='*',
                         default=['main'],
                         help='Entry point.')
    parser.add_argument ('-v', '--verbose', action='count', default=0,
                         help='Produce verbose output (repeat for more output).')
    parser.add_argument ('--debug', action='store_true', help='Emit debugging trace.')
    return Options (parser.parse_args (args))


def main (program='toyld', args=sys.argv [1:]) -> int:
    options = _get_options (program, args)

    try:
        # Set the root logger's level: this allows logging messages to be logged to the default console.
        logging.getLogger ().setLevel ((logging.WARNING, logging.INFO, logging.DEBUG) [min (options.verbose, 2)])

        # Load the input files (the repository and the tickets)
        repository = Repository.read (path=options.repository)
        tickets = [_load_ticket (path) for path in options.infile]

        _logger.debug ('Entry points are: %s', ' '.join (options.entry_point))

        temp_file = options.outfile + '.t'
        f = open (temp_file, 'wt')
        try:
            link_uuid = uuid.uuid4 ()
            with f:
                entry_addresses = toyld.link.link (tickets=tickets,
                                                   repository=repository,
                                                   repository_path=options.repository,
                                                   entry_points=options.entry_point,
                                                   out_file=f,
                                                   uuid=link_uuid)

            # Add this link to the repository and rewrite it.
            repository.links.append (LinksRecord (file=os.path.abspath (options.outfile), uuid=link_uuid))
            repository.write (path=options.repository)
            os.replace (src=temp_file, dst=options.outfile)

            _logger.info ('Entry addresses are: %s', ' '.join (hex (ea) for ea in entry_addresses))
        except errors.LinkError as ex:
            _logger.error (ex)
        finally:
            try:
                os.unlink (temp_file)
            except FileNotFoundError:
                pass
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

# eof link.py
