CDSL_MANS_GZ=com-cdslinvchk.1.gz com-mkcdsl.1.gz com-cdslinvadm.1.gz com-rmcdsl.1.gz

CLUSTER_MAN_GZ=com-queryclusterconf.1.gz

GZIP=gzip -f
DOCBOOK2MAN=docbook2x-man
RM=rm

.SUFFIXES: .1 .gz .xml

%.1.gz: %.1
	$(GZIP) $<

%.1: %.xml
	$(DOCBOOK2MAN) $<

.PHONY: comoonics-cdsl-py
comoonics-cdsl-py: $(CDSL_MANS_GZ)

.PHONY: comoonics-cluster-py
comoonics-cluster-py: $(CLUSTER_MAN_GZ)

.PHONY: man
man: comoonics-cdsl-py comoonics-cluster-py

.PHONY:clean
clean:
	$(RM) -f *.1.gz