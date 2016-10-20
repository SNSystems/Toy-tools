# -*- coding: utf-8 -*-
## Copyright (c) 2016 by Sony Interactive Entertainment, Inc.
## This file is subject to the terms and conditions defined in file
## 'LICENSE.txt', which is part of this source code package.

#
# This file contains variables that are used by the "distributed" sample to ensure that we
# have just a single definition for each of them that is used by the host and its two
# (simulated) agents.
#

ifeq ($(OS),Windows_NT)
    RM=del
    CP=copy
    FIXPATH=$(subst /,\,$1)
else
    RM=rm -f
    CP=cp
    FIXPATH = $1
endif


# The Toy compiler
TCC = toycc
TCFLAGS = -g --verbose #--debug-parse

# The Toy linker
TLD = toyld
TLDFLAGS = #--verbose

# The Toy virtual machine
TVM = toyvm
TVMFLAGS =

# The Toy garbage collector
TGC = toygc
TGCFLAGS = --verbose

%.o: %.toy
	$(TCC) $(TCFLAGS) -o $@ $<

#eof toyconfg.mk
