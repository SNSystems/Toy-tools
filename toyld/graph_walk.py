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

import abc
from typing import Mapping

from store.types import Fragment
from .eligible_fragments import EligibleFragment
from . import log

_logger = log.get_logger (__name__)

class FragmentGraphWalker:

    class LinkVisitor (metaclass=abc.ABCMeta):
        @abc.abstractmethod
        def visit (self, name:str, digest:str, fragment:Fragment) -> None:
            pass

    def __init__ (self, graph_dict:Mapping[str, EligibleFragment], visitor:'FragmentGraphWalker.LinkVisitor') -> None:
        """
        :param graph_dict: A dictionary mapping from name (string) to Fragment.
        :param visitor: A subclass of LinkVisitor whose visit() method will be called once for each vertex of
            the graph that is visited during traversal.
        """

        assert isinstance (visitor, FragmentGraphWalker.LinkVisitor)
        self.__graph_dict = graph_dict
        self.__visited = set ()
        self.__visitor = visitor

    def walk  (self, name:str, digest_fragment:EligibleFragment) -> None:
        """
        Performs a simple recursive depth-first walk of the fragment graph.

        :param name: The name of the graph vertex being visited.
        :param digest_fragment: The digest and body of a fragment.
        :return: Nothing.
        """

        if not name in self.__visited:
            self.__visited.add (name)

            fragment = digest_fragment.fragment
            for section in fragment.section_names ():
                section = fragment.sections [section]
                for fixup in section.xfixups:
                    self.walk (name=fixup.name, digest_fragment=self.__graph_dict [fixup.name])

            _logger.info ('Visiting "%s"', name)
            self.__visitor.visit (name=name, digest=digest_fragment.digest, fragment=fragment)

#eof linker/graph_walk.py
