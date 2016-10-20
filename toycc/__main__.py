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
import hashlib
import logging
import sys
from typing import Mapping

# Local modules
from store.types import Repository
from toycc import backend, frontend, optimizer, options, rebase
from toycc.types import NameMeta, ProcedureRecord
from toyvm import instruction

_logger = logging.getLogger (__name__)

EXIT_SUCCESS = 0
EXIT_FAILURE = 1


def _get_digest (procedure: instruction.Instruction) -> str:
    h = hashlib.md5 ()
    procedure.digest (h)
    return h.hexdigest ()


def _prune_ir (program: Mapping [str, ProcedureRecord],
               name_metadata_map: Mapping [str, NameMeta],
               repository: Repository) -> Mapping [str, ProcedureRecord]:
    """
    Remove any procedures from the program which already have an equivalent definition in the repository.

    :param program: IR for the TU. A dictionary mapping name to code.
    :param name_metadata_map:
    :param repository: The host program repository.
    :return: The program dictionary with known code -> binary equivalents in the repository.
    """

    new_program = dict ()
    for name, procedure_record in program.items ():
        if not name_metadata_map [name].digest in repository.fragments:
            new_program [name] = procedure_record
        else:
            _logger.info ("Removing '%s' from the IR (its definition is already in the repository)", name)
    return new_program


def main (args=sys.argv [1:]) -> int:
    opt = options.parse_command_line (args)
    try:
        # Set the root logger's level: this allows logging messages to be logged to the default console.
        logging.getLogger ().setLevel ((logging.WARNING, logging.INFO, logging.DEBUG) [min (opt.verbose, 2)])

        orig_program = frontend.front_end (opt)

        # We now need to adjust the source-line correspondence so that each function's line numbers are
        # relative to its first line. This enables the user to move the function around without the compiler
        # then needing to recompile it because its line numbers have changed. Changes _within_ the body of
        # the function will trigger a re-compile.

        rebased_program = {
            name: rebase.rebase_source_info (procedure)
            for name, procedure in orig_program.items ()
            }

        # Compute a digest for each of the functions in the AST using a cryptographic hash function. We'll look
        # these up in the repository to discover which functions we've already produced and stored the definitions.

        digests = {
            name: NameMeta (digest=_get_digest (procedure_record.procedure), line_base=procedure_record.line_base)
            for name, procedure_record in rebased_program.items ()
            }

        repository = Repository.read (opt.repository, create=True)

        # Now remove functions that are already present in the repository. There's no need for them to go
        # through the compiler's later stages.

        rebased_program = _prune_ir (rebased_program, digests, repository)

        optimizer.optimize (rebased_program)

        backend.back_end (opt,
                          rebased_program,
                          name_metadata_map=digests,
                          repository=repository)
    except Exception as ex:
        if opt.debug:
            raise
        else:
            _logger.error (ex)
        return EXIT_FAILURE
    return EXIT_SUCCESS


if __name__ == '__main__':
    logging.basicConfig (level=logging.DEBUG, format='  %(levelname)s: %(message)s')
    sys.exit (main ())

# eof toycc.__main__
