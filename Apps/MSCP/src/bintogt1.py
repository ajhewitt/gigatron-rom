import argparse, os, sys

def save_gt1(fname, data, addr, execa=0):
    with open(fname,"wb") as fd:
        for page in range(0, len(data), 256):
            pagedata = data[page:page+256]
            fd.write(bytes(((addr>>8)&255, addr&255, len(pagedata)&255)))
            fd.write(pagedata)
            addr += 256
        fd.write(bytes((0, (execa>>8)&255, execa&255)))

def bintogt1(argv):
    try:
        parser = argparse.ArgumentParser(
            usage='bintogt1 --addr=<xxx> <binfile> <gt1file>',
            description='Converts a raw binary file into a GT1 file')
        parser.add_argument('bin', type=str, help='input file')
        parser.add_argument('gt1', type=str, help='output file')
        parser.add_argument('--addr', type=str, help='gt1 start address',
                            action='store', default='0x8000' )
        args = parser.parse_args(argv)
        with open(args.bin,"rb") as fd:
            data = fd.read()
        save_gt1(args.gt1, data, int(args.addr, 0))
        return 0
    except FileNotFoundError as err:
        print(str(err), file=sys.stderr)
    #except Exception as err:
    #    print(repr(err), file=sys.stderr)
        
if __name__ == '__main__':
    sys.exit(bintogt1(sys.argv[1:]))

# Local Variables:
# mode: python
# indent-tabs-mode: ()
# End:
	
