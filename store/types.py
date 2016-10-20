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

import enum
import logging
import os
import uuid
from typing import Iterable, List, Mapping, Sequence

import yaml

_logger = logging.getLogger (__name__)


@enum.unique
class SectionType (enum.Enum):
    text = 1
    data = 2
    debug_line = 3


# The YAML tag used for SectionType objects.
_section_type_yaml_tag = '!scn'


def _section_type_representer (dumper, section):
    """Emits a SectionType to YAML."""
    return dumper.represent_scalar (_section_type_yaml_tag, section.name)


def _section_type_constructor (loader, node):
    """Converts a YAML SectionType to a new instance ."""
    return SectionType.__members__ [loader.construct_scalar (node)]


yaml.add_representer (SectionType, _section_type_representer)
yaml.add_constructor (_section_type_yaml_tag, _section_type_constructor)


class XFixup:
    """
    The type representing a fragment's external fixup record.
    """
    YAML_NAME = '!xfixup'

    def __init__ (self, offset: int, name: str) -> None:
        self.offset = offset
        self.name = name

    def __repr__ (self):
        return "{classname}(offset={offset}, name={name})".format (
                classname=self.__class__.__name__,
                offset=self.offset,
                name=self.name)

    @staticmethod
    def yaml_representer (dumper, xfixup):
        """Emits a XFixup record to YAML."""

        return dumper.represent_mapping (XFixup.YAML_NAME, xfixup.__dict__)

    @staticmethod
    def yaml_constructor (loader, node) -> 'XFixup':
        """Converts a YAML XFixup to a new instance of the class."""

        value = loader.construct_mapping (node)
        return XFixup (**value)


yaml.add_representer (XFixup, XFixup.yaml_representer)
yaml.add_constructor (XFixup.YAML_NAME, XFixup.yaml_constructor)


class Fragment:
    YAML_NAME = '!fragment'

    def __init__ (self, sections, primary) -> None:
        self.sections = sections  # A dict mapping section 'name' to fsection instance
        self.primary = primary  # 'name' of the primary section

    def section_names (self) -> List [str]:
        return self.sections.keys ()

    def __repr__ (self):
        return "{classname}(sections={sections}, primary={primary})".format (
                classname=self.__class__.__name__,
                sections=self.sections,
                primary=self.primary)

    @staticmethod
    def yaml_representer (dumper, fragment):
        """Emits a Fragment to YAML."""

        return dumper.represent_mapping (Fragment.YAML_NAME, fragment.__dict__)

    @staticmethod
    def yaml_constructor (loader, node) -> 'Fragment':
        """Converts a YAML Fragment record to a new instance of the class."""

        value = loader.construct_mapping (node, deep=True)
        return Fragment (**value)


yaml.add_representer (Fragment, Fragment.yaml_representer)
yaml.add_constructor (Fragment.YAML_NAME, Fragment.yaml_constructor)


class FSection:
    """
    A Fragment Section record. Each fragment contains an array of zero or more sections.
    """

    YAML_NAME = '!fsection'

    def __init__ (self, data, xfixups=None, ifixups=None) -> None:
        """
        :param data:
        :param xfixups: A list of inter-fragment (external) fixup records (offset, name)
        :param ifixups: A list of intra-fragment (internal) fixup records (offset, section)
        :return:
        """
        self.data = data
        self.xfixups = xfixups if xfixups is not None else list ()
        self.ifixups = ifixups if ifixups is not None else list ()

    def __repr__ (self):
        data = str (self.data)  # TODO: hex encode?
        data = data if len (data) < 20 else data [:20] + '...'
        return "{classname}(data={data}, xfixups={xfixups}, ifixups={ifixups})".format (
                classname=self.__class__.__name__,
                data=data,
                xfixups=self.xfixups,
                ifixups=self.ifixups)

    @staticmethod
    def yaml_representer (dumper, fsection):
        """Emits a FSection to YAML."""

        mapping = {'data': fsection.data}
        if len (fsection.xfixups) > 0:
            mapping ['xfixups'] = fsection.xfixups
        if len (fsection.ifixups) > 0:
            mapping ['ifixups'] = fsection.ifixups
        return dumper.represent_mapping (FSection.YAML_NAME, mapping)

    @staticmethod
    def yaml_constructor (loader, node) -> 'FSection':
        """Converts a YAML FSection to a new instance of the class."""

        value = loader.construct_mapping (node)
        return FSection (**value)


yaml.add_representer (FSection, FSection.yaml_representer)
yaml.add_constructor (FSection.YAML_NAME, FSection.yaml_constructor)


class TicketRecord:  # FIXME: rename TicketMember
    YAML_NAME = '!ticketmember'

    def __init__ (self, name: str, digest: str, line_base: int) -> None:
        self.name = name
        self.digest = digest
        self.line_base = line_base

    @staticmethod
    def yaml_representer (dumper, tr):
        """Emits a TicketRecord to YAML."""

        return dumper.represent_mapping (TicketRecord.YAML_NAME, tr.__dict__)

    @staticmethod
    def yaml_constructor (loader, node) -> 'TicketRecord':
        """Converts a YAML TicketRecord to a new instance of the class."""

        value = loader.construct_mapping (node)
        return TicketRecord (**value)


yaml.add_representer (TicketRecord, TicketRecord.yaml_representer)
yaml.add_constructor (TicketRecord.YAML_NAME, TicketRecord.yaml_constructor)


