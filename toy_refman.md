# The Toy Programming Language 

The Toy programming language is heavily based on [PostScript](www.adobe.com/products/postscript), albeit a highly stripped-down version of the language. The syntax differs slightly in the use of the number sign ('#') rather than percent ('%') to introduce a comment, and quotation marks ('"') rather than parentheses ('(' and ')') to delimit strings. The major change is that rather than an interpreter which reads and executes a source stream, there is a compiler and linker in the same way as in a statically-compiled language.

## Introduction

### Hello ###

Every description of a programming language has to start with the classic "Hello world" program. Here's Toy's:

    main {
        "Hello, World" print
    }

You should create the program in a file `hello.toy`, then compile and link it with with the commands:

    $ toycc hello.toy
    $ toyld hello.tobj

Finally we can run the program:

    $ toyvm a.out

It will print:

    Hello, World

Now to explain the program itself. In outline it looks like `main { ... }`. This defines a "procedure" (the bit between the curly braces) whose name is "main". Toy programs always start at a procedure named "main". A procedure is a series of instructions to be executed. The first instruction in the procedure is:

    "Hello, World"
   
This series of characters enclosed in double-quotes is a _character string_ or just _string_ instruction. In Toy, executing a string places it on the _operand stack_. This is a "last in, first out" (LIFO) data structure. The operand stack holds arbitrary objects that are the operands and results of the instruction being executed. When an instruction requires or or more operands, it obtains them by popping them off the top of the operand stack. When an instruction returns one or more results, it does so by pushing them on the operand stack.

The second instruction in our hello.toy program is simply:

    print
    
`print` is a built-in name which pops a value from the operand stack &mdash; the string "Hello, World" in our case &mdash; and prints it to standard-out.

### Some Arithmetic ###

A simple calculation to add the numbers two and three can written using conventional algebraic notation as:

    2 + 3

This form of notation can be described as "infix" because the operation &mdash; addition &mdash; lies between the two values to be added (the _operands_). Alternatively, the operation could be written _before_ the two operands:

    + 2 3
   
This notation is sometimes known as "Polish notation" and may be familiar from programming languages such as Lisp. Toy, like PostScript and Forth and Hewlett Packard calculators, employs so-called "Reverse Polish Notation" in which the same addition is written as:

    2 3 +

In Toy, this same expression would be written as:

    2 3 add

