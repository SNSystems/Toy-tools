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
This module is represents the compiler's back-end. This is the part that's responsible for the finalizing the
generated code and for writing the final output, in this case to both the program repository and a ticket file.
"""

import logging
import os.path
import uuid
from typing import Mapping
import yaml

from store import types
from .fixups import procedure_fixups
from .types import NameMeta, ProcedureRecord
from .options import Options

_logger = logging.getLogger (__name__)


def back_end (options: Options,
              rebased_program: Mapping [str, ProcedureRecord],
              name_metadata_map: Mapping [str, NameMeta],
              repository: types.Repository) -> None:
    """
    The compiler 'back end'. This part is responsible for emitting the result of this compilation to the
    repository and for creating a new 'ticket' file to represent it.
    """

    # Make a unique identifier for this compilation.
    compile_uuid = uuid.uuid4 ()

    # Create a ticket record for this compilation in the repository.
    # FIXME: TicketRecord should really be called TicketMember

    repository.tickets [compile_uuid] = types.TicketFileEntry (
            path=os.path.abspath (options.out_file),
            members=[types.TicketRecord (name=name, digest=meta.digest, line_base=meta.line_base)
                     for name, meta in name_metadata_map.items ()]
    )

    # Add a fragment record for each of the functions that we included in this TU.
    for name, procedure_record in rebased_program.items ():
        digest = name_metadata_map [name].digest
        _logger.info ("Emitting procedure '%s', digest %s", name, digest)


        fixups = procedure_fixups (rebased_program [name].procedure)
        xfixups = [types.XFixup (offset=-1, name=f) for f in fixups]

        # Write the fragment's section data.
        io_sections = dict ()
        procedure_record.procedure.write (io_sections)

        # Now build the fragment sections themselves. (In a Toy language program only the text
        # section can have external fixups; it's not a property of the repository design.)
        sections = {
            scn: types.FSection (data=io.getvalue (), xfixups=xfixups if scn == types.SectionType.text else None)
            for scn, io in io_sections.items ()
            }
        repository.fragments [digest] = types.Fragment (sections=sections, primary=types.SectionType.text)

    # Write the updated repository
    repository.write (options.repository)

    # Write the object/ticket file.
    _logger.info ("Writing ticket %s to '%s'", compile_uuid, options.out_file)
    with open (options.out_file, 'wt') as ticket_file:
        yaml.dump (data=compile_uuid, stream=ticket_file, explicit_start=True, explicit_end=True)

# eof toycc.backend
