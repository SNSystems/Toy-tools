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
This module is responsible for generating the set of fragments which are eligible for inclusion in the link.
These are gathered from the collection of stores that are passed to the linker.
"""

import uuid
from typing import Dict, Iterable

from store.types import Fragment, Repository
from . import errors


class EligibleFragment:
    """
    Contains all the information about an individual fragment to be included in the link.
    """

    def __init__ (self, digest: str, fragment: Fragment, line_base: int) -> None:
        self.digest = digest
        self.fragment = fragment
        self.line_base = line_base
        self.puxifs = list ()  # TOD: this is for incremental linking


def collect (tickets: Iterable [uuid.UUID], repository: Repository) -> Dict [str, EligibleFragment]:
    """
    :param tickets: A list of ticket UIDs which define the compilations whose
                    resulting fragments may be included in the link.
    :param repository: The program repository used for this link.

    :return: A collection of EligibleFragment instances that are eligible for inclusion in the
             linked output.
    """

    eligible = dict ()
    for ticket in tickets:
        ticket_file_entry = repository.tickets.get (ticket)
        if not ticket_file_entry:
            raise errors.LinkError ("ticket '{ticket}' was not found in the repository".format (ticket=str (ticket)))
        else:
            # Now scan the name/digest pairs that the store associates with this ticket UUID
            # and record the final name/fragment relationship.
            for member in ticket_file_entry.members:
                fragment = repository.fragments.get (member.digest)
                if fragment is None:
                    raise errors.LinkError ("Fragment '{0}' was not found".format (member.digest))

                if member.name in eligible:
                    raise errors.LinkError ("Multiple definitions of '{0}'".format (member.name))

                eligible [member.name] = EligibleFragment (digest=member.digest,
                                                           fragment=fragment,
                                                           line_base=member.line_base)
    return eligible

# eof toyld.eligible_fragments.py
