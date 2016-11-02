# -*- coding: utf-8 -*-
## Copyright (c) 2016 by Sony Interactive Entertainment, Inc.
## This file is subject to the terms and conditions defined in file
## 'LICENSE.txt', which is part of this source code package.

define make-samples
	$(MAKE) -C distributed $@
	$(MAKE) -C hello $@
	$(MAKE) -C modules $@
endef

.PHONY: all
all:
	$(make-samples)
.PHONY: run
run:
	$(make-samples)
.PHONY: clean
clean:
	$(make-samples)
#eof samples/Makefile
