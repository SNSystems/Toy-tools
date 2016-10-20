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

import os
from typing import BinaryIO, Dict, Iterable, List, Mapping
from uuid import UUID

from store import exetypes, types
from . import eligible_fragments, layout, log, output
from .ldtypes import SectionLayout

_logger = log.get_logger (__name__)


def _section_bases (layout: Mapping [str, SectionLayout]) -> Dict [str, int]:
    bases = dict ()
    dot = 0
    for section in sorted (layout.keys ()):
        bases [section] = dot
        dot += layout [section].dot
    return bases


def link (tickets: Iterable [UUID],
          repository: types.Repository,
          repository_path: str,
          entry_points: Iterable [str],
          out_file: BinaryIO,
          uuid: UUID) -> List [int]:
    # 'eligible' is a mapping from name to fragment and digest.
    name_fragment_map = eligible_fragments.collect (tickets, repository)

    ly, name_address_map = layout.produce (name_fragment_map, entry_points)
    bases = _section_bases (ly)
    _logger.info ('Section bases are: {0}'
        .format (' '.join (
            str (key) + ':' + str (value)
            for key, value in bases.items ())))

    repository_record = exetypes.RepositoryRecord (path=os.path.abspath (repository_path), uuid=repository.uuid)

    output.output (out_file,
                   name_fragment_map,
                   repository_record,
                   layout=ly,
                   name_address_map=name_address_map,
                   bases=bases,
                   uuid=uuid)

    addrs = list ()
    for ep in entry_points:
        target_primary_section = name_fragment_map [ep].fragment.primary
        addrs.append (name_address_map [ep] + bases [target_primary_section])
    return addrs

# eof toyld.link
