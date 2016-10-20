# -*- coding: utf-8 -*-
## Copyright (c) 2016 by Sony Interactive Entertainment, Inc.
## This file is subject to the terms and conditions defined in file
## 'LICENSE.txt', which is part of this source code package.

.SUFFIXES:
vpath %.toy ..
include ../toyconfig.mk

OBJECTS = sieve.o main.o
.PHONY: all
all: $(OBJECTS)

.PHONY: clean
clean:
	-$(RM) $(OBJECTS) repo.yaml

#eof agent2/Makefile
