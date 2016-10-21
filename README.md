# A Toy Example

This project contains a collection of tools whose sole purpose in life is to demonstrate the design and workings of the Whole Program Repository. It consists of the following tools:

Tool | Role
------------- | -------------
`toycc`  | A Toy compiler.
`toyld`  | A static linker for Toy programs.
`toyvm` | A virtual machine which can execute Toy programs.
`toydb` | A Toy debugger.
`toygc` | A manual Repository garbage collector.
`toystrip` | A repository strip utility for distributed builds.
`toymerge` | A utility to merge repositories for distributed builds. It adds definitions from repositories modified by one or more remote agents.

If, for some reason, you'd like to read about the Toy language, it is described in the [reference manual](toy_refman.md).

## Prerequisites

Tested with Python 3.5. Additional non-standard modules required are:

Name | Description | Install
-----|-------------|--------
PyYAML | YAML implementation for Python <http://pyyaml.org> | `pip install pyyaml`
PyParsing | Parsing library <https://pyparsing.wikispaces.com> | `pip install pyparsing`
discover | Unit test discovery | `pip install discover`

The sample programs assume that GNU make is available and on the path.


## Setup

Once the Python 3.5 interpreter and the prerequisites are installed, the only remaining step is to ensure that the project's `bin` directory appended to the `PATH` environment variable, and the project directory (containing the Python modules) is added to the `PYTHONPATH` environment variable. 

### Linux/macOS

The `setup` shell script handles this step:

    $ . ./setup

(Don't forget the leading `.` (`source`) command.)

### Windows

The `setup.bat` batch file handles this step for the CMD shell:

    C:\toy_tools\samples\distributed>setup.bat


## "Binary" files

For simplicity of implementation, and to enable the contents of the files to be easily viewed and understood without additional tools, YAML is used for all of the files that would contain binary in a typical programming environment. Object and executable files are YAML as are Program Repositories.


## The Toy Programming Language

The Toy programming language itself is very simple, stack-based, and primarily intended to be very simple to parse and execute. It bears a resemblance to Adobe PostScript although is far less complex. Only 4 data types are on offer: floating-point numbers, strings, boolean true and false, and key/value pair dictionaries. The virtual machine employs three stacks:

- The operand stack is used for arguments and results from the built-in operators
- The dictionary stack is used for name lookup
- The execution stack cannot be accessed by the user program and is used by the virtual machine to determine which instructions are to be executed.

Programs are composed from "named procedures". Each is a name followed by a braced-enclosed sequence of instructions.


Getting Started
----
The first program to write is the same for all languages: print the words "hello, world". In Toy, the program looks like:

    main {
        "hello, world" print
    }

Typical build workflow is intended to fairly closely mirror that of a typical C development environment, with the exception that the compiler is just that: a compiler, rather than a "compiler driver" which knows how to run an assembler or link programs. Taking a simple, single source file, "hello.toy" program, compiling to an "object file" named "hello.to" and linking it to make "hello.tx" would look like:

    $ toycc -g -o hello.to hello.toy
    $ toyld -o hello.tx  hello.to

The tools don't produce a native binary, so running it is a little different, but not terribly complex:

    $ toyvm hello.tx

When run, it will print

    hello, world


Debugging Toy programs
---
The tools suite includes a simple, very limited, command-line debugger. Sporting a simple GDB-like syntax it enables:

 - A Toy program to be executed one instruction at a time.
 - The source-correspondence of the instructions to be checked.
 - The state of the Toy virtual machine to be inspected.

Running the debugger is straightforward:

     $ toydb main.tx
     Toy debugger. Remember, it's just a toy.
     Executable "main.tx" was not found
     (toydb)

The commands supported are a very basic subset of GDB-like commands; the main ones being:

- "help" to see the complete list of supported commands
- "step": execute a single instruction
- "list" to display the source code around the next instruction to be executed
- "continue" to run the program to completion
- "quit" to exit from the debugger