class TicketFileEntry:
    """This class contains a description of an individual compilation. It records the output file of the ticket file
    produced by the compiler and a list of zero or more name to fragment mappings."""

    YAML_NAME = '!ticket'

    def __init__ (self, path: str, members: Iterable [TicketRecord]) -> None:
        self.path = path
        self.members = members

    @staticmethod
    def yaml_representer (dumper, tf):
        """Emits a ticket file record to YAML."""

        return dumper.represent_mapping (TicketFileEntry.YAML_NAME, tf.__dict__)

    @staticmethod
    def yaml_constructor (loader, node):
        """Converts a YAML ticket file record to a new instance of TicketFileEntry."""

        value = loader.construct_mapping (node)
        return TicketFileEntry (**value)


yaml.add_representer (TicketFileEntry, TicketFileEntry.yaml_representer)
yaml.add_constructor (TicketFileEntry.YAML_NAME, TicketFileEntry.yaml_constructor)


class LinksRecord:
    """This class contains a connection from a program repository to a native binary that was linked from it. Its
    primary purpose is to enable the garbage collector to "keep alive" fragments that are referenced by debug
    information in those files. A specific binary is identified by its path and a UUID which is created at link-time."""

    YAML_NAME = '!link'

    def __init__ (self, file: str, uuid: uuid.UUID) -> None:
        self.file = file
        self.uuid = uuid

    @staticmethod
    def yaml_representer (dumper, lr):
        """Emits a LinksRecord to YAML."""

        return dumper.represent_mapping (LinksRecord.YAML_NAME, lr.__dict__)

    @staticmethod
    def yaml_constructor (loader, node) -> 'LinksRecord':
        """Converts a YAML LinksRecord to a new instance of the class."""

        value = loader.construct_mapping (node)
        return LinksRecord (**value)


yaml.add_representer (LinksRecord, LinksRecord.yaml_representer)
yaml.add_constructor (LinksRecord.YAML_NAME, LinksRecord.yaml_constructor)


class DebugLineRecord:
    YAML_NAME = '!debuglinerecord'

    def __init__ (self, address: int, fragment: str, line_base: int) -> None:
        self.address = address
        self.fragment = fragment  # The referenced fragment's digest.
        self.line_base = line_base

    @staticmethod
    def yaml_representer (dumper, lr):
        """Emits a DebugListRecord to YAML."""

        return dumper.represent_mapping (DebugLineRecord.YAML_NAME, {
            'address': lr.address,
            'fragment': lr.fragment,
            'line_base': lr.line_base,
        })

    @staticmethod
    def yaml_constructor (loader, node) -> 'DebugLineRecord':
        """Converts a YAML DebugLineRecord to a new instance of the class."""

        value = loader.construct_mapping (node)
        return DebugLineRecord (**value)


yaml.add_representer (DebugLineRecord, DebugLineRecord.yaml_representer)
yaml.add_constructor (DebugLineRecord.YAML_NAME, DebugLineRecord.yaml_constructor)


class Repository:
    YAML_NAME = '!repository'

    def __init__ (self,
                  fragments: Mapping [str, Fragment],
                  links: Sequence [LinksRecord],
                  tickets: Mapping [uuid.UUID, TicketFileEntry],
                  uuid: uuid.UUID) -> None:
        self.fragments = fragments
        self.links = links
        self.tickets = tickets
        self.uuid = uuid

    @staticmethod
    def new () -> 'Repository':
        """This method creates a new repository."""

        return Repository (fragments={}, links=[], tickets={}, uuid=uuid.uuid4 ())

    @staticmethod
    def read (path, create=False) -> 'Repository':
        """
        Creates an instance of Repository from the given file path.
        :param path: The file path from which the repository is read.
        :param create: If true, a new repository will be returned if it was not found at the given path.
        :return: A new Repository instance.
        """

        try:
            stream = open (path, 'rt')
        except FileNotFoundError:
            if create:
                _logger.info ("New repository created")
                return Repository.new ()
            else:
                raise
        else:
            with stream:
                try:
                    _logger.debug ("Loading YAML repository '%s'", os.path.abspath (path))
                    r = yaml.load (stream)
                except (ValueError, yaml.YAMLError):
                    raise RuntimeError ("Repository '{0}' was not valid".format (path))
                if not isinstance (r, Repository):
                    raise yaml.YAMLError ("YAML file '{0}' did not contain a repository".format (path))
                return r

    def write (self, path: str) -> None:
        """
        Writes the repository as YAML.
        :param path: The path to which the repository will be written.
        :return: None
        """

        _logger.debug  ("Writing repository '%s'", os.path.abspath (path))
        with open (path, 'wt') as stream:
            dumper = yaml.Dumper
            dumper.ignore_aliases = lambda self, data: True
            yaml.dump (data=self, stream=stream, explicit_start=True, explicit_end=True, Dumper=dumper)

    @staticmethod
    def yaml_representer (dumper, r):
        """Emits a Repository to YAML."""

        return dumper.represent_mapping (Repository.YAML_NAME, r.__dict__)

    @staticmethod
    def yaml_constructor (loader, node) -> 'Repository':
        """Converts a YAML Repository to a new instance of the class."""

        value = loader.construct_mapping (node)
        return Repository (**value)


yaml.add_representer (Repository, Repository.yaml_representer)
yaml.add_constructor (Repository.YAML_NAME, Repository.yaml_constructor)


def _uuid_representer (dumper, u):
    """Emits a UUID to YAML."""
    return dumper.represent_scalar ('!uuid', str (u))


def _uuid_constructor (loader, node):
    """Converts a YAML UUID to a new instance."""
    return uuid.UUID (hex=loader.construct_scalar (node))


yaml.add_representer (uuid.UUID, _uuid_representer)
yaml.add_constructor ('!uuid', _uuid_constructor)

# eof store/types.py
