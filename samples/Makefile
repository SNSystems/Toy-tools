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
