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
	${CC} -DSAVE_BOOK_BIN=1 -DSUBTRACTIVE_RND=1 -DMAXBOOKSIZE=10000 mscp.c -o dumpbook

book.bin: # dumpbook book.txt mscp.c
	./dumpbook

../book.gt1: book.bin
	python3 bintogt1.py book.bin $@

clean:
	-rm ${OBJS} ${PGMS} dumpbook mscp

