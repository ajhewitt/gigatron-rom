
# Marcel's Simple Chess Program

MSCP, Marcel's Simple Chess Program by Marcel van Kervinck, is a
small, simple, yet complete open source chess engine released under
the GNU GPL. This version has been adapted to work on the Gigatron
which is another brainchild of Marcel.

https://www.chessprogramming.org/MSCP


## Changes

The main change relocates the `union core` structure containing
the compiled opening book and the transposition table into bank 3
of the 128k gigatron. To that effect, the file `mscp.ovl` ensures
that all objects defined in file `core.c` are placed below 0x7fff
and therefore remain accessible when the banks are switched.

The random generator has been changed to a subtractive generator
that avoids costly long multiplications.

The opening book is loaded into bank3 using SYS_Exec.
