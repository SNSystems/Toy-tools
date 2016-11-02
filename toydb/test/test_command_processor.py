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

import sys
import unittest
from toydb import command_processor
from contextlib import contextmanager
from io import StringIO

@contextmanager
def capture_stderr():
    old_stderr, sys.stderr = sys.stderr, StringIO()
    yield sys.stderr
    sys.stderr = old_stderr

class FakeMachine:
    def __init__(self):
        self.recorded_handlers = []

    def record_handler_dispatch(self, name, parameters):
        self.recorded_handlers.append((name, parameters))

class NamedHandler:
    def __init__(self, name):
        self.name = name

    def __call__(self, machine, parameters):
        machine.record_handler_dispatch(self.name, parameters)

class TestCommandProcessor (unittest.TestCase):

    commands = {
        'bar': NamedHandler('bar'),
        'foo': NamedHandler('foo'),
        'wibble': NamedHandler('wibble'),
        'wobble': NamedHandler('wobble'),
    }

    def setup_sut(self):
        machine = FakeMachine()
        cmd = command_processor.CommandProcessor (machine=machine, commands=TestCommandProcessor.commands)
        return machine, cmd

    def test_simple_command (self):
        machine, cmd = self.setup_sut()
        cmd.command('foo')
        self.assertEqual([('foo', [])], machine.recorded_handlers)

    def test_command_with_param (self):
        machine, cmd = self.setup_sut()
        cmd.command('bar param')
        self.assertEqual([('bar', ['param'])], machine.recorded_handlers)

    def test_command_with_multiple_params (self):
        machine, cmd = self.setup_sut()
        cmd.command('bar param1 param2')
        self.assertEqual([('bar', ['param1', 'param2'])], machine.recorded_handlers)

    def test_command_with_quoted_param (self):
        machine, cmd = self.setup_sut()
        cmd.command('bar "param1 param2"')
        self.assertEqual([('bar', ['param1 param2'])], machine.recorded_handlers)

    def test_command_with_shortened_name_resolution (self):
        machine, cmd = self.setup_sut()
        cmd.command('wi')
        self.assertEqual([('wibble', [])], machine.recorded_handlers)

    def test_command_with_shortened_name_resolution_with_param (self):
        machine, cmd = self.setup_sut()
        cmd.command('wi param')
        self.assertEqual([('wibble', ['param'])], machine.recorded_handlers)

    def test_unknown_command (self):
        machine, cmd = self.setup_sut()
        with capture_stderr() as stderr:
            cmd.command('unknown')
        self.assertEqual([], machine.recorded_handlers)
        self.assertEqual('Error: Unknown command "unknown"\n', stderr.getvalue())

    def test_shortened_name_resolution_ambiguity (self):
        machine, cmd = self.setup_sut()
        with capture_stderr() as stderr:
            cmd.command('w')

        self.assertEqual([], machine.recorded_handlers)
        self.assertEqual('Error: Unknown command "w". Did you mean one of:\nwibble  \nwobble\n\n', stderr.getvalue())

    def test_rerun_last_command(self):
        machine, cmd = self.setup_sut()
        cmd.command('wi param')
        cmd.command('') # If the user hits enter with no command, run previous command
        self.assertEqual([
            ('wibble', ['param']),
            ('wibble', ['param'])
        ], machine.recorded_handlers)

if __name__ == '__main__':
    unittest.main ()

#eof test_command_processor.py
