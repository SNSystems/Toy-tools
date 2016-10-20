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

from typing import Dict, Iterable, Mapping, Tuple

from . import graph_walk
from . import log
from . import errors
from .ldtypes import SectionLayout
from .eligible_fragments import EligibleFragment
from store.types import Fragment, SectionType

_STAY_AT_HOME_SECTIONS = set ([ SectionType.debug_line ])

_logger = log.get_logger (__name__)

class _LayoutVisitor (graph_walk.FragmentGraphWalker.LinkVisitor):

    def __init__ (self) -> None:
        self.__layout = dict ()  # section name -> SectionLayout
        self.__name_address_map = dict () # fragment name -> address

    def visit (self, name:str, digest:str, fragment:Fragment) -> None:
        for section_name in fragment.section_names ():
            if section_name not in _STAY_AT_HOME_SECTIONS:
                section_layout = self.__layout.setdefault (section_name, SectionLayout ())

                section_layout.append (address=section_layout.dot,
                                       digest=digest,
                                       fragment=fragment,
                                       name=name)

                address = section_layout.dot
                if section_name != fragment.primary:
                    name += '/' + str (section_name)

                self.__name_address_map [name] = address

                _logger.info ('Layout placed "{fragment_name}" (section {section_name}) at {address:02x}'
                              .format (fragment_name=name, section_name=section_name, address=address))

                section_layout.dot += len (fragment.sections [section_name].data)

    def layout (self) -> Dict[str, SectionLayout]:
        return self.__layout
    def name_address_map (self) -> Dict[str, int]:
        return self.__name_address_map


def produce (eligible:Mapping[str, EligibleFragment],
             entry_points:Iterable[str]) -> Tuple[Dict[str, SectionLayout], Dict[str,int]]:
    """
    :param eligible: A dictionary mapping from name to digest, fragment, and store.
    :param entry_points: A list of entry point ("anchor") names for the fragment graph.
    :return:
    """

    visitor = _LayoutVisitor ()
    walker = graph_walk.FragmentGraphWalker (eligible, visitor)
    for ep in entry_points:
        if ep not in eligible:
            raise errors.LinkError ("Entry point '{0}' was not defined".format (ep))
        walker.walk (ep, eligible [ep])
    return visitor.layout (), visitor.name_address_map ()

#eof toyld/layout.py
