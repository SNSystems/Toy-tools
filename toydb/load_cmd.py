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
import io
import logging
import uuid
from typing import List, Mapping, Optional, Sequence
import yaml

# Local modules
from store.exetypes import Executable
from store.types import DebugLineRecord, Fragment, Repository, SectionType
from toyvm import dyld
from toyvm.instruction import Instruction, SourceLocation
from toyvm.machine import Machine

_logger = logging.getLogger (__name__)


def _load_repo_yaml (path: str, uuid: uuid.UUID) -> Repository:
    repo = Repository.read (path)
    if repo.uuid != uuid:
        raise RuntimeError ("Repository UUID does not match (expected {0} got {1})".format (uuid, repo.uuid))
    return repo


def find_fragment (repository: Repository, fragment_digest: str) -> Optional [Fragment]:
    """
    Locates a specific fragment in a repository.

    :param repositories: An instance of types.Repository.
    :param fragment_digest: The fragment digest to be located.
    :return: The fragment which corresponds to the given digest.
    """
    return repository.fragments.get (fragment_digest)


def load_debug_info (executable:Executable, in_memory_program: Mapping [str, Instruction]) -> None:
    """
    Loads the source correspondence for a loaded program (in_memory_program) from the information provided in
    the executable file from which that program was loaded, or more particularly, the program repositories
    which are referenced by the executable.

    :param executable:
    :param in_memory_program:
    :return: Nothing
    """

    if executable.repository_record.path is None:
        _logger.info ('Executable was not associated with a program repository')
        return

    repository = Repository.read (executable.repository_record.path)

    address_to_symbol_map = {
        symbol.address: symbol
        for symbol in executable.symbols
        }

    for debug_record in executable.debug:
        assert isinstance (debug_record, DebugLineRecord)

        symbol = address_to_symbol_map [debug_record.address]
        fragment = find_fragment (repository, debug_record.fragment)
        if fragment is None:
            _logger.warning ("Could not load fragment for %s", symbol.name)
        else:
            debug_line = fragment.sections.get (SectionType.debug_line, dict ())

            _logger.debug ('Loading source correspondence for %s', symbol.name)
            in_memory_program [symbol.name].read_debug (binary=io.BytesIO (debug_line.data),
                                                        line_base=debug_record.line_base)


def load_handler (machine: Machine, tokens: Sequence [str]) -> None:
    if len (tokens) != 1:
        _logger.warning ('Unexpected arguments')

    executable_name = tokens [0]
    try:
        f = open (executable_name, 'rt')
    except FileNotFoundError:
        _logger.error ('Executable "%s" was not found', executable_name)
    else:
        with f:
            content = yaml.load (f)

        program = dyld.load (content)

        # Now load the source correspondence information from the program repository and use it to annotate
        # our newly loaded instructions.
        load_debug_info (content, program)

        # Prepare the program for execution by pushing its names onto the dictionary stack and scheduling 'main'
        # for execution.
        machine.reset ()
        machine.dict_s.push (program)
        machine.execute_operator ('main')
        _logger.info ('Executable "%s" is ready.', executable_name)

# eof toydb/load_cmd.py
