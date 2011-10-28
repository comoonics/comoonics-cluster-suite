include ../../Makefile.inc

.PHONY: test
test:
	make PACKAGES="$(PACKAGES)" -C test test
	@for dir in `find ./ -maxdepth 1 -type d -not -wholename "*test*" -not -wholename "./"`; do \
		make -C $$dir test || exit 1; \
	done
