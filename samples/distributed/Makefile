# -*- coding: utf-8 -*-
## Copyright (c) 2016 by Sony Interactive Entertainment, Inc.
## This file is subject to the terms and conditions defined in file
## 'LICENSE.txt', which is part of this source code package.

.SUFFIXES:
include toyconfig.mk

VPATH = .:agent1:agent2

OBJECTS = \
	$(call FIXPATH,agent1/factorial.o) \
	$(call FIXPATH,agent2/sieve.o) \
	$(call FIXPATH,agent2/main.o)

REPOS = $(call FIXPATH,agent1/repo.yaml) \
	$(call FIXPATH,agent2/repo.yaml) \
	repo.yaml \
	repoc.yaml

.PHONY: all
all: main.x

.PHONY: clean
clean:
	-$(RM) $(OBJECTS) $(REPOS) main.x
	$(MAKE) -C agent1 clean
	$(MAKE) -C agent2 clean

# Strip the fragment bodies from repo.yaml to produce repoc.yaml then distribute that file to both agents.
define dist-repo
	@echo ** Distribute repository to agent 1 and 2
	toystrip -i repo.yaml -o repoc.yaml
	$(CP) repoc.yaml $(call FIXPATH,agent1/repo.yaml)
	$(CP) repoc.yaml $(call FIXPATH,agent2/repo.yaml)
	$(RM) repoc.yaml
endef

# Distribute the repository if it exists.
.PHONY: distributed-repository
distributed-repository:
	$(if $(wildcard repo.yaml), $(dist-repo), @echo ** No repository)

$(call FIXPATH,agent1/factorial.o) $(call FIXPATH,agent1/main.o): distributed-repository
	$(MAKE) -C agent1

$(call FIXPATH,agent2/sieve.o) $(call FIXPATH,agent2/main.o): distributed-repository
	$(MAKE) -C agent2

main.x: $(OBJECTS)
	toymerge $(call FIXPATH,agent1/repo.yaml) $(call FIXPATH,agent2/repo.yaml)
	$(TLD) -o $@ $(TLDFLAGS) $^

.PHONY: run
run: main.x
	$(TVM) $(TVMFLAGS) $<

.PHONY: gc
gc:
	$(TGC) $(TGCFLAGS)

#eof distributed/Makefile
