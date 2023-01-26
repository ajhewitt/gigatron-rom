ROM=dev7
MAP=128k
GLCC=glcc
PGMS=../mscp.gt1 ../book.gt1
OBJS=mscp.o core.o

all: ${PGMS}

../mscp.gt1: ${OBJS} mscp.ovl
	${GLCC} -rom=${ROM} -map=${MAP},./mscp.ovl ${OBJS} -o $@

mscp.o: mscp.c core.h
	${GLCC} -rom=${ROM} -c $<

core.o: core.c core.h
	${GLCC} -rom=${ROM} -DBOOKSIZE=`wc -c < book.bin` -c $<

dumpbook: mscp.c
	${CC} -DSAVE_BOOK_BIN=1 -DSUBTRACTIVE_RND=1 -DMAXBOOKSIZE=13000 mscp.c -o dumpbook

book.bin: dumpbook book.txt mscp.c Makefile
	./dumpbook

../book.gt1: #book.bin
	python3 bintogt1.py --addr=0xc000 book.bin $@

clean:
	-rm ${OBJS} *.gt1 *.prf *.frg prof.txt dumpbook mscp


# Profiling support

GTSIM=gtsim -rom ../../../dev128k7.rom
GTPROF=gtprof
CFILES=${OBJS:.o=.c}

prof.txt: mscp-sim.prf
	${GTPROF} mscp-sim.prf mscp-sim.frg | sort -nr > $@

mscp-sim.gt1: ${CFILES} mscp.ovl
	${GLCC} -rom=${ROM} -map=sim,allout,./mscp.ovl \
	    -DREPEATABLE_RND=1 ${CFILES} -o $@ --frags > mscp-sim.frg

mscp-sim.prf: mscp-sim.gt1 prof.in
	${GTSIM} -prof $@ mscp-sim.gt1 < prof.in


