# -*- coding: utf-8 -*-
## Copyright (c) 2016 by Sony Interactive Entertainment, Inc.
## This file is subject to the terms and conditions defined in file
## 'LICENSE.txt', which is part of this source code package.

ifeq ($(OS),Windows_NT)
PYTHON=python3
else
PYTHON=/usr/bin/env python3
endif

.PHONY: all
all: test samples
.PHONY: clean
clean: clean_samples
.PHONY: clean_samples
clean_samples:
	$(MAKE) -C samples clean
.PHONY: samples
samples:
	$(MAKE) -C samples all
.PHONY: test
test:
	$(PYTHON) -m discover
.PHONY: run
run:
	$(MAKE) -C samples run
#eof Makefile
