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

# System modules
import argparse
import logging
import signal
import sys
from typing import Iterable, Sequence

from toydb import command_processor, list_cmd, load_cmd, stacks, step_cmd
from toyvm import machine

_logger = logging.getLogger (__name__)

EXIT_SUCCESS = 0
EXIT_FAILURE = 1


def continue_handler (machine: machine.Machine, _) -> None:
    """
    Handles the 'continue' command which resumes execution of the debuggee.

    :param machine: The machine on which the debuggee is being run.
    :return: Nothing.
    """

    if len (machine.dict_s) < 2:
        _logger.warn ('No loaded program')
    machine.run_all ()


HELP = {
    'dictstack': "Displays the contents of the VM's dictionary stack",
    'opstack': "Displays the contents of the VM's operand stack",
    'execstack': "Displays the contents of the VM's execution stack",
    'load': "Loads the named executable file into the VM and prepares it for execution",
    'continue': "Executes the contents of the execution stack until it exhausted",
    'list': 'list',
    'step': 'step',
    'next': 'next',
    'help': 'This help text.',
    'quit': 'Exits the debugger.'
}


def help_handler (_, tokens: Sequence [str]) -> None:
    """
    Displays the command help.

    :param tokens: Any arguments passed to this command (none are expected).
    :return: Nothing
    """

    if len (tokens) != 0:
        _logger.warn ('Ignored unexpected arguments')

    longest = max (len (s) for s in HELP.keys ())
    for key in sorted (HELP.keys ()):
        spacing = ' ' * (longest - len (key) + 1)
        print (key + spacing + HELP [key])


def quit_handler (_, tokens: Sequence [str]) -> None:
    """
    Exits from the debugger.

    :param tokens: Any arguments passed to this command (none are expected).
    :return: Nothing
    """

    if len (tokens) != 0:
        _logger.warn ('Ignored unexpected arguments')
    _logger.info ('Bye')
    sys.exit (0)


def signal_handler (signal, frame):
    # TODO: can I get this to interrupt a running program?
    print ('You pressed Ctrl+C!')
    sys.exit (0)


class Options:
    """
    A class to represent the options that can be set of the program's command line.
    """

    def __init__ (self, opt) -> None:
        self.command = opt.command
        self.verbose = opt.verbose
        self.program = opt.program
        self.debug = opt.debug


def command_line (args: Iterable [str], program: str = 'toydb') -> Options:
    """
    Processes options from the command line.
    :param args: A list of arguments to be parsed.
    :param args: The prgoram name to be used in the option help text.
    :return: An object containing the user's options.
    """
    parser = argparse.ArgumentParser (prog=program, description='Debug a Toy program.')
    parser.add_argument ('program', nargs='?',
                         help='A Toy program to be debugged.')
    parser.add_argument ('-c', '--command', action='append',
                         help='Execute a command; specify once for each command')
    parser.add_argument ('-v', '--verbose', action='store_true',
                         help='Produce verbose output')
    parser.add_argument ('--debug', action='store_true', help='Emit debugging trace.')
    return Options (parser.parse_args (args))


PROMPT = '(toydb) '
COMMANDS = {
    'dictstack': stacks.dict_stack_handler,
    'opstack': stacks.operand_stack_handler,
    'execstack': stacks.execution_stack_handler,

    'load': load_cmd.load_handler,
    'continue': continue_handler,
    'list': list_cmd.list_handler,

    'step': step_cmd.step_handler,
    'next': step_cmd.next_handler,

    'help': help_handler,
    'quit': quit_handler,
}


def main (args: Sequence [str] = sys.argv [1:]) -> int:
    options = command_line (args)
    try:
        signal.signal (signal.SIGINT, signal_handler)

        # Set the root logger's level: this controls the messages that will appear on the console.
        logging.getLogger ().setLevel (logging.DEBUG if options.verbose else logging.INFO)

        _logger.info ("Toy debugger. Remember, it's just a toy.")

        mach = machine.Machine ()
        if options.program:
            load_cmd.load_handler (machine=mach, tokens=[options.program])

        cmd = command_processor.CommandProcessor (machine=mach, commands=COMMANDS)
        if options.command is not None:
            for c in options.command:
                cmd.command (c)
        else:
            while True:
                try:
                    cmd.command (input (PROMPT))
                except EOFError:
                    # Turn an EOF (^D) into a quit command.
                    cmd.command ('quit')
    except Exception as ex:
        if options.debug:
            raise
        else:
            _logger.error (ex)
        return EXIT_FAILURE
    return EXIT_SUCCESS


if __name__ == '__main__':
    logging.basicConfig (level=logging.DEBUG, format='')
    sys.exit (main ())

# eof toydb/__main__.py
