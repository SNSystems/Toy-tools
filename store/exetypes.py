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
import uuid
from typing import Iterable, Mapping, Optional

import yaml

from .types import DebugLineRecord, SectionType

_logger = logging.getLogger (__name__)


class Symbol:
    YAML_NAME = '!symbol'

    def __init__ (self, name: str, address: int, size: int) -> None:
        self.name = name
        self.address = address
        self.size = size

    @staticmethod
    def yaml_representer (dumper, symbol):
        """Emits a Symbol instance to YAML."""

        return dumper.represent_mapping (Symbol.YAML_NAME, symbol.__dict__)

    @staticmethod
    def yaml_constructor (loader, node) -> 'Symbol':
        """Converts a YAML Symbol to a new instance of the class."""

        value = loader.construct_mapping (node)
        return Symbol (**value)


yaml.add_representer (Symbol, Symbol.yaml_representer)
yaml.add_constructor (Symbol.YAML_NAME, Symbol.yaml_constructor)


class RepositoryRecord:
    YAML_NAME = '!repo_record'

    def __init__ (self, path: str, uuid: uuid.UUID):
        self.path = path
        self.uuid = uuid

    @staticmethod
    def yaml_representer (dumper, rr):
        """Emits a RepositoryRecord instance to YAML."""

        return dumper.represent_mapping (RepositoryRecord.YAML_NAME, rr.__dict__)

    @staticmethod
    def yaml_constructor (loader, node) -> 'RepositoryRecord':
        """Converts a YAML RepositoryRecord to a new instance of the class."""

        value = loader.construct_mapping (node)
        return RepositoryRecord (**value)


yaml.add_representer (RepositoryRecord, RepositoryRecord.yaml_representer)
yaml.add_constructor (RepositoryRecord.YAML_NAME, RepositoryRecord.yaml_constructor)


class Executable:
    YAML_NAME = '!executable'

    def __init__ (self, symbols: Iterable [Symbol], uuid: uuid.UUID, repository_record: RepositoryRecord,
                  data: Mapping [SectionType, bytearray], debug=Iterable [DebugLineRecord]) -> None:
        self.symbols = symbols
        self.uuid = uuid
        self.repository_record = repository_record
        self.data = data
        self.debug = debug

    @staticmethod
    def new (repository_record: RepositoryRecord = Optional [RepositoryRecord],
             uuid: uuid.UUID = Optional [uuid.UUID]) -> 'Executable':
        if uuid is None:
            uuid = uuid.UUID ()
        return Executable (symbols=list (), uuid=uuid, repository_record=repository_record, data=dict (), debug=list ())

    def write (self, stream) -> None:
        """
        Writes the executable as YAML.
        :param stream: The stream to which the executable will be written.
        """

        _logger.info ("Writing executable")
        yaml.dump (data=self, stream=stream, explicit_start=True, explicit_end=True)

    @staticmethod
    def yaml_representer (dumper, exe):
        """Emits an Executable instance to YAML."""

        return dumper.represent_mapping (Executable.YAML_NAME, exe.__dict__)

    @staticmethod
    def yaml_constructor (loader, node) -> 'Executable':
        """Converts a YAML Executable to a new instance of the class."""

        return Executable (**loader.construct_mapping (node))


yaml.add_representer (Executable, Executable.yaml_representer)
yaml.add_constructor (Executable.YAML_NAME, Executable.yaml_constructor)

# eof store/exetypes.py
