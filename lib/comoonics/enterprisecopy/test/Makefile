include ../../../../Makefile.inc

TESTS:=$(shell ls test*.py | grep -v testStorage)
CTESTS:=$(TESTS:.py=.pyc)
TESTSDONE=$(TESTS:%.py=.%)

.% : %.py
	PYTHONPATH=$(PYTHONPATH) python $<

.PHONY: clean
clean:
	rm -f $(CTESTS)

.PHONY: test
test: $(TESTSDONE)
