# -*- coding: utf-8 -*-
## Copyright (c) 2016 by Sony Interactive Entertainment, Inc.
## This file is subject to the terms and conditions defined in file
## 'LICENSE.txt', which is part of this source code package.

.SUFFIXES:

ifeq ($(OS),Windows_NT)
    RM=del
else
    RM=rm -f
endif

%.o: %.toy
	toycc -g --verbose -o $@ $^
%.x: %.o
	toyld -o $@ $^

OBJECTS = main.o factorial.o sieve.o

.PHONY: all
all: main.x

.PHONY: run
run: main.x
	toyvm $<

.PHONY: clean
clean:
	-$(RM) main.x $(OBJECTS) repo.yaml

.PHONY: gc
gc:
	toygc --verbose

main.x: $(OBJECTS)

#eof Makefile
