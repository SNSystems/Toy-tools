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

from typing import Iterable, Mapping, Sequence, Dict, Callable

from toyvm.machine import Machine

CommandCallback = Callable[[Machine, Sequence [str]], None]

def get_candidates (input_str:str, command_dict:Mapping [str, CommandCallback]) -> Dict [str, CommandCallback]:
    """
    Given an input string and a dictionary mapping command-names to their implementation returns a copy
    of the command dictionary containing the list of matching candidate commands (which may, of course, be empty).

    :param input_str: The string containing the command-name to be matched or None. If value is an empty string or
                      None, then an empty dictionary will be returned.
    :param command_dict:  A dictionary mapping command-names to implementation.
    :return: A dictionary containing those entries from command_dict whose initial characters match the characters in
             input_str. If input_str is empty or None, then an empty dictionary.
    """
    result = {}

    if input_str:
        matching = [c for c in command_dict.keys() if c.startswith(input_str)]
        result = {name: command_dict[name] for name in matching}

    return result


class CommandError (RuntimeError):
    """
    The base class for the exception types raised by from_string.
    """
    pass


class UnknownCommandError (CommandError):
    """
    An exception which is thrown if an unknown command is found.
    """
    def __init__ (self, command:str) -> None:
        super ().__init__ ('Unknown command "{0}"'.format (command))
        self.command = command


class MultipleCommandError (CommandError):
    """
    An exception class which is thrown if multiple potential commands are found from a given input.
    """
    def __init__ (self, command:str, candidates:Iterable[str]) -> None:
        s = '  \n'.join (sorted (candidates))
        super ().__init__ ('Unknown command "{0}". Did you mean one of:\n{1}\n'.format (command, s))
        self.command = command
        self.candidates = candidates


def from_string (input_str:str, commands:Mapping [str, CommandCallback]) -> Dict [str, CommandCallback]:
    """
    Scans a string for matching commands in the commands table. If a single match is found,
    its key/name pair is  returned.

    :param input_str: The input string to be matched against the command table.
    :param commands: The command table. A dictionary mapping from command string to handler function.
    :return: Returns a dictionary with a single entry which will be the matching entry from the commands table.
    """
    candidate = get_candidates (input_str, commands)
    if   len (candidate) == 0:
        raise UnknownCommandError (input_str)
    elif len (candidate) > 1:
        raise MultipleCommandError (input_str, candidate.keys ())
    return candidate

#eof commands.py
