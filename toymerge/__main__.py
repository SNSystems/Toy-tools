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
        self.debug = opt.debug
        self.inputs = opt.inputs # The source repositories
        self.output = opt.output  # The destination repository
        self.verbose = opt.verbose


def command_line (args:Iterable[str], program:str='toymerge') -> Options:
    """
    Processes options from the command line.

    :param args: A list of arguments to be parsed.
    :param args: The program name to be used in the option help text.
    :return: An instance of Options containing the user's options.
    """

    parser = argparse.ArgumentParser (prog=program, description='Merge Toy program repositories.')
    parser.add_argument ('inputs', nargs='*', default=list(),
                         help='The path of the repository to be merges')
    parser.add_argument ('-r', '--repository', default='repo.yaml', dest='output',
                         help='The path of the target repository for the merge')
    parser.add_argument ('-v', '--verbose', action='count', default=0,
                         help='Produce verbose output (repeat for more output)')
    parser.add_argument ('--debug', action='store_true', help='Emit debugging trace.')
    return Options (parser.parse_args (args))



def main (args:Sequence[str] = sys.argv [1:]) -> int:
    options = command_line (args)
    try:
        # Set the root logger's level: this allows logging messages to be logged to the default console.
        logging.getLogger ().setLevel ((logging.WARNING, logging.INFO, logging.DEBUG) [min (options.verbose, 2)])

        repository = Repository.read (options.output, create=True)
        _logger.debug ("Merging to repository '{output}'".format (output=options.output))
        for input in options.inputs:
            inrepo = Repository.read (input)
            _logger.info ("Merging from '{input}'".format (input=input))

            # Copy in any newly created fragments.
            for digest, fragment in inrepo.fragments.items ():
                if fragment is None:
                    #_logger.debug ("Skipping digest-only fragment {digest}".format (digest=digest))
                    pass
                else:
                    if digest in repository.fragments:
                        # Ignore duplicate fragments to account for more than one agent builing the same file.
                        _logger.debug ("Duplicate fragment {digest} found in '{input}'".format (digest=digest, input=input))
                    else:
                        _logger.debug ("Fragment {digest} merged".format (digest=digest))
                        repository.fragments [digest] = fragment

            # Copy in any newly created ticket records.
            for key, file_entry in inrepo.tickets.items ():
                if key in repository.tickets:
                    _logger.warning ("Duplicate ticket {ticket} found in '{input}'".format (ticket=key, input=input))
                else:
                    _logger.debug ("Ticket {ticket} merged".format (ticket=key))
                    repository.tickets [key] = file_entry

            # TODO: Not expecting any new links. Merge them anyway?

        # Write the merged respository
        _logger.info ("Writing output repository '{output}'".format (output=options.output))
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

#eof toymerge/__main__.py
