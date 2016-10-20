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


.PHONY: all
all: hello.x

.PHONY: run
run: hello.x
	toyvm $<

.PHONY: clean
clean:
	$(RM) hello.x hello.o repo.yaml

.PHONY: gc
gc:
	toygc

hello.x: hello.o

#eof Makefile
