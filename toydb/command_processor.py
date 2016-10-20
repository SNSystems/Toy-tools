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

# Standard modules
import logging
import shlex
from typing import Mapping

# Local modules
from toydb import commands
from toyvm.machine import Machine
from .commands import CommandCallback

_logger = logging.getLogger (__name__)



class CommandProcessor:
    """
    A class which consumes a single string, decodes it and dispatches to the relevant command handler callable.
    """

    def __init__ (self, machine: Machine, commands: Mapping[str, CommandCallback]) -> None:
        self.__prev_tokens = list ()
        self.__machine = machine
        self.__commands = commands

    def command (self, s: str) -> None:
        """
        Dispatches the command string 's' to the relevant handler as defined by the 'commands' constructor argument.
        """

        try:
            # Split the string into a series of tokens. This deals with any quoting.
            tokens = shlex.split (s)
        except Exception as ex:
            _logger.error ('Error: %s', str (ex))
        else:
            # If an empty command was supplied, we repeat the previous.
            if len (tokens) == 0:
                tokens = self.__prev_tokens
            if len (tokens) > 0:
                try:
                    # Find a handler for this command.
                    command = commands.from_string (tokens [0], self.__commands)
                except commands.CommandError as ex:
                    _logger.error ('Error: %s', str (ex))
                else:
                    assert len (command) == 1
                    # Remember this command so a blank line can repeat it.
                    self.__prev_tokens = tokens

                    # Extract the sole value from this dictionary.
                    handler = next (iter (command.values ()))
                    handler (self.__machine, tokens [1:])

#eof toydb/command_processor.py
