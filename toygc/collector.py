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
The core of the garbage collector. The Collector class discovers all of the live "roots" (i.e. the extant object files
and executables) for the garbage collection trace. Then follows each of the referenced objects to produce the final
new repository. Any repositories referenced from a rooted link are also collected.
"""

import logging
import uuid
from typing import Mapping, Optional
import yaml

from store.types import Repository

_logger = logging.getLogger (__name__)


class Collector:
    """
    A program repository garbage collector.
    """

    def __init__ (self, source: Repository, dest: Repository) -> None:
        self.__source = source
        self.__dest = dest

    def collect (self) -> None:
        """
        The core of the collection process. The files given to the constructor, and any repositories that
        they reference, are garbage collected by this function.
        """

        # The collected repository must have the same UUID as the original.
        self.__dest.uuid = self.__source.uuid

        self.__preserve_stripped_fragments ()
        self.__preserve_extant_tickets ()
        self.__preserve_extant_links ()

    def __preserve_extant_tickets (self) -> None:
        _logger.info ("Collecting extant ticket files")

        for ticket, entry in self.__source.tickets.items ():
            ticket_id = Collector.__load_ticket (entry.path)
            # If the ticket's id matches the record in the repository, we keep its contents.
            if ticket_id != ticket:
                _logger.info ("Removing ticket '%s'", entry.path)
            else:
                _logger.debug ("Copying ticket '%s'", entry.path)

                # Copy the fragments to which this ticket refers
                for m in entry.members:
                    digest = m.digest
                    if not digest in self.__dest.fragments:
                        _logger.debug ("Copying fragment %s", digest)
                        self.__dest.fragments [digest] = self.__source.fragments [digest]

                # Copy the ticket itself.
                self.__dest.tickets [ticket] = entry

    def __preserve_stripped_fragments (self) -> None:
        """
        Once a repository has been stripped, the contents of its fragments are stripped and the corresponding
        ticket records removed. To stop the garbage collector from accidentally eliminating these stripped
        fragments, I perform an explicit pass to copy them.
        """

        _logger.info ("Collecting stripped fragments")
        for digest, fragment in self.__source.fragments.items ():
            if fragment is None:
                _logger.debug ("Copying stripped fragment %s", digest)
                self.__dest.fragments [digest] = None

    def __preserve_extant_links (self) -> None:
        _logger.info ("Collecting extant links")
        for link in self.__source.links:
            exe = Collector.__load_executable (link.file)

            # The executable's uuid must match the link UID in the repository for the
            # repo contents to be valid for that file.
            if exe is None or exe.uuid != link.uuid:
                _logger.info ("Removing traces of executable '%s'", link.file)
            else:
                # Collect fragments to which this executable's debug records refer. I need to keep the reference
                # fragments so that it's still possible to debug an executable after its object files have gone.
                _logger.debug ("Copying executable '%s'", link.file)

                # Preserve the link record itself.
                self.__dest.links.append (link)

                for d in exe.debug:
                    fragment = self.__source.fragments [d.fragment]
                    if fragment is not None:
                        digest = d.fragment
                        if not digest in self.__dest.fragments:
                            _logger.debug ("Copying fragment %s", digest)
                            self.__dest.fragments [digest] = fragment

    # FIXME: share with the VM/Debugger?
    @staticmethod
    def __load_executable (path: str) -> Optional [Mapping]:
        _logger.info ('Loading executable "%s"', path)
        try:
            with open (path, 'rt') as f:
                return yaml.load (stream=f)
        except (FileNotFoundError, yaml.YAMLError):
            return None

    # FIXME: this should be shared with the linker.
    @staticmethod
    def __load_ticket (path: str) -> Optional [uuid.UUID]:
        _logger.info ('Loading ticket "%s"', path)
        try:
            with open (path, 'rt') as f:
                return yaml.load (f)  # TODO: check it's a UUID
        except (FileNotFoundError, ValueError, yaml.YAMLError):
            return None


def collect (src_repo: Repository, dest_repo: Repository) -> None:
    """
    Performs garbage collection on the repository 'src_repo' writing the collected content to 'dest_repo'.

    :param src_repo:
    :param dest_repo:
    """

    Collector (src_repo, dest_repo).collect ()

# eof toygc/collector.py
