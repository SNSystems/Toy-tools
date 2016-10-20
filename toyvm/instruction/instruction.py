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
Provides the base class for the Toy virtual machine's instruction set.
"""
import abc
import binascii
import io
import logging
import struct
from typing import Any, BinaryIO, Iterable, Dict, Optional

from store.types import SectionType
from .source_location import SourceLocation


_logger = logging.getLogger (__name__)

class Instruction (metaclass=abc.ABCMeta):
    """
    The base class from which all machine instructions are derived. It provides the basic serialization and
    execution interfaces.
    """

    _represent_map = dict ()
    _construct_map = dict ()

    __struct = struct.Struct ('>HI')

    # Each debug line record (an instance of SourceLocation) is prefixed with an int that holds the class-id
    # of the instruction to which it belongs. This allows the correct pairing to be crudely checked.
    __debug_struct = struct.Struct ('>I')

    # Magic value placed at the start of every instruction to ensure that the encode and decode always pair
    # up exactly.
    __MAGIC = 0xc0de

    def __init__ (self, locn: Optional [SourceLocation]) -> None:
        """
        :param locn: The source location for this instruction if known or None if not.
        """
        self.__locn = locn

    @classmethod
    def add_class (cls) -> None:
        crc = binascii.crc32 (cls.__name__.encode ())
        assert (cls not in Instruction._represent_map and crc not in Instruction._construct_map)
        Instruction._represent_map [cls] = crc
        Instruction._construct_map [crc] = cls

    def instructions (self) -> Iterable ['Instruction']:
        return list ()

    def name (self) -> Optional [str]:
        return None

    def locn (self) -> Optional [SourceLocation]:
        """
        Returns the source correspondence for this instruction or None if no debug information is available.
        """
        return self.__locn

    def _locn_str (self) -> str:
        return str (self.__locn) if self.__locn is not None else ''

    @abc.abstractmethod
    def execute (self, machine: 'Machine') -> None:
        """
        Executes the instruction. Many instruction types simple respond by pushing their value onto the operand
        stack; others will cause some sort of change in the state of the machine.

        :param machine: The machine on which the instruction is to be executed.
        :return: None
        """
        raise NotImplementedError ('Instruction.execute')

    def digest (self, hasher) -> None:
        hasher.update (self.__class__.__name__.encode ('utf8'))
        self._digest_impl (hasher)

        locn = self.locn ()
        if locn is None:
            hasher.update ('n'.encode ())
        else:
            hasher.update ('d'.encode ())
            locn.digest (hasher)

    @abc.abstractmethod
    def _digest_impl (self, hasher) -> None:
        """
        Adds the body of the instruction to the secure hash given by 'hasher'. Subclasses must implement this
        method to incorporate the value of their instance variables in the hash.

        :param hasher: A secure hasher object implementing the hashlib interface.
        :return: None
        """
        raise NotImplementedError ('Instruction._digest_impl')

    def write (self, sections: Dict [SectionType, BinaryIO]) -> None:
        # Write the instruction code to the text section
        text_section = sections.setdefault (SectionType.text, io.BytesIO ())
        text_offset = text_section.tell ()

        # Write a magic number followed by the class-id that will enable us to de-serialize it later.
        text_section.write (Instruction.__struct.pack (Instruction.__MAGIC, Instruction._represent_map [self.__class__]))
        self._write (sections)

        debug_line = sections.setdefault (SectionType.debug_line, io.BytesIO ())
        debug_line.write (Instruction.__debug_struct.pack (Instruction._represent_map [self.__class__]))

        self._write_debug (sections, text_offset)

    def set_location (self, locn: SourceLocation) -> None:
        self.__locn = locn

    @staticmethod
    def read (sections: Dict [SectionType, BinaryIO]) -> 'Instruction':
        """
        Reads an instruction from a fragment's text section. Note that this does _not_ read the source correspondence
        for that instruction.

        :param sections:
        :return: The instruction that was read.
        """
        b = sections [SectionType.text].read (Instruction.__struct.size)
        magic, cls_id = Instruction.__struct.unpack (b)
        if magic != Instruction.__MAGIC:
            raise RuntimeError ('Instruction magic number was invalid')

        cls = Instruction._construct_map [cls_id]
        obj = cls.__new__ (cls)
        assert isinstance (obj, Instruction)
        obj.__locn = None  # SourceLocation.construct (sections)
        obj._read (sections)
        return obj

    @abc.abstractmethod
    def _read (self, sections: Dict [SectionType, BinaryIO]) -> None:
        raise NotImplementedError ('Instruction._read')

    def read_debug (self, binary:BinaryIO, line_base:int) -> None:
        """
        Reads the source correspondence for this instruction from the supplied binary stream.

        :param binary: The binary stream from which the source correspondence should be read.
        :param line_base: The containing fragment's debug line offset.
        :return: None
        """

        (instruction_cls_id,) = Instruction.__debug_struct.unpack (binary.read (Instruction.__debug_struct.size))

        # Check that this debug line record appears to match the instruction to which it is about to be attached.
        assert instruction_cls_id == Instruction._represent_map [self.__class__]

        locn = SourceLocation.construct (binary)

        # The fragment's line numbers are stored with 0 as the first line number of
        # the function so that external changes don't require the fragment to be rebuilt.
        # Here we correct that and add the real offset to yield the true line number.
        locn.line += line_base

        # Attach the location to this instruction.
        self.set_location (locn)

    @abc.abstractmethod
    def _write (self, sections: Dict [SectionType, BinaryIO]) -> None:
        raise NotImplementedError ('Instruction._write')

    def _write_debug (self, sections: Dict [SectionType, BinaryIO], text_offset: int) -> None:
        """
        Writes a source-correspondence debug record for this instruction if we have source
        information available.

        :param sections: The sections that make up the fragment. Write to members of this dictionary to add content.
        :param text_offset: The byte offset of the corresponding instruction in the text section.
        """

        locn = self.locn ()
        if locn is not None:
            _logger.debug ("write locn: %s %s", str (self), str (self.locn ()))
            binary = sections.setdefault (SectionType.debug_line, io.BytesIO ())
            locn.write (binary, text_offset)

    def __eq__ (self, other: Any) -> bool:
        return isinstance (other, Instruction) and self.locn () == other.locn ()

    def __ne__ (self, other: Any) -> bool:
        return not self.__eq__ (other)

# eof toyvm/instruction/instruction.py
