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

import uuid
from typing import Any, Mapping, TextIO

import yaml

from store.exetypes import Executable, RepositoryRecord, Symbol
from store import types
from toyld.ldtypes import FragmentAddress
from . import log

_output_logger = log.get_logger ('output')


def apply (data, offset: int, value: int):
    """
    :param data:
    :param offset:
    :param value:
    :return:
    """

    if offset >= 0:
        initial_data_len = len (data)
        value_str = '{0:02x}'.format (value)  # As a 2 character hex string
        assert len (value_str) == 2
        data = data [:offset] + value_str + data [offset + 2:]
        assert len (data) == initial_data_len
    return data


def _apply_fixups (fsection, fragment_name, name_fragment_map, name_address_map, bases):
    """

    :param fsection: A fragment-section instance whose fixups, both internal and external, are to be applied.
    :param fragment_name: The name of the fragment whose fixups are to be applied.
    :param name_fragment_map:
    :param name_address_map:
    :param bases:
    :return:
    """

    assert isinstance (fsection, types.FSection)

    data = fsection.data

    # Apply the _external_ fixups to this fragment. The names are those of other fragments;
    # we link to the primary section of the fragment.
    for fixup in fsection.xfixups:
        name = fixup.name
        fragment = name_fragment_map [name].fragment

        # Reverse fixups
        name_fragment_map [name].puxifs.append ([fragment_name, fixup.offset])

        address = name_address_map [name] + bases [fragment.primary]
        _output_logger.debug ('fixup "%s" -> 0x%02x', name, address)
        data = apply (data, fixup.offset, address)

    # Apply the internal fixups. The reference is always to the source fragment,
    # and the name refers to the section.
    for offset, section in fsection.ifixups:
        name = fragment_name + '/' + section
        address = name_address_map [name] + bases [section]
        _output_logger.debug ('internal fixup %s -> 0x%02x', name, address)

        data = apply (data, offset, address)

    return data




def output (out_file: TextIO,
            name_fragment_map,
            repository_record: RepositoryRecord,
            layout,
            name_address_map: Mapping [str, int],
            bases: Mapping [types.SectionType, int],
            uuid: uuid.UUID) -> None:

    executable = Executable.new (repository_record=repository_record, uuid=uuid)

    for section in sorted (layout.keys ()):
        _output_logger.info ('Writing section %s', str (section))

        for fa in layout [section].fragment_addresses:
            assert isinstance (fa, FragmentAddress)
            address = fa.address
            digest = fa.digest
            fragment = fa.fragment
            name = fa.name

            data = _apply_fixups (fsection=fragment.sections [section],
                                  fragment_name=name,
                                  name_fragment_map=name_fragment_map,
                                  name_address_map=name_address_map,
                                  bases=bases)

            address += bases [section]
            _output_logger.debug ('Writing "%s"/%s at 0x%02x', name, section, address)

            section_data = executable.data.setdefault (section, bytearray ())
            section_data += data

            line_base = name_fragment_map [name].line_base
            if line_base is not None:
                debug_line_record = types.DebugLineRecord (address=address,
                                                           fragment=digest,
                                                           line_base=line_base)
                executable.debug.append (debug_line_record)

            fa.symbol = len (executable.symbols)
            executable.symbols.append (Symbol (name=name, address=address, size=len (data)))

        if executable.data.get (section):
            executable.data [section] = bytes (executable.data [section])

    executable.write (stream=out_file)

# eof linker/output.py