This snippet of code consists of three instructions. The first two are both numbers; executing a number places it on the operand stack (in the same way that we've already seen for strings). The third instruction, "add" is the name of a built-in operator which removes two numbers from the operand stack, adds them, then places the result back on the operand stack.


### Decisions, Decisions ###

(a brief discussion of procedures, booleans, if/ifelse)

## Objects ###

### Simple Objects ###

#### Numbers

Numbers are always floating point. Executing a number object places it on the operand stack.

#### Booleans

true or false. Executing a boolean object places it on the operand stack.

#### Strings

An array of characters. Executing a string object places it on the operand stack.

#### Operators

### Compound Objects ###

Compound objects are different from simple objects in that when a copy is made of the object, the runtime simply makes a new reference to the original object; modifications to the original object will also be reflected in the copy.

#### Dictionaries

Dictionaries can originate from any of several sources. There is the "system" dictionary which contains the collection of built-in operators and which is available when the runtime is initialized. There is the "program dictionary" which results from loading a program into the runtime: it contains the names and their corresponding procedures from the program. Finally, dictionaries may be explicitly created by the program at run-time (using the [dict](#BIdict) operator)

#### Procedures


## [Stacks](id:stacks) ##

Like PostScript or [Forth](http://www.forth.org), the language and runtime use stacks extensively. The runtime employs three separate stacks; they are:

- The operand stack. As explained above, this is stack is under the explicit control of the program and is used to store the operands and results of instructions.

- The [dictionary stack](id:dictstack). i
- The execution stack. The execution stack is managed by the runtime and cannot be explicitly manipulated by the program.


## Built-in Operators

#### [add](id:BIadd)

_num<sub>1</sub>_ _num<sub>2</sub>_ **add** _sum_

Pops two numbers from the operand stack (num<sub>1</sub> and num<sub>2</sub>) and pushes the result of adding them.

See also: [div](#BIdiv) [mul](#BImul) [sub](#BIsub)

#### [begin](id:BIbegin)

_dict_ **begin** &mdash;

Pushes _dict_ on the dictionary stack, making it the current dictionary and installing it as the first of the dictionaries consulted during name lookup and by **def**.

See also: [def](#BIdef) [dict](#BIdict) [end](#BIend)

#### [currentdict](id:BIcurrentdict)

#### [currenttrace](id:BIcurrenttrace)

&mdash; **currenttrace** _bool_

Pushes a boolean value indicating whether the machine's trace state is enabled.

See also: [trace](#BItrace)

#### [def](id:BIdef)

_key_ _value_ **def** &mdash;

Associates _key_ with _value_ in the current dictionary (the one on the top of the [dictionary stack](#dictstack)). If _key_ is already present in the current dictionary, **def** simply replaces its value; otherwise, **def** creates a new entry for _key_ and stores _value_ with it.

See also: [begin](#BIbegin) [end](#BIend) [get](#BIget)

#### [dict](id:BIdict)

&mdash; **dict** _dict_

Creates an empty dictionary and pushes it onto the operand stack.

See also: [begin](#BIbegin) [end](#BIend)

#### [div](id:BIdiv)

_num<sub>1</sub>_ _num<sub>2</sub>_ **div** _quotient_

Divides _num<sub>1</sub>_ by _num<sub>2</sub>_, producing a number.

See also: [add](#BIadd) [mul](#BImul) [sub](#BIsub)

#### [dup](id:BIdup)

_any_ **dup** _any_ _any_

Duplicates the top element on the operand stack.
 
See: [pop](#BIpop) [exch](#BIexch)

#### [end](id:BIend)

See also: [begin](#BIbegin)

#### [eq](id:BIeq)

See also: [ne](#BIne)

#### [exch](id:BIexch)

See also: dup pop

#### [exec](id:BIexec)

_proc_ **exec** &mdash;

Pushes the instructions contained in the procedure _proc_ onto the execution stack so that they will are executed immediately.

#### [for](id:BIfor)

_initial_ _increment_ _limit_ _proc_ **for** &mdash;

Executes the procedure _proc_ repeatedly, passing it a sequence of values from initial by steps of _increment_ to _limit_. The **for** operator expects _initial_, _increment_, and _limit_ to be numbers. It maintains a temporary internal variable, known as the control variable, which it first sets to _initial_. Then, before each repetition, it compares the control variable to the termination value _limit_. If _limit_ has not been exceeded, **for** pushes the control variable on the operand stack, executes _proc_, and adds _increment_ to the control variable.

The termination condition depends on whether _increment_ is positive or negative. If _increment_ is _positive_, **for** terminates when the control variable becomes greater than _limit_. If _increment_ is negative, **for** terminates when the control variable becomes less than _limit_. If _initial_ meets the termination condition, **for** does not execute _proc_ at all.

#### [get](id:BIget)

#### [if](id:BIif)

_bool_ _proc_ **if** &mdash;

Removes both operands from the stack, then executes _proc_ if _bool_ is true. The **if** operator pushes no results of its own on the operand stack, but _proc_ may do so.

See also: [ifelse](#BIifelse)

#### [ifelse](id:BIifelse)

_bool_ _proc<sub>1</sub>_ _proc<sub>2</sub>_ **ifelse** &mdash;

Removes all three operands from the stack, then executes _proc<sub>1</sub>_ if _bool_ is true or _proc<sub>2</sub>_ if _bool_ is false. The **ifelse** operator pushes no results of its own on the operand stack, but the procedure it executes may do so.

See also: [if](#BIif)

#### [known](id:BIknown)

_dict_ _key_ **known** _bool_

Returns true if there is an entry in the dictionary _dict_ whose key is _key_; otherwise, it returns false. _dict_ does not have to be on the dictionary stack.

#### [mul](id:BImul)

See also: [add](#BIadd) [div](#BIdiv) [sub](#BIsub)

#### [ne](id:BIne)

See also: [eq](#BIeq)

#### [pop](id:BIpop)

_obj_ **pop** &mdash;

Removes the object from the top of the stack and discards it.

See also: [dup](#BIdup) [exch](#BIexch)

#### [print](id:BIprint)

_obj_ **print** &mdash;

Converts the value of _obj_ to a string and prints the resulting characters to the standard output file. If _obj_ is a string, then the characters of the string printed verbatim, otherwise the conversion of _obj_ to string is implementation-defined.

#### [sub](id:BIsub)

_num<sub>1</sub>_ _num<sub>2</sub>_ **sub** _difference_

The result of subtracting _num<sub>1</sub>_ from _num<sub>2</sub>_.

See also: [add](#BIadd) [div](#BIdiv) [mul](#BImul)

#### [stack](id:BIstack)

&mdash; **stack** &mdash;

Prints the contents of the operand stack to the standard output file. The contents of the stack are not affected. Conversion of stack objects to a string representation for printing follows the same results as the **print** operator.

See also: [print](#BIprint)

#### [systemdict](id:BIsystemdict)

#### [trace](id:#BItrace)

bool _trace_ &mdash;

Enables or disables the virtual machine's "trace" option. Enabling the trace causes the current instruction to be written to the standard output file before it is executed. Be aware that even small programs can generate a lot of output.

See also: [currenttrace](#BIcurrenttrace)


## Grammar ##

    EOL ::= ? end of line ?
    any ::= ? any character except EOL ?
    digit ::= "0"..."9"
    letter ::= [a-zA-Z]
    ident ::= letter (letter | digit | '_')*

    int-part ::= digit+
    fraction ::= "." digit+
    exponent ::= ("e" | "E") ["+" | "-"] digit+
    point-float ::= [int-part] fraction | int-part "."?
    exponent-float ::= (int-part | point-float) exponent
    number ::= point-float | exponent-float

    comment ::= '#' any* EOL

    string-character ::= (any* - '"')
    string ::= '"' string-character* '"'

    instruction ::=   comment | "false" | "true" | number 
                    | procedure | string | ident
    
    procedure ::= '{' instruction* '}'
    named-procedure ::= ident comment? procedure

    grammar ::= (comment | named-procedure)*

