#!/usr/bin/env python3
#-----------------------------------------------------------------------
#
#  Core video, sound and interpreter loop for Gigatron TTL microcomputer
#
#-----------------------------------------------------------------------
#
#  Main characteristics:
#
#  - 6.25 MHz clock
#  - Rendering 160x120 pixels at 6.25MHz with flexible videoline programming
#  - Must stay above 31 kHz horizontal sync --> 200 cycles/scanline
#  - Must stay above 59.94 Hz vertical sync --> 521 scanlines/frame
#  - 4 channels sound
#  - 16-bits vCPU interpreter
#  - 8-bits v6502 emulator
#  - Builtin vCPU programs (Snake, Racer, etc) loaded from unused ROM area
#  - Serial input handler, supporting ASCII input and two game controller types
#  - Serial output handler
#  - Soft reset button (keep 'Start' button down for 2 seconds)
#  - Low-level support for I/O and RAM expander (SPI and banking)
#
#-----------------------------------------------------------------------
#
#  ROM v2: Mimimal changes
#
#  DONE Snake color upgrade (just white, still a bit boring)
#  DONE Sound continuity fix
#  DONE A-C- mode (Also A--- added)
#  DONE Zero-page handling of ROM loader (SYS_Exec_88)
#  DONE Replace Screen test
#  DONE LED stopped mode
#  DONE Update font (69;=@Sc)
#  DONE Retire SYS_Reset_36 from all interfaces (replace with vReset)
#  DONE Added SYS_SetMemory_54 SYS_SetVideoMode_80
#  DONE Put in an example BASIC program? Self list, self start
#  DONE Move SYS_NextByteIn_32 out page 1 and rename SYS_LoaderNextByteIn_32
#       Same for SYS_PayloadCopy_34 -> SYS_LoaderPayloadCopy_34
#  DONE Update version number to v2a
#  DONE Test existing GT1 files, in all scan line modes
#  DONE Sanity test on HW
#  DONE Sanity test on several monitors
#  DONE Update version number to v2
#
#-----------------------------------------------------------------------
#
#  ROM v3: New applications
#
#  DONE vPulse width modulation (for SAVE in BASIC)
#  DONE Bricks
#  DONE Tetronis
#  DONE TinyBASIC v2
#  DONE TicTacToe
#  DONE SYS spites/memcpy acceleration functions (reflections etc.)
#  DONE Replace Easter egg
#  DONE Update version number to v3
#
#-----------------------------------------------------------------------
#
#  ROM v4: Numerous small updates, no new applications
#
#  DONE #81 Support alternative game controllers (TypeC added)
#  DONE SPI: Setup SPI at power-on and add 'ctrl' instruction to asm.py
#  DONE SPI: Expander control (Enable/disable slave, set bank etc)
#  DONE SPI: SYS Exchange bytes
#  DONE SYS: Reinitialize waveforms at soft reset, not just at power on
#  DONE v6502: Prototype. Retire bootCount to free up zp variables
#  DONE v6502: Allow soft reset when v6502 is active
#  DONE Apple1: As easter egg, preload with WozMon and Munching6502
#  DONE Apple1: Don't use buttonState but serialRaw
#  DONE Snake: Don't use serialRaw but buttonState
#  DONE Snake: Head-only snake shouldn't be allowed to turn around #52
#  DONE Snake: Improve game play and colors in general
#  DONE Snake: Tweak AI. Also autoplayer can't get hiscore anymore
#  DONE Racer: Don't use serialRaw but buttonState
#  DONE Racer: Faster road setup with SYS_SetMemory
#  DONE Makefile: Pass app-specific SYS functions on command line (.py files)
#  DONE Main: "Press [A] to start": accept keyboard also (incl. 'A') #38
#  DONE Add 4 arrows to font to fill up the ROM page
#  DONE Mode 1975 (for "zombie" mode), can do mode -1 to recover
#  DONE TinyBASIC: support larger font and MODE 1975. Fix indent issue #40
#  DONE Add channelMask to switch off the higher sound channels
#  DONE Loader: clear channelMask when loading into sound channels
#  DONE Update romTypeValue and interface.json
#  DONE Update version number to v4
#  DONE Formally Support SPI and RAM expander: publish in interface.json
#  DONE Use `inspect' to make program listing with original comments #127
#
#-----------------------------------------------------------------------
#
#  Ideas for ROM v5:
#
#  DONE v6502: Test with VTL02
#  DONE v6502: Test with Microchess
#  DONE Sound: Better noise by changing wavX every frame (at least in channel 1)
#  DONE Sound demo: Play SMB Underworld tune
#  DONE SPI: Also reset state at soft reset
#  DONE Fix clobbering of 0x81 by SPI SYS functions #103
#  DONE Control variable to black out the area at the top of the screen
#  DONE Fix possible video timing error in Loader #100
#  DONE Fix zero page usage in Bricks and Tetronis #41
#  DONE Add CALLI instruction to vCPU
#  DONE Add CMPHS/CMPHU instructions to vCPU XXX Still needs testing
#  DONE Main: add Apple1 to main menu
#  DONE Replace egg with something new
#  DONE Split interface.json and interface-dev.json
#  DONE MSBASIC
#  DONE Speed up SetMemory by 300% using bursts #126
#  DONE Discoverable ROM contents #46
#  DONE Vertical blank interrupt #125
#  DONE TinyBASIC: Support hexadecimal numbers $....
#  DONE Expander: Auto-detect banking, 64K and 128K (multiple tests)
#  DONE Cardboot: Boot from *.GT1 file if SDC/MMC detected
#  DONE CardBoot: Strip non-essentials
#  DONE CardBoot: Fix card type detection
#  DONE CardBoot: Read full sector
#  DONE Apple-1: Memory mapped PIA emulation using interrupt (D010-D013)
#  DONE Apple-1: Include A1 Integer BASIC
#  DONE Apple-1: Suppress lower case
#  DONE Apple-1: Include Mastermind and 15-Puzzle
#  DONE Apple-1: Include mini-assembler
#  DONE Apple-1: Intercept cassette interface = menu
#  XXX  Reduce the Pictures application ROM footprint #120
#  DONE Mandelbrot: Faster Mandelbrot using qwertyface's square trick
#  PART Main: Better startup chime, eg. sequence the 4 notes and then decay
#  XXX  Main: Some startup logo as intro, eg. gigatron letters from the box
#  DONE Racer: Control speed with up/down (better for TypeC controllers)
#  DONE Racer: Make noise when crashing
#  NO   Loader: make noise while loading (only channel 1 is safe to use)
#  DONE Faster SYS_Exec_88, with start address (GT1)?
#  DONE Let SYS_Exec_88 clear channelMask when loading into live channels
#  UNK  Investigate: Babelfish sometimes freezes during power-on?
#
#  Ideas for ROM v6+
#  XXX  ROM functions: SYS_PrintString, control codes, SYS_DrawChar, SYS_Newline
#  XXX  v8080 prepping for CP/M
#  XXX  vForth virtual CPU
#  XXX  Video: Increase vertical resolution with same videoTable (160 lines?)
#  XXX  Video mode for 12.5 MHz systems
#  XXX  Pucrunch (well documented) or eximozer 3.0.2 (better compression)
#  XXX  SPI: Think about SPI modes (polarities)
#  XXX  I2C: Turn SPI port 2-3 into a I2C port as suggesred by jwolfram
#  XXX  Reset.c and Main.c (that is: port these from GCL to C, but requires LCC fixed)
#  XXX  Need keymaps in ROM? (perhaps undocumented if not tested)
#  XXX  FrogStroll (not in Contrib/)
#  XXX  How it works memo: brief description of every software function
#  XXX  Adjustable return for LUP trampolines (in case SYS functions need it)
#  XXX  Loader: make noise when data comes in
#  XXX  vCPU: Multiplication (mulShift8?)
#  XXX  vCPU: Interrupts / Task switching (e.g for clock, LED sequencer)
#  XXX  Scroll out the top line of text, or generic vertical scroll SYS call
#  XXX  SYS function for plotting a full character in one go
#  XXX  Multitasking/threading/sleeping (start with date/time clock in GCL)
#-----------------------------------------------------------------------

import importlib
from sys import argv
from os  import getenv

from asm import *
import gcl0x as gcl
import font_v4 as font


# Enable patches for 512k board --
# Roms compiled with this option take full advantage
# of the 512k extension board but are only suitable
# for the Gigatron512k.
WITH_512K_BOARD = defined('WITH_512K_BOARD')

# Enable patches for 128k board --
# Roms compiled with this option can only be used
# with a Gigatron equipped with a 128k extension board.
# This patch forces the framebuffer to remain in banks 0
# or 1 regardless of the bank selected for the vCPU.
# This is never needed for the Gigatron512k because the hardware
# enforces this. This may not be needed for a Gigatron128k equipped
# with a suitable hardware patch.
WITH_128K_BOARD = defined('WITH_128K_BOARD')


# Enable patches for the Novatron --
# This supports the particular way the Novatron wires its SPI
# inputs. This is enabled by default but can be suppressed to
# attempt support for more than two SPI inputs on Marcel's
# original RAM & IO extension.
WITH_NOVATRON_PATCH = defined('WITH_NOVATRON_PATCH', True)

# Rom name --
# This is the stem of the target rom name
# in case it differs from the source file stem
ROMNAME = defined('ROMNAME', argv[0])
if ROMNAME.endswith('.rom'):
    ROMNAME, _ = splitext(ROMNAME)
if ROMNAME.endswith('.py'):
    ROMNAME, _ = splitext(ROMNAME)
if ROMNAME.endswith('.asm'):
    ROMNAME, _ = splitext(ROMNAME)

# Displayed rom name --
# This is the name displayed by Reset.gcl.
# It defaults to '[DEV7]'
DISPLAYNAME = defined('DISPLAYNAME', "[DEV7]")




enableListing()
#-----------------------------------------------------------------------
#
#  Start of core
#
#-----------------------------------------------------------------------

# Pre-loading the formal interface as a way to get warnings when
# accidentally redefined with a different value
loadBindings('interface.json')
loadBindings('Core/interface-dev.json') # Provisional values for DEVROM

# Gigatron clock
cpuClock = 6.250e+06

# Output pin assignment for VGA
R, G, B, hSync, vSync = 1, 4, 16, 64, 128
syncBits = hSync+vSync # Both pulses negative

# When the XOUT register is in the circuit, the rising edge triggers its update.
# The loop can therefore not be agnostic to the horizontal pulse polarity.
assert syncBits & hSync != 0

# VGA 640x480 defaults (to be adjusted below!)
vFront = 10     # Vertical front porch
vPulse = 2      # Vertical sync pulse
vBack  = 33     # Vertical back porch
vgaLines = vFront + vPulse + vBack + 480
vgaClock = 25.175e+06

# Video adjustments for Gigatron
# 1. Our clock is (slightly) slower than 1/4th VGA clock. Not all monitors will
#    accept the decreased frame rate, so we restore the frame rate to above
#    minimum 59.94 Hz by cutting some lines from the vertical front porch.
vFrontAdjust = vgaLines - int(4 * cpuClock / vgaClock * vgaLines)
vFront -= vFrontAdjust
# 2. Extend vertical sync pulse so we can feed the game controller the same
#    signal. This is needed for controllers based on the 4021 instead of 74165
vPulseExtension = max(0, 8-vPulse)
vPulse += vPulseExtension
# 3. Borrow these lines from the back porch so the refresh rate remains
#    unaffected
vBack -= vPulseExtension

# Start value of vertical blank counter
videoYline0 = 1-2*(vFront+vPulse+vBack-2)

# Mismatch between video lines and sound channels
soundDiscontinuity = (vFront+vPulse+vBack) % 4

# QQVGA resolution
qqVgaWidth      = 160
qqVgaHeight     = 120

# Game controller bits (actual controllers in kit have negative output)
# +----------------------------------------+
# |       Up                        B*     |
# |  Left    Right               B     A*  |
# |      Down      Select Start     A      |
# +----------------------------------------+ *=Auto fire
buttonRight     = 1
buttonLeft      = 2
buttonDown      = 4
buttonUp        = 8
buttonStart     = 16
buttonSelect    = 32
buttonB         = 64
buttonA         = 128

#-----------------------------------------------------------------------
#
#  RAM page 0: zero-page variables
#
#-----------------------------------------------------------------------

# Memory size in pages from auto-detect
memSize         = zpByte()

# The current channel number for sound generation. Advanced every scan line
# and independent of the vertical refresh to maintain constant oscillation.
channel         = zpByte()

# Next sound sample being synthesized
sample          = zpByte()
# To save one instruction in the critical inner loop, `sample' is always
# reset with its own address instead of, for example, the value 0. Compare:
# 1 instruction reset
#       st sample,[sample]
# 2 instruction reset:
#       ld 0
#       st [sample]
# The difference is not audible. This is fine when the reset/address
# value is low and doesn't overflow with 4 channels added to it.
# There is an alternative, but it requires pull-down diodes on the data bus:
#       st [sample],[sample]
assert 4*63 + sample < 256
# We pin this reset/address value to 3, so `sample' swings from 3 to 255
assert sample == 3

# Former bootCount and bootCheck (<= ROMv3)
zpReserved      = zpByte() # Recycled and still unused. Candidate future uses:
                           # - Video driver high address (for alternative video modes)
                           # - v6502: ADH offset ("MMU")
                           # - v8080: ???
vCpuSelect      = zpByte() # Active interpreter page

# Entropy harvested from SRAM startup and controller input
entropy         = zpByte(2)

# Former entropy+2
reserved1       = zpByte(1)

# Visible video
videoY          = zpByte() # Counts up from 0 to 238 in steps of 2
                           # Counts up (and is odd) during vertical blank
videoModeB      = zpByte() # Handler for every 2nd line (pixel burst or vCPU)
videoModeC      = zpByte() # Handler for every 3rd line (pixel burst or vCPU)
videoModeD      = zpByte() # Handler for every 4th line (pixel burst or vCPU)

nextVideo       = zpByte() # Jump offset to scan line handler (videoA, B, C...)
videoPulse      = nextVideo # Used for pulse width modulation

# Frame counter is good enough as system clock
frameCount      = zpByte(1)

# Serial input (game controller)
serialRaw       = zpByte() # New raw serial read
serialLast      = zpByte() # Previous serial read
buttonState     = zpByte() # Clearable button state
resetTimer      = zpByte() # After 2 seconds of holding 'Start', do a soft reset
                           # XXX move to page 1 to free up space

# Extended output (blinkenlights in bit 0:3 and audio in bit 4:7). This
# value must be present in AC during a rising hSync edge. It then gets
# copied to the XOUT register by the hardware. The XOUT register is only
# accessible in this indirect manner because it isn't part of the core
# CPU architecture.
xout            = zpByte()
xoutMask        = zpByte() # The blinkenlights and sound on/off state

# vCPU interpreter
vTicks          = zpByte()  # Interpreter ticks are units of 2 clocks
vPC             = zpByte(2) # Interpreter program counter, points into RAM
vAC             = zpByte(2) # Interpreter accumulator, 16-bits
vLR             = zpByte(2) # Return address, for returning after CALL
vSP             = zpByte(1) # Stack pointer
vTmp            = zpByte()
vReturn         = zpByte()  # Return into video loop (in page of vBlankStart)

# Scratch
frameX          = zpByte() # Starting byte within page
frameY          = zpByte() # Page of current pixel line (updated by videoA)

# Vertical blank (reuse some variables used in the visible part)
videoSync0      = frameX   # Vertical sync type on current line (0xc0 or 0x40)
videoSync1      = frameY   # Same during horizontal pulse (0x80 or 0x00)

# Versioning for GT1 compatibility
# Please refer to Docs/GT1-files.txt for interpreting this variable
romType         = zpByte(1)

# The low 3 bits are repurposed to select the actively updated sound channels.
# Valid bit combinations are:
#  xxxxx011     Default after reset: 4 channels (page 1,2,3,4)
#  xxxxx001     2 channels at double update rate (page 1,2)
#  xxxxx000     1 channel at quadruple update rate (page 1)
# The main application for this is to free up the high bytes of page 2,3,4.
channelMask = symbol('channelMask_v4')
assert romType == channelMask

# SYS function arguments and results/scratch
sysFn           = zpByte(2)
sysArgs         = zpByte(8)
fsmState        = sysArgs+7

# Play sound if non-zero, count down and stop sound when zero
soundTimer      = zpByte()

# Former ledTimer
reserved2       = zpByte()

# Fow now the LED state machine itself is hard-coded in the program ROM
ledState_v2     = zpByte() # Current LED state
ledTempo        = zpByte() # Next value for ledTimer after LED state change


if WITH_128K_BOARD:
  ctrlBitsVideo = reserved1
  ctrlBitsCopy  = reserved2


# Management of free space in page zero (userVars)
# * Programs that only use the features of ROMvx can
#   safely use all bytes above userVars_vx except 0x80.
# * Programs that use some but not all features of ROMvx
#   may exceptionally use bytes between userVars
#   and userVars_vx if they avoid using ROM features
#   that need them. This is considerably riskier.
userVars        = zpByte(0)

# Start of safely usable bytes under ROMv4
userVars_v4     = zpByte(0)
vIrqSave        = zpByte(5)  # saved vcpu context during virq
vTmp0           = zpByte(1)  # scratch register used by v7 ops
# Start of safely usable bytes under ROMv5
userVars_v5     = zpByte(0)
# Start of safely usable bytes under ROMv6
userVars_v6     = zpByte(0)
# Start of safely usable bytes under ROMv7
userVars_v7     = zpByte(0)

# [0x80]
# Constant 0x01.
zpReset(0x80)
oneConst        = zpByte(1)
userVars2       = zpByte(0)

# Warning: One should avoid using SYS_ExpanderControl
# under ROMv4 overwrites becauses it overwrites 0x81.


#-----------------------------------------------------------------------
#
#  RAM page 1: video line table
#
#-----------------------------------------------------------------------

# Byte 0-239 define the video lines
videoTable      = 0x0100 # Indirection table: Y[0] dX[0]  ..., Y[119] dX[119]

vReset          = 0x01f0
ledTimer        = 0x01f2 # (displaced) Ticks until next LED change
entropy2        = 0x01f3 # (displaced) Entropy hidden state
reserved4       = 0x01f4
reserved5       = 0x01f5
vIRQ_v5         = 0x01f6
ctrlBits        = 0x01f8
videoTop_v5     = 0x01f9 # Number of skip lines

# Highest bytes are for sound channel variables
wavA = 250      # Waveform modulation with `adda'
wavX = 251      # Waveform modulation with `xora'
keyL = 252      # Frequency low 7 bits (bit7 == 0)
keyH = 253      # Frequency high 8 bits
oscL = 254      # Phase low 7 bits
oscH = 255      # Phase high 8 bits

#-----------------------------------------------------------------------
#  Memory layout
#-----------------------------------------------------------------------

userCode = 0x0200       # Application vCPU code
soundTable = 0x0700     # Wave form tables (doubles as right-shift-2 table)
screenMemory = 0x0800   # Default start of screen memory: 0x0800 to 0x7fff

#-----------------------------------------------------------------------
#  Application definitions
#-----------------------------------------------------------------------

maxTicks = 30//2                # Duration of vCPU's slowest virtual opcode (ticks)
minTicks = 14//2                # vcPU's fastest instruction
v6502_maxTicks = 38//2          # Max duration of v6502 processing phase (ticks)

runVcpu_overhead = 5            # Caller overhead (cycles)
vCPU_overhead = 9               # Callee overhead of jumping in and out (cycles)
v6502_overhead = 11             # Callee overhead for v6502 (cycles)

v6502_adjust = (v6502_maxTicks - maxTicks) + (v6502_overhead - vCPU_overhead)//2
assert v6502_adjust >= 0        # v6502's overhead is a bit more than vCPU

def runVcpu(n, ref=None, returnTo=None):
  """Macro to run interpreter for exactly n cycles. Returns 0 in AC.

  - `n' is the number of available Gigatron cycles including overhead.
    This is converted into interpreter ticks and takes into account
    the vCPU calling overheads. A `nop' is inserted when necessary
    for alignment between cycles and ticks.
  - `returnTo' is where program flow continues after return. If not set
     explicitely, it will be the first instruction behind the expansion.
  - If another interpreter than vCPU is active (v6502...), that one
    must adjust for the timing differences, because runVcpu wouldn't know."""

  overhead = runVcpu_overhead + vCPU_overhead
  if returnTo == 0x100:         # Special case for videoZ
    overhead -= 2

  if n is None:
    # (Clumsily) create a maximum time slice, corresponding to a vTicks
    # value of 127 (giving 282 cycles). A higher value doesn't work because
    # then SYS functions that just need 28 cycles (0 excess) won't start.
    n = (127 + maxTicks) * 2 + overhead

  n -= overhead
  assert n > 0
  m = n % 2                     # Need alignment?
  n //= 2
  n -= maxTicks                 # First instruction always runs
  assert n < 128
  assert n >= v6502_adjust

  print('runVcpu at $%04x net cycles %3s info %s' % (pc(), n, ref))

  ld([vCpuSelect],Y)            #0 Allows us to use ctrl() just before runVcpu
  if m == 1: nop()              #1 Tick alignment
  if returnTo != 0x100:
    if returnTo is None:
      returnTo = pc() + 4       # Next instruction
    ld(lo(returnTo))            #1
    st([vReturn])               #2
  jmp(Y,'ENTER')                #3
  ld(n)                         #4
assert runVcpu_overhead ==       5

#-----------------------------------------------------------------------
#       v6502 definitions
#-----------------------------------------------------------------------

# Registers are zero page variables
v6502_PC        = vLR           # Program Counter
v6502_PCL       = vLR+0         # Program Counter Low
v6502_PCH       = vLR+1         # Program Counter High
v6502_S         = vSP           # Stack Pointer (kept as "S+1")
v6502_A         = vAC+0         # Accumulator
v6502_BI        = vAC+1         # B Input Register (used by SBC)
v6502_ADL       = sysArgs+0     # Low Address Register
v6502_ADH       = sysArgs+1     # High Address Register
v6502_IR        = sysArgs+2     # Instruction Register
v6502_P         = sysArgs+3     # Processor Status Register (V flag in bit 7)
v6502_Qz        = sysArgs+4     # Quick Status Register for Z flag
v6502_Qn        = sysArgs+5     # Quick Status Register for N flag
v6502_X         = sysArgs+6     # Index Register X
v6502_Y         = sysArgs+7     # Index Register Y
v6502_Tmp       = vTmp          # Scratch (may be clobbered outside v6502)

# MOS 6502 definitions for P register
v6502_Cflag = 1                 # Carry Flag (unsigned overflow)
v6502_Zflag = 2                 # Zero Flag (all bits zero)
v6502_Iflag = 4                 # Interrupt Enable Flag (1=Disable)
v6502_Dflag = 8                 # Decimal Enable Flag (aka BCD mode, 1=Enable)
v6502_Bflag = 16                # Break (or PHP) Instruction Flag
v6502_Uflag = 32                # Unused (always 1)
v6502_Vflag = 64                # Overflow Flag (signed overflow)
v6502_Nflag = 128               # Negative Flag (bit 7 of result)

# In emulation it is much faster to keep the V flag in bit 7
# This can be corrected when importing/exporting with PHP, PLP, etc
v6502_Vemu = 128

# On overflow:
#       """Overflow is set if two inputs with the same sign produce
#          a result with a different sign. Otherwise it is clear."""
# Formula (without carry/borrow in!):
#       (A ^ (A+B)) & (B ^ (A+B)) & 0x80
# References:
#       http://www.righto.com/2012/12/the-6502-overflow-flag-explained.html
#       http://6502.org/tutorials/vflag.html

# Memory layout
v6502_Stack     = 0x0000        # 0x0100 is already used in the Gigatron
#v6502_NMI      = 0xfffa
#v6502_RESET    = 0xfffc
#v6502_IRQ      = 0xfffe

#-----------------------------------------------------------------------
#
#  $0000 ROM page 0: Boot
#
#-----------------------------------------------------------------------

align(0x100, size=0x80)

# Give a first sign of life that can be checked with a voltmeter
ld(0b0000)                      # LEDs |OOOO|
ld(syncBits^hSync,OUT)          # Prepare XOUT update, hSync goes down, RGB to black
ld(syncBits,OUT)                # hSync goes up, updating XOUT

# Setup I/O and RAM expander
ctrl(0b01111111)                # Reset signal (default state | 0x3)
ctrl(0b01111100)                # Disable SPI slaves, enable RAM, bank 1
#      ^^^^^^^^
#      |||||||`-- SCLK
#      ||||||`--- Not connected
#      |||||`---- /SS0
#      ||||`----- /SS1
#      |||`------ /SS2
#      ||`------- /SS3
#      |`-------- B0
#      `--------- B1
# bit15 --------- MOSI = 0

if WITH_128K_BOARD:
  ld(0x7c)
  st([ctrlBitsVideo])
  st([ctrlBitsCopy])

# Simple RAM test and size check by writing to [1<<n] and see if [0] changes or not.
ld(1)                           # Quick RAM test and count
label('.countMem0')
st([memSize],Y)                 # Store in RAM and load AC in Y
ld(255)
xora([Y,0])                     # Invert value from memory
st([Y,0])                       # Test RAM by writing the new value
st([0])                         # Copy result in [0]
xora([Y,0])                     # Read back and compare if written ok
bne(pc())                       # Loop forever on RAM failure here
ld(255)
xora([Y,0])                     # Invert memory value again
st([Y,0])                       # To restore original value
xora([0])                       # Compare with inverted copy
beq('.countMem1')               # If equal, we wrapped around
ld([memSize])
bra('.countMem0')               # Loop to test next address line
adda(AC)                        # Executes in the branch delay slot!
label('.countMem1')

# Momentarily wait to allow for debouncing of the reset switch by spinning
# roughly 2^15 times at 2 clocks per loop: 6.5ms@10MHz to 10ms@6.3MHz
# Real-world switches normally bounce shorter than that.
# "[...] 16 switches exhibited an average 1557 usec of bouncing, with,
#  as I said, a max of 6200 usec" (From: http://www.ganssle.com/debouncing.htm)
# Relevant for the breadboard version, as the kit doesn't have a reset switch.

ld(255)                         # Debounce reset button
label('.debounce')
st([0])
bne(pc())
suba(1)                         # Branch delay slot
ld([0])
bne('.debounce')
suba(1)                         # Branch delay slot

# Update LEDs (memory is present and counted, reset is stable)
ld(0b0001)                      # LEDs |*OOO|
ld(syncBits^hSync,OUT)
ld(syncBits,OUT)

# Scan the entire RAM space to collect entropy for a random number generator.
# The 16-bit address space is scanned, even if less RAM was detected.
ld(0)                           # Collect entropy from RAM
st([vAC+0],X)
st([vAC+1],Y)
label('.initEnt0')
ld([entropy+0])
bpl('.initEnt1')
adda([Y,X])
xora(191)
label('.initEnt1')
st([entropy+0])
ld([entropy+1])
bpl('.initEnt2')
adda([entropy+0])
xora(193)
label('.initEnt2')
st([entropy+1])
ld(1,Y)
adda([Y,entropy2])
st([Y,entropy2])
ld([vAC+1],Y)
ld([vAC+0])
adda(1)
bne('.initEnt0')
st([vAC+0],X)
ld([vAC+1])
adda(1)
bne('.initEnt0')
st([vAC+1],Y)

# Update LEDs
ld(0b0011)                      # LEDs |**OO|
ld(syncBits^hSync,OUT)
ld(syncBits,OUT)

# vCPU reset handler
ld((vReset&255)-2)              # Setup vCPU reset handler
st([vPC])
adda(2,X)
ld(vReset>>8)
st([vPC+1],Y)
st(0x35,              [Y,Xpp])  # vReset
st(lo('RESET_v7'),    [Y,Xpp])
ld(vIRQ_v5 & 0xff, X)
st(0,                 [Y,Xpp])  # vIRQ_v5: Disable interrupts
st(0,                 [Y,Xpp])  # vIRQ_v5
st(0b01111100,        [Y,Xpp])  # Control register
st(0,                 [Y,Xpp])  # videoTop

ld(hi('ENTER'))                 # Active interpreter (vCPU,v6502) = vCPU
st([vCpuSelect])

ld(255)                         # Setup serial input
st([frameCount])
st([serialRaw])
st([serialLast])
st([buttonState])
st([resetTimer])                # resetTimer<0 when entering Main.gcl

ld(0b0111)                      # LEDs |***O|
ld(syncBits^hSync,OUT)
ld(syncBits,OUT)

ld(0)
st([0])                         # Carry lookup ([0x80] in 1st line of vBlank)
st([channel])
st([soundTimer])

ld(0b1111)                      # LEDs |****|
ld(syncBits^hSync,OUT)
ld(syncBits,OUT)
st([xout])                      # Setup for control by video loop
st([xoutMask])

ld(hi('startVideo'),Y)          # Enter video loop at vertical blank
jmp(Y,'startVideo')
st([ledState_v2])               # Setting to 1..126 means "stopped"

#-----------------------------------------------------------------------
# Soft reset
#-----------------------------------------------------------------------

# Resets the gigatron without breaking the video loop.
# This mostly consists of executing Reset.gt1.
#
# This used to be achieved with a SYS_Reset_88 that was removed
# from interface.json for ROMv5a in order to prefer achieving this
# by jumping to vReset. Instead of a SYS call, this is now
# achieved by a secret vCPU instruction RESET_v7 that frees
# the [1f2-1f5] space for other purposes.

# ROM type (see also Docs/GT1-files.txt)
romTypeValue = symbol('romTypeValue_DEVROM')

label('softReset#20')
st([vSP])                       #20 vSP
nop()                           #21 Empty for vSPH
ld(hi('videoTop_v5'),Y)         #22
st([Y,lo('videoTop_v5')])       #23 Show all 120 pixel lines
st([Y,vIRQ_v5])                 #24 Disable vIRQ dispatch
st([Y,vIRQ_v5+1])               #25
st([soundTimer])                #26 soundTimer
st([vLR])                       #27 vLR
st([vLR+1])                     #28
# set videoMode
if WITH_512K_BOARD:
  st([videoModeC])              #29
  ld('nopixels')                #30
else:
  ld('nopixels')                #29
  st([videoModeC])              #30
st([videoModeB])                #31
st([videoModeD])                #32
# Set romTypeValue
assert (romTypeValue & 7) == 0
ld(romTypeValue)                #33 Set ROM type/version and clear channel mask
st([romType])                   #34
# Reset expansion board
ctrl(0b01111111)                #35 Reset signal (default state | 0x3)
ctrl(0b01111100)                #36 Default state.
ld([vTmp])                      #37 Always load after ctrl
if WITH_128K_BOARD:
  ld(0x7c)                      #38
  st([ctrlBitsVideo])           #39
  st([ctrlBitsCopy])            #40
  ld(-32/2)                     #41-32=9
else:
  nop()                         #38 adjust vticks
  ld(-30/2)                     #39-30=9
# Exec Reset.gt1
adda([vTicks])                  #10
st([vTicks])                    #11
ld('Reset')                     #12 Reset.gt1 from EPROM
st([sysArgs+0])                 #13
ld(hi('Reset'))                 #14
ld(hi('sys_Exec'),Y)            #15
jmp(Y,'sys_Exec')               #16
st([sysArgs+1])                 #17


#-----------------------------------------------------------------------
# Placeholders for future SYS functions. This works as a kind of jump
# table. The indirection allows SYS implementations to be moved around
# between ROM versions, at the expense of 2 clock cycles (or 1). When
# the function is not present it just acts as a NOP. Of course, when a
# SYS function must be patched or extended it needs to have budget for
# that in its declared maximum cycle count.
#
# Technically the same goal can be achieved by starting each function
# with 2 nop's, or by overdeclaring their duration in the first place
# (a bit is still wise to do). But this can result in fragmentation
# of future ROM images. The indirection avoids that.
#
# An added advantage of having these in ROM page 0 is that it saves one
# byte when setting sysFn: LDI+STW (4 bytes) instead of LDWI+STW (5 bytes)
#-----------------------------------------------------------------------

align(0x80, size=0x80)
assert pc() == 0x80

ld(hi('REENTER'),Y)             #15 slot 0x80
jmp(Y,'REENTER')                #16
ld(-20/2)                       #17

ld(hi('REENTER'),Y)             #15 slot 0x83
jmp(Y,'REENTER')                #16
ld(-20/2)                       #17

ld(hi('REENTER'),Y)             #15 slot 0x86
jmp(Y,'REENTER')                #16
ld(-20/2)                       #17

ld(hi('REENTER'),Y)             #15 slot 0x89
jmp(Y,'REENTER')                #16
ld(-20/2)                       #17

ld(hi('REENTER'),Y)             #15 slot 0x8c
jmp(Y,'REENTER')                #16
ld(-20/2)                       #17

ld(hi('REENTER'),Y)             #15 slot 0x8f
jmp(Y,'REENTER')                #16
ld(-20/2)                       #17

ld(hi('REENTER'),Y)             #15 slot 0x92
jmp(Y,'REENTER')                #16
ld(-20/2)                       #17

ld(hi('REENTER'),Y)             #15 slot 0x95
jmp(Y,'REENTER')                #16
ld(-20/2)                       #17

ld(hi('REENTER'),Y)             #15 slot 0x98
jmp(Y,'REENTER')                #16
ld(-20/2)                       #17

ld(hi('REENTER'),Y)             #15 slot 0x9b
jmp(Y,'REENTER')                #16
ld(-20/2)                       #17

#-----------------------------------------------------------------------
# Extension SYS_Multiply_s16_v6_66: 16 bit multiplication
# Also known as SYS_Multiply_s16_v7_34.
#-----------------------------------------------------------------------
#
# Computes C = C + A * B where A,B,C are 16 bits integers.
# Returns product in vAC as well
#
#       sysArgs[0:1]    Multiplicand A (in)
#       sysArgs[2:3]    Multiplicand B (in)
#       sysArgs[4:5]    C (inout)
#       sysArgs[6:7]    (changed)
#
# Original design: at67

label('SYS_Multiply_s16_v6_66')
label('SYS_Multiply_s16_v7_34')
ld(hi('sys_Multiply_s16'),Y)    #15 slot 0x9e
jmp(Y,'sys_Multiply_s16')       #16
nop()

#-----------------------------------------------------------------------
# Extension SYS_Divide_s16_v6_80: 15 bit division
# Also known as SYS_Divide_s16_v7_34
#-----------------------------------------------------------------------
#
# Computes the Euclidean division of 0<=A<65536 and 0<B<65536.
# An external wrapper is needed to handle signed division.
# Returns product in vAC as well as sysArgs[01]
# Returns remainder in sysArgs[45]
#
#       sysArgs[0:1]    Dividend A (in) Quotient (out)
#       sysArgs[2:3]    Divisor B (in)
#       sysArgs[4:5]    Remainder (out)
#       sysArgs[6:7]    (changed)
#
# Original design by at67.
# Improved for unrestricted unsigned division

label('SYS_Divide_s16_v6_80')
label('SYS_Divide_u16_v7_34')
ld(hi('sys_Divide_u16'),Y)      #15 slot 0xa1
jmp(Y,'sys_Divide_u16')         #16
nop()

#-----------------------------------------------------------------------
# More placeholders for future SYS functions
#-----------------------------------------------------------------------

ld(hi('REENTER'),Y)             #15 slot 0xa4
jmp(Y,'REENTER')                #16
ld(-20/2)                       #17

ld(hi('REENTER'),Y)             #15 slot 0xa7
jmp(Y,'REENTER')                #16
ld(-20/2)                       #17

ld(hi('REENTER'),Y)             #15 slot 0xaa
jmp(Y,'REENTER')                #16
ld(-20/2)                       #17

#-----------------------------------------------------------------------
# Extension SYS_Exec_88: Load code from ROM into memory and execute it
#-----------------------------------------------------------------------
#
# This loads the vCPU code with consideration of the current vSP
# Used during reset, but also for switching between applications or for
# loading data from ROM from within an application (overlays).
#
# ROM stream format is
#  [<addrH> <addrL> <n&255> n*<byte>]* 0 [<execH> <execL>]
# on top of lookup tables.
#
#       sysArgs[0:1]    ROM pointer (in)
#       sysArgs[2:3]    RAM pointer (changed) Execution address (out)
#       sysArgs[4]      Byte counter (changed)
#       sysArgs[7]      FSM state (changed)
#       vLR==0          vCPU continues at GT1 execution address (in)
#       vLR!=0          vCPU continues at vLR (in)

label('SYS_Exec_88')
ld(hi('sys_Exec'),Y)            #15
jmp(Y,'sys_Exec')               #16
nop()                           #17

#-----------------------------------------------------------------------
# Extension SYS_Loader_DEVROM_44: Load code from serial input and execute
#-----------------------------------------------------------------------
#
# This loads vCPU code and data presented on the serial port according
# to the loader protocol then jumps to the avertised execution
# address. This call never returns.
#
# Set sysArgs[0] to 0xc to updated green or red dots in the
# screen row located in page sysArgs[1]. This is automatically
# disabled if visible bytes are loaded there.
#
#       sysArgs[0]      Zero to disable echo (0x00 or ox0c) (in)
#       sysArgs[1]      Echo row (0x59) (in)
#
# Credits: The first native loader was written for ROMvX0 by at67.
#
# Loader protocol
# ---------------
# The data is divided into chunks of at most 60 bytes to be loaded at
# contiguous addresses inside a same gigatron memory page. Each chunk
# is transmitted over the serial port (IN) synchronously with the
# video signal, one chunk per frame. Each byte of the chunk must be
# read from the IN port when videoY takes specific values:
#
#  videoY    Data
#   207      protocol signature: 'L'
#   219      chunk length (low 6 bits) or zero to execute.
#   235      chunk address (l) or execution address (l) if len=0
#   251      chunk address (h) or execution address (h)  if len=0
#   2        chunk byte 0
#   6        chunk byte 1
#  ....
#   2+4*k    chunk byte k

ld(hi('sys_Loader'),Y)          #15 slot 0xb0
jmp(Y,'sys_Loader')             #16
ld([sysArgs+0])                 #17

#-----------------------------------------------------------------------
# More placeholders for future SYS functions
#-----------------------------------------------------------------------

ld(hi('REENTER'),Y)             #15 slot 0xb3
jmp(Y,'REENTER')                #16
ld(-20/2)                       #17

ld(hi('REENTER'),Y)             #15 slot 0xb6
jmp(Y,'REENTER')                #16
ld(-20/2)                       #17

ld(hi('REENTER'),Y)             #15 slot 0xb9
jmp(Y,'REENTER')                #16
ld(-20/2)                       #17

ld(hi('REENTER'),Y)             #15 slot 0xbc
jmp(Y,'REENTER')                #16
ld(-20/2)                       #17

ld(hi('REENTER'),Y)             #15 slot 0xbf
jmp(Y,'REENTER')                #16
ld(-20/2)                       #17

ld(hi('REENTER'),Y)             #15 slot 0xc2
jmp(Y,'REENTER')                #16
ld(-20/2)                       #17

ld(hi('REENTER'),Y)             #15 slot 0xc5
jmp(Y,'REENTER')                #16
ld(-20/2)                       #17

ld(hi('REENTER'),Y)             #15 slot 0xc8
jmp(Y,'REENTER')                #16
ld(-20/2)                       #17

ld(hi('REENTER'),Y)             #15 slot 0xcb
jmp(Y,'REENTER')                #16
ld(-20/2)                       #17

ld(hi('REENTER'),Y)             #15 slot 0xce
jmp(Y,'REENTER')                #16
ld(-20/2)                       #17

ld(hi('REENTER'),Y)             #15 slot 0xd1
jmp(Y,'REENTER')                #16
ld(-20/2)                       #17

ld(hi('REENTER'),Y)             #15 slot 0xd4
jmp(Y,'REENTER')                #16
ld(-20/2)                       #17

ld(hi('REENTER'),Y)             #15 slot 0xd7
jmp(Y,'REENTER')                #16
ld(-20/2)                       #17

ld(hi('REENTER'),Y)             #15 slot 0xda
jmp(Y,'REENTER')                #16
ld(-20/2)                       #17

ld(hi('REENTER'),Y)             #15 slot 0xdd
jmp(Y,'REENTER')                #16
ld(-20/2)                       #17

ld(hi('REENTER'),Y)             #15 slot 0xe0
jmp(Y,'REENTER')                #16
ld(-20/2)                       #17

#-----------------------------------------------------------------------
# Extension SYS_ScanMemoryExt_v6_50
#-----------------------------------------------------------------------

# SYS function for searching a byte in a 0 to 256 bytes string located
# in a different bank. Doesn't cross page boundaries. Returns a
# pointer to the target if found or zero. Temporarily deselects SPI
# devices.
#
# sysArgs[0:1]            Start address
# sysArgs[2], sysArgs[3]  Bytes to locate in the string
# vACL                    Length of the string (0 means 256)
# vACH                    Bit 6 and 7 contain the bank number

label('SYS_ScanMemoryExt_v6_50')
ld(hi('sys_ScanMemoryExt'),Y)   #15 slot 0xe3
jmp(Y,'sys_ScanMemoryExt')      #16
ld([vAC+1])                     #17


#-----------------------------------------------------------------------
# Extension SYS_ScanMemory_v6_50
#-----------------------------------------------------------------------

# SYS function for searching a byte in a 0 to 256 bytes string.
# Returns a pointer to the target if found or zero.  Doesn't cross
# page boundaries.
#
# sysArgs[0:1]            Start address
# sysArgs[2], sysArgs[3]  Bytes to locate in the string
# vACL                    Length of the string (0 means 256)

label('SYS_ScanMemory_v6_50')
ld(hi('sys_ScanMemory'),Y)      #15 slot 0xe6
jmp(Y,'sys_ScanMemory')         #16
ld([sysArgs+1],Y)               #17

#-----------------------------------------------------------------------
# Extension SYS_CopyMemory_v6_80
#-----------------------------------------------------------------------

# SYS function for copying 1..256 bytes
#
# sysArgs[0:1]    Destination address
# sysArgs[2:3]    Source address
# vAC[0]          Count (0 means 256)
#
# Doesn't cross page boundaries.
# Overwrites sysArgs[4:7] and vLR.

label('SYS_CopyMemory_v6_80')
ld(hi('sys_CopyMemory'),Y)       # 15 slot 0xe9
jmp(Y, 'sys_CopyMemory')         # 16
ld([vAC])                        # 17

#-----------------------------------------------------------------------
# Extension SYS_CopyMemoryExt_v6_100
#-----------------------------------------------------------------------

# SYS function for copying 1..256 bytes across banks
#
# sysArgs[0:1]  Destination address
# sysArgs[2:3]  Source address
# vAC[0]        Count (0 means 256)
# vAC[1]        Bits 7 and 6 contain the destination bank number,
#               and bits 5 and 4 the source bank number.
#
# Doesn't cross page boundaries.
# Overwrites sysArgs[4:7], vLR, and vTmp.
# Temporarily deselect all SPI devices.
# Should not call without expansion board

label('SYS_CopyMemoryExt_v6_100')
ld(hi('sys_CopyMemoryExt'),Y)    # 15 slot 0xec
jmp(Y, 'sys_CopyMemoryExt')      # 16
ld([vAC+1])                      # 17

#-----------------------------------------------------------------------
# Extension SYS_ReadRomDir_v5_80
#-----------------------------------------------------------------------

# Get next entry from ROM file system. Use vAC=0 to get the first entry.

# Variables:
#       vAC             Start address of current entry (inout)
#       sysArgs[0:7]    File name, padded with zeroes (out)

label('SYS_ReadRomDir_v5_80')
ld(hi('sys_ReadRomDir'),Y)      #15
jmp(Y,'sys_ReadRomDir')         #16
ld([vAC+1])                     #17

fillers(until=symbol('SYS_Out_22') & 255)

#-----------------------------------------------------------------------
# Extension SYS_Out_22
#-----------------------------------------------------------------------

# Send byte to output port
#
# Variables:
#       vAC

label('SYS_Out_22')
ld([sysArgs+0],OUT)             #15
nop()                           #16
ld(hi('REENTER'),Y)             #17
jmp(Y,'REENTER')                #18
ld(-22/2)                       #19

#-----------------------------------------------------------------------
# Extension SYS_In_24
#-----------------------------------------------------------------------

# Read a byte from the input port
#
# Variables:
#       vAC

label('SYS_In_24')
st(IN, [vAC])                   #15
ld(0)                           #16
st([vAC+1])                     #17
nop()                           #18
ld(hi('REENTER'),Y)             #19
jmp(Y,'REENTER')                #20
ld(-24/2)                       #21

assert pc()&255 == 0

#-----------------------------------------------------------------------
#
#  $0100 ROM page 1: Video loop vertical blank
#
#-----------------------------------------------------------------------
align(0x100, size=0x100)

# Video off mode (also no sound, serial, timer, blinkenlights, ...).
# For benchmarking purposes. This still has the overhead for the vTicks
# administration, time slice granularity etc.
label('videoZ')
videoZ = pc()
runVcpu(None, '---- novideo', returnTo=videoZ)

label('startVideo')             # (Re)start of video signal from idle state
ld(syncBits)

# Start of vertical blank interval
label('vBlankStart')
st([videoSync0])                #32 Start of vertical blank interval
ld(syncBits^hSync)              #33
st([videoSync1])                #34

# Reset line counter before vCPU can see it
ld(videoYline0)                 #35
st([videoY])                    #36

# Update frame count and [0x80] (4 cycles)
ld(1)                           #37 Reinitialize carry lookup, for robustness
st([0x80],Y)                    #38 And set Y=1 for 1fx variables
adda([frameCount])              #39 Frame counter
st([frameCount])                #40

# Mix entropy (11 cycles)
xora([entropy+1])               #41 Mix entropy
xora([serialRaw])               #42 Mix in serial input
adda([entropy+0])               #43
st([entropy+0])                 #44
adda([Y,entropy2])              #45 Some hidden state
st([Y,entropy2])                #46
bmi(pc()+3)                     #47
bra(pc()+3)                     #48
xora(64+16+2+1)                 #49
xora(64+32+8+4)                 #49(!)
adda([entropy+1])               #50
st([entropy+1])                 #51

# LED sequencer (15 cycles)
ld([Y,ledTimer])                #52 Blinkenlight sequencer
suba(1)                         #53
bne('.leds#56')                 #54
st([Y,ledTimer])                #55
ld(1)                           #56
adda([ledState_v2])             #57
label('.leds#58')
bne(pc()+3)                     #58
bra(pc()+3)                     #59
ld(-24)                         #60 State 0 becomes -24, start of sequence
bgt('.leds#62')                 #60(!) Catch the stopped state (>0)
st([ledState_v2])               #61
adda('.leds#65')                #62
bra(AC)                         #63 Jump to lookup table
bra('.leds#66')                 #64 Single-instruction subroutine
label('.leds#56')
bge('.leds#58')                 #56
ld([ledState_v2])               #57
ld([ledTempo])                  #58
st([Y,ledTimer])                #59
bra(pc()+1)                     #60
nop()                           #61,62
bra('.leds#65')                 #63
ld([xoutMask])                  #64
label('.leds#62')
ld(0xf)                         #62 Maintain stopped state
st([ledState_v2])               #63
bra('.leds#66')                 #64 
anda([xoutMask])                #65
ld(0b1111)                      #65 LEDs |****| offset -24 Low 4 bits are the LED output
ld(0b0111)                      #65 LEDs |***O|
ld(0b0011)                      #65 LEDs |**OO|
ld(0b0001)                      #65 LEDs |*OOO|
ld(0b0010)                      #65 LEDs |O*OO|
ld(0b0100)                      #65 LEDs |OO*O|
ld(0b1000)                      #65 LEDs |OOO*|
ld(0b0100)                      #65 LEDs |OO*O|
ld(0b0010)                      #65 LEDs |O*OO|
ld(0b0001)                      #65 LEDs |*OOO|
ld(0b0011)                      #65 LEDs |**OO|
ld(0b0111)                      #65 LEDs |***O|
ld(0b1111)                      #65 LEDs |****|
ld(0b1110)                      #65 LEDs |O***|
ld(0b1100)                      #65 LEDs |OO**|
ld(0b1000)                      #65 LEDs |OOO*|
ld(0b0100)                      #65 LEDs |OO*O|
ld(0b0010)                      #65 LEDs |O*OO|
ld(0b0001)                      #65 LEDs |*OOO|
ld(0b0010)                      #65 LEDs |O*OO|
ld(0b0100)                      #65 LEDs |OO*O|
ld(0b1000)                      #65 LEDs |OOO*|
ld(0b1100)                      #65 LEDs |OO**|
ld(0b1110)                      #65 LEDs |O***| offset -1
label('.leds#65')
anda(0xf)                       #65 Always clear sound bits
label('.leds#66')
st([xoutMask])                  #66 Sound bits will be re-enabled below

# Default video pulse length
ld(vPulse*2)                    #67 vPulse default length when not modulated
st([videoPulse])                #68

# When the total number of scan lines per frame is not an exact multiple of the
# (4) channels, there will be an audible discontinuity if no measure is taken.
# This static noise can be suppressed by swallowing the first `lines mod 4'
# partial samples after transitioning into vertical blank. This is easiest if
# the modulo is 0 (do nothing), 1 (reset sample when entering the last visible
# scan line), or 2 (reset sample while in the first blank scan line). For the
# last case there is no solution yet: give a warning.
extra = 0
if soundDiscontinuity == 2:
  st(sample, [sample])          # Sound continuity
  extra += 1
if soundDiscontinuity > 2:
  highlight('Warning: sound discontinuity not suppressed')

if WITH_128K_BOARD:
  # The cpu bank is enabled during vblank.
  # Rebuild ctrlBits{Video,Copy} since Y=1
  # at the cost of 4 extra cycles.
  ld([Y,ctrlBits])              #+1
  st([ctrlBitsCopy],X)          #+2
  anda(0x3c)                    #+3
  ora(0x40)                     #+4
  st([ctrlBitsVideo])           #+5
  ctrl(X)                       #+6 next must be a load
  extra += 6

# vCPU interrupt
ld([frameCount])                #69
beq('vBlankFirst#72')           #70

runVcpu(190-71-extra,           #71 Application cycles (scan line 0)
    '---D line 0 no timeout',
    returnTo='vBlankFirst#190')

label('vBlankFirst#72')
ld(hi('vBlankFirst#75'),Y)      #72
jmp(Y,'vBlankFirst#75')         #73
ld(hi(vIRQ_v5),Y)               #74

label('vBlankFirst#190')

# Mitigation for rogue channelMask (3 cycles)
ld([channelMask])               #190 Normalize channelMask, for robustness
anda(0b11111011)                #191
st([channelMask])               #192
# Sound timer
ld([soundTimer])                #193
bne('.sound00')                 #194
suba(1)                         #195
bra('.sound01')                 #196
ld(0)                           #197
label('.sound00')
st([soundTimer])                #196
ld(0xf0)                        #197
label('.sound01')
ora([xoutMask])                 #198
st([xoutMask])                  #199

# New scan line 
ld([videoSync0],OUT)            #0 <New scan line start>
label('sound1')
ld([channel])                   #1 Advance to next sound channel
anda([channelMask])             #2
adda(1)                         #3
ld([videoSync1],OUT)            #4 Start horizontal pulse
st([channel],Y)                 #5
ld(0x7f)                        #6 Update sound channel
anda([Y,oscL])                  #7
adda([Y,keyL])                  #8
st([Y,oscL])                    #9
anda(0x80,X)                    #10
ld([X])                         #11
adda([Y,oscH])                  #12
adda([Y,keyH])                  #13
st([Y,oscH])                    #14
anda(0xfc)                      #15
xora([Y,wavX])                  #16
ld(AC,X)                        #17
ld([Y,wavA])                    #18
ld(soundTable>>8,Y)             #19
adda([Y,X])                     #20
bmi(pc()+3)                     #21
bra(pc()+3)                     #22
anda(63)                        #23
ld(63)                          #23(!)
adda([sample])                  #24
st([sample])                    #25

ld([xout])                      #26 Gets copied to XOUT
ld(hi('vBlankLast#34'),Y)       #27 Prepare jumping out of page in last line
ld([videoSync0],OUT)            #28 End horizontal pulse

# Count through the vertical blank interval until its last scan line
ld([videoY])                    #29
bpl('.vBlankLast#32')           #30
adda(2)                         #31
st([videoY])                    #32

# Determine if we're in the vertical sync pulse
suba(1-2*(vBack+vPulse-1))      #33 Prepare sync values
bne('.prepSync36')              #34 Tests for start of vPulse
suba([videoPulse])              #35
ld(syncBits^vSync)              #36 Entering vertical sync pulse
bra('.prepSync39')              #37
st([videoSync0])                #38
label('.prepSync36')
bne('.prepSync38')              #36 Tests for end of vPulse
ld(syncBits)                    #37
bra('.prepSync40')              #38 Entering vertical back porch
st([videoSync0])                #39
label('.prepSync38')
ld([videoSync0])                #38 Load current value
label('.prepSync39')
nop()                           #39
label('.prepSync40')
xora(hSync)                     #40 Precompute, as during the pulse there is no time
st([videoSync1])                #41

# Capture the serial input before the '595 shifts it out
ld([videoY])                    #42 Capture serial input
xora(1-2*(vBack-1-1))           #43 Exactly when the 74HC595 has captured all 8 controller bits
bne(pc()+3)                     #44
bra(pc()+3)                     #45
st(IN, [serialRaw])             #46
st(0,[0])                       #46(!) Reinitialize carry lookup, for robustness

# Update [xout] with the next sound sample every 4 scan lines.
# Keep doing this on 'videoC equivalent' scan lines in vertical blank.
ld([videoY])                    #47
anda(6)                         #48
beq('vBlankSample')             #49
if not WITH_512K_BOARD:
  ld([sample])                    #50
else:
  ld([sample],Y)                  #50

label('vBlankNormal')
runVcpu(199-51,                 #51 Application cycles (vBlank scan lines without sound sample update)
        'AB-D line 1-36')
bra('sound1')                   #199
ld([videoSync0],OUT)            #0 <New scan line start>

label('vBlankSample')
if not WITH_512K_BOARD:
  ora(0x0f)                       #51 New sound sample is ready
  anda([xoutMask])                #52
  st([xout])                      #53
  st(sample, [sample])            #54 Reset for next sample
  runVcpu(199-55,                 #55 Application cycles (vBlank scan lines with sound sample update)
          '--C- line 3-39')
else:
  ld([xoutMask])                  #51
  bmi(pc()+3)                     #52
  bra(pc()+3)                     #53
  nop()                           #54
  ctrl(Y,0xD0)                    #54 instead of #43 (wrong by ~2us)
  ld([sample])                    #55
  ora(0x0f)                       #56 New sound sample is ready
  anda([xoutMask])                #57
  st([xout])                      #58
  st(sample, [sample])            #59 Reset for next sample
  runVcpu(199-60,                 #60 Application cycles (vBlank scan lines with sound sample update)
          '--C- line 3-39')

bra('sound1')                   #199
ld([videoSync0],OUT)            #0 <New scan line start>

#-----------------------------------------------------------------------

label('.vBlankLast#32')
jmp(Y,'vBlankLast#34')          #32 Jump out of page for space reasons
#assert hi(controllerType) == hi(pc()) # Assume these share the high address
ld(hi(pc()),Y)                  #33

label('vBlankLast#52')

# Respond to reset button (14 cycles)
# - ResetTimer decrements as long as just [Start] is pressed down
# - Reaching 0 (normal) or 128 (extended) triggers the soft reset sequence
# - Initial value is 128 (or 255 at boot), first decrement, then check
# - This starts vReset -> SYS_Reset_88 -> SYS_Exec_88 -> Reset.gcl -> Main.gcl
# - Main.gcl then recognizes extended presses if resetTimer is 0..127 ("paasei")
# - This requires a full cycle (4s) in the warm boot scenario
# - Or a half cycle (2s) when pressing [Select] down during hard reset
# - This furthermore requires >=1 frame (and <=128) to have passed between
#   reaching 128 and getting through Reset and the start of Main, while [Start]
#   was still pressed so the count reaches <128. Two reasonable expectations.
# - The unintended power-up scenarios of ROMv1 (pulling SER_DATA low, or
#   pressing [Select] together with another button) now don't trigger anymore.

ld([buttonState])               #52 Check [Start] for soft reset
xora(~buttonStart)              #53
bne('.restart#56')              #54
ld([resetTimer])                #55 As long as button pressed
suba(1)                         #56 ... count down the timer
st([resetTimer])                #57
anda(127)                       #58
beq('.restart#61')              #59 Reset at 0 (normal 2s) or 128 (extended 4s)
ld((vReset&255)-2)              #60 Start force reset when hitting 0
bra('.restart#63')              #61 ... otherwise do nothing yet
bra('.restart#64')              #62
label('.restart#56')
wait(62-56)                     #56
ld(128)                         #62 Not pressed, reset the timer
st([resetTimer])                #63
label('.restart#64')
bra('.restart#66')              #64
label('.restart#63')
nop()                           #63,65
label('.restart#61')
st([vPC])                       #61 Point vPC at vReset
ld(vReset>>8)                   #62
st([vPC+1])                     #63
ld(hi('ENTER'))                 #64 Set active interpreter to vCPU
st([vCpuSelect])                #65
label('.restart#66')

# Switch video mode when (only) select is pressed (16 cycles)
# XXX We could make this a vCPU interrupt
ld([buttonState])               #66 Check [Select] to switch modes
xora(~buttonSelect)             #67 Only trigger when just [Select] is pressed
bne('.select#70')               #68

if not WITH_512K_BOARD:
  ld([videoModeC])              #69
  bmi('.select#72')             #70 Branch when line C is off
  ld([videoModeB])              #71 Rotate: Off->D->B->C
  st([videoModeC])              #72
  ld([videoModeD])              #73
  st([videoModeB])              #74
  bra('.select#77')             #75
  label('.select#72')
  ld('nopixels')                #72,76
  ld('pixels')                  #73 Reset: On->D->B->C
  st([videoModeC])              #74
  st([videoModeB])              #75
  nop()                         #76
  label('.select#77')
  st([videoModeD])              #77
else:
  ld([videoModeB])              #69
  xora('nopixels')              #70
  beq('.select#73')             #71
  ld([videoModeD])              #72
  st([videoModeB])              #73
  bra('.select#76')             #74
  ld('nopixels')                #75
  label('.select#73')
  ld('pixels')                  #73
  st([videoModeB])              #74
  nop()                         #75
  label('.select#76')
  st([videoModeD])              #76
  nop()                         #77

ld(255)                         #78
st([buttonState])               #79

if not WITH_128K_BOARD:

  runVcpu(189-80,               #80
          '---D line 40 select',
          returnTo='vBlankEnd#189')
  label('.select#70')
  runVcpu(189-70,               #70
          '---D line 40 no select',
          returnTo='vBlankEnd#189')
  # This must end in 0x1fe and continue
  # with the video loop entry point at 0x1ff
  fillers(until=0xf3)
  label('vBlankEnd#189')
  ld(videoTop_v5>>8,Y)          #189
  ld([Y,videoTop_v5])           #190
  st([videoY])                  #191
  st([frameX])                  #192
  bne(pc()+3)                   #193
  bra(pc()+3)                   #194
  ld('videoA')                  #195
  ld('videoF')                  #195(!)
  st([nextVideo])               #196
  ld([channel])                 #197 Normalize channel for robustness
  anda(0b00000011)              #198
  st([channel])                 #199

else: # WITH_128K_BOARD

  runVcpu(188-80,               #80
          '---D line 40 select',
          returnTo='vBlankEnd#188')
  label('.select#70')
  runVcpu(188-70,               #70
          '---D line 40 no select',
          returnTo='vBlankEnd#188')
  fillers(until=0xf2)
  # Since the entry point is in 0x1fe/#199
  # we have to shift all this by one byte/cycle.
  label('vBlankEnd#188')
  ld(videoTop_v5>>8,Y)          #188
  ld([Y,videoTop_v5])           #189
  st([videoY])                  #190
  st([frameX])                  #191
  bne(pc()+3)                   #192
  bra(pc()+3)                   #193
  ld('videoA')                  #194
  ld('videoF')                  #194(!)
  st([nextVideo])               #195
  ld([channel])                 #196 Normalize channel for robustness
  anda(0b00000011)              #197
  st([channel])                 #198


#-----------------------------------------------------------------------
#
#  $0200 ROM page 2: Video loop visible scanlines
#
#-----------------------------------------------------------------------



if WITH_512K_BOARD:
  assert pc() == 0x1ff            # Enables runVcpu() to re-enter into the next page
  ld(syncBits,OUT)                #200,0 <New scan line start>
  align(0x100, size=0x100)

  # Front porch
  anda([channelMask])             #1 AC is [channel] already!
  adda(1)                         #2
  st([channel],Y)                 #3
  ld(syncBits^hSync,OUT)          #4 Start horizontal pulse (4)

  # Horizontal sync and sound channel update for scanlines outside vBlank
  label('sound2')
  ld(0x7f)                        #5
  anda([Y,oscL])                  #6
  adda([Y,keyL])                  #7
  st([Y,oscL])                    #8
  anda(0x80,X)                    #9
  ld([X])                         #10
  adda([Y,oscH])                  #11
  adda([Y,keyH])                  #12
  st([Y,oscH] )                   #13
  anda(0xfc)                      #14
  xora([Y,wavX])                  #15
  ld(AC,X)                        #16
  ld([Y,wavA])                    #17
  ld(soundTable>>8,Y)             #18
  adda([Y,X])                     #19
  bmi(pc()+3)                     #20
  bra(pc()+3)                     #21
  anda(63)                        #22
  ld(63)                          #22(!)
  adda([sample])                  #23
  st([sample])                    #24
  ld([xout])                      #25 Gets copied to XOUT
  ld(videoTable>>8,Y)             #26 Make Y=1 for all videoABC routines!
  bra([nextVideo])                #27
  ld(syncBits,OUT)                #28 End horizontal pulse

  # Back porch A: first of 4 repeated scan lines
  # - Fetch next Yi and store it for retrieval in the next scan lines
  # - Calculate Xi from dXi and store it as well thanks to a saved cycle.
  label('videoA')
  ld('videoB')                    #29 1st scanline of 4 (always visible)
  st([nextVideo])                 #30
  ld([videoY],X)                  #31
  ld([Y,X])                       #32 Y is already 1
  st([Y,Xpp])                     #33 Just X++
  st([frameY])                    #34
  ld([Y,X])                       #35
  adda([frameX])                  #36
  st([frameX],X)                  #37 I am sure Marcel sought to do this (LB)
  ld([frameY],Y)                  #38
  ld(syncBits)                    #39
  ora([Y,Xpp],OUT)                #40 begin of pixel burst
  runVcpu(200-41,                 #41
          'A--- line 40-520',
          returnTo=0x1ff )

  # Back porch B: second of 4 repeated scan lines
  # - Process double vres
  label('videoB')
  ld('videoC')                    #29
  st([nextVideo])                 #30
  ld([frameY],Y)                  #31
  ld([videoModeC])                #32 New role for videoModeC
  anda(1)                         #33
  adda([frameY])                  #34
  st([frameY])                    #35
  ld([frameX],X)                  #36
  ld(syncBits)                    #37
  bra([videoModeB])               #38
  bra(pc()+2)                     #39
  nop()                           #40 'pixels' or 'nopixels'
  runVcpu(200-41,                 #41
          '-B-- line 40-520',
          returnTo=0x1ff )

  # Back porch C: third of 4 repeated scan lines
  # - Nothing new to for video do as Yi and Xi are known,
  # - This is the time to emit and reset the next sound sample
  label('videoC')
  ld('videoD')                    #29 3rd scanline of 4
  st([nextVideo])                 #30
  ld([sample])                    #31 New sound sample is ready (didn't fit in audio loop)
  ora(0x0f)                       #32
  anda([xoutMask])                #33
  st([xout])                      #34 Update [xout] with new sample (4 channels just updated)
  ld([frameX],X)                  #35
  ld([xoutMask])                  #36
  bmi('videoC#39')                #37
  ld([frameY],Y)                  #38
  ld(syncBits)                    #39
  ora([Y,Xpp], OUT)               #40 Always outputs pixels on C lines
  runVcpu(200-41,                 #41
          '-B-- line 40-520 no sound',
          returnTo=0x1ff )
  label('videoC#39')
  ld(syncBits)                    #39
  ora([Y,Xpp], OUT)               #40 Always outputs pixels on C lines
  ld([sample],Y)                  #41
  st(sample, [sample])            #42 Reset for next sample
  ctrl(Y,0xD0);                   #43 Forward audio to PWM (only when audio is active)
  runVcpu(200-44,                 #44
          '--C- line 40-520 sound forwarding',
        returnTo=0x1ff )

  # Back porch D: last of 4 repeated scan lines
  # - Calculate the next frame index
  # - Decide if this is the last line or not
  label('videoD')                 # Default video mode
  ld([frameX], X)                 #29 4th scanline of 4
  ld([videoY])                    #30
  suba((120-1)*2)                 #31
  beq('.lastpixels#34')           #32
  adda(120*2)                     #33 More pixel lines to go
  st([videoY])                    #34
  nop()                           #35
  ld([frameY],Y)                  #36
  ld(syncBits)                    #37
  bra([videoModeD])               #38
  bra(pc()+2)                     #39
  nop()                           #40 'pixels' or 'nopixels'
  nop()                           #41
  ld('videoA')                    #42
  label('videoD#43')
  st([nextVideo])                 #43
  runVcpu(200-44,                 #44
          '---D line 40-520',
          returnTo=0x1ff )

  label('.lastpixels#34')
  if soundDiscontinuity == 1:
    st(sample, [sample])          #34 Sound continuity
  else:
    nop()                         #34
  ld([frameY],Y)                  #35
  ld(syncBits)                    #36
  nop()                           #37
  bra([videoModeD])               #38
  bra(pc()+2)                     #39
  nop()                           #40 'pixels' or 'nopixels'
  bra('videoD#43')                #41
  ld('videoE')                    #42 no more scanlines

  # Back porch "E": after the last line
  # - Go back and and enter vertical blank (program page 2)
  label('videoE') # Exit visible area
  ld(hi('vBlankStart'),Y)         #29 Return to vertical blank interval
  jmp(Y,'vBlankStart')            #30
  ld(syncBits)                    #31

  # Video mode that blacks out one or more pixel lines from the top of screen.
  # This yields some speed, but also frees up screen memory for other purposes.
  # Note: Sound output becomes choppier the more pixel lines are skipped
  # Note: The vertical blank driver leaves 0x80 behind in [videoSync1]
  label('videoF')
  ld([videoSync1])                #29 Completely black pixel line
  adda(0x80)                      #30
  st([videoSync1],X)              #31
  ld([frameX])                    #32
  suba([X])                       #33 Decrements every two VGA scanlines
  beq('.videoF#36')               #34
  st([frameX])                    #35
  bra('.videoF#38')               #36
  label('.videoF#36')
  ld('videoA')                    #36,37 Transfer to visible screen area
  st([nextVideo])                 #37
  label('.videoF#38')
  runVcpu(200-38,                 #38
          'ABCD line 40-520 (videoF)',
          returnTo=0x1ff )

  fillers(until=0xfc);
  label('pixels')
  ora([Y,Xpp],OUT)                #40
  label('nopixels')
  nop()                           #40


elif WITH_128K_BOARD:

  assert pc() == 0x1fe
  ld([ctrlBitsVideo],X)           #199
  bra('sound3')                   #200,0 <New scan line start>
  align(0x100, size=0x100)
  ctrl(X)                         #1 Reset banking to page1.

  # Back porch A: first of 4 repeated scan lines
  # - Fetch next Yi and store it for retrieval in the next scan lines
  # - Calculate Xi from dXi, but there is no cycle time left to store it as well
  label('videoA')
  ld('videoB')                    #29 1st scanline of 4 (always visible)
  st([nextVideo])                 #30
  ld(videoTable>>8,Y)             #31
  ld([videoY],X)                  #32
  ld([Y,X])                       #33
  st([Y,Xpp])                     #34 Just X++
  st([frameY])                    #35
  ld([Y,X])                       #36
  adda([frameX],X)                #37
  label('pixels')
  ld([frameY],Y)                  #38
  ld(syncBits)                    #39

  # Stream 160 pixels from memory location <Yi,Xi> onwards
  # Superimpose the sync signal bits to be robust against misprogramming
  for i in range(qqVgaWidth):
    ora([Y,Xpp],OUT)              #40-199 Pixel burst
  ld(syncBits,OUT)                #0 <New scan line start> Back to black

  # Front porch
  ld([channel])                   #1 Advance to next sound channel
  label('sound3')                 # Return from vCPU interpreter
  anda([channelMask])             #2
  adda(1)                         #3
  ld(syncBits^hSync,OUT)          #4 Start horizontal pulse

  # Horizontal sync and sound channel update for scanlines outside vBlank
  label('sound2')
  st([channel],Y)                 #5
  ld(0x7f)                        #6
  anda([Y,oscL])                  #7
  adda([Y,keyL])                  #8
  st([Y,oscL])                    #9
  anda(0x80,X)                    #10
  ld([X])                         #11
  adda([Y,oscH])                  #12
  adda([Y,keyH])                  #13
  st([Y,oscH] )                   #14
  anda(0xfc)                      #15
  xora([Y,wavX])                  #16
  ld(AC,X)                        #17
  ld([Y,wavA])                    #18
  ld(soundTable>>8,Y)             #19
  adda([Y,X])                     #20
  bmi(pc()+3)                     #21
  bra(pc()+3)                     #22
  anda(63)                        #23
  ld(63)                          #23
  adda([sample])                  #24
  st([sample])                    #25

  ld([xout])                      #26 Gets copied to XOUT
  bra([nextVideo])                #27
  ld(syncBits,OUT)                #28 End horizontal pulse

  # Back porch B: second of 4 repeated scan lines
  # - Recompute Xi from dXi and store for retrieval in the next scan lines
  label('videoB')
  ld('videoC')                    #29 2nd scanline of 4
  st([nextVideo])                 #30
  ld(videoTable>>8,Y)             #31
  ld([videoY])                    #32
  adda(1,X)                       #33
  ld([frameX])                    #34
  adda([Y,X])                     #35
  bra([videoModeB])               #36
  st([frameX],X)                  #37 Store in RAM and X

  # Back porch C: third of 4 repeated scan lines
  # - Nothing new to for video do as Yi and Xi are known,
  # - This is the time to emit and reset the next sound sample
  label('videoC')
  ld('videoD')                    #29 3rd scanline of 4
  st([nextVideo])                 #30
  ld([sample])                    #31 New sound sample is ready (didn't fit in audio loop)
  ora(0x0f)                       #32
  anda([xoutMask])                #33
  st([xout])                      #34 Update [xout] with new sample (4 channels just updated)
  st(sample, [sample])            #35 Reset for next sample
  bra([videoModeC])               #36
  ld([frameX],X)                  #37

  # Back porch D: last of 4 repeated scan lines
  # - Calculate the next frame index
  # - Decide if this is the last line or not
  label('videoD')                 # Default video mode
  ld([frameX], X)                 #29 4th scanline of 4
  ld([videoY])                    #30
  suba((120-1)*2)                 #31
  beq('.lastpixels#34')           #32
  adda(120*2)                     #33 More pixel lines to go
  st([videoY])                    #34
  ld('videoA')                    #35
  bra([videoModeD])               #36
  st([nextVideo])                 #37

  label('.lastpixels#34')
  if soundDiscontinuity == 1:
    st(sample, [sample])          #34 Sound continuity
  else:
    nop()                         #34
  ld('videoE')                    #35 No more pixel lines to go
  bra([videoModeD])               #36
  st([nextVideo])                 #37

  # Back porch "E": after the last line
  # - Go back and and enter vertical blank (program page 2)
  label('videoE') # Exit visible area
  ld(hi('vBlankStart'),Y)         #29 Return to vertical blank interval
  jmp(Y,'vBlankStart')            #30
  ld(syncBits)                    #31

  # Video mode that blacks out one or more pixel lines from the top of screen.
  # This yields some speed, but also frees up screen memory for other purposes.
  # Note: Sound output becomes choppier the more pixel lines are skipped
  # Note: The vertical blank driver leaves 0x80 behind in [videoSync1]
  label('videoF')
  ld([videoSync1])                #29 Completely black pixel line
  adda(0x80)                      #30
  st([videoSync1],X)              #31
  ld([frameX])                    #32
  suba([X])                       #33 Decrements every two VGA scanlines
  beq('.videoF#36')               #34
  st([frameX])                    #35
  bra('nopixels')                 #36
  label('.videoF#36')
  ld('videoA')                    #36,37 Transfer to visible screen area
  st([nextVideo])                 #37
  #
  # Alternative for pixel burst: faster application mode
  label('nopixels')
  ld([ctrlBitsCopy],X)            #38
  ctrl(X)                         #39
  runVcpu(199-40,
          'ABCD line 40-520',
          returnTo=0x1fe)         #40 Application interpreter (black scanlines)

else:  # NORMAL VIDEO CODE

  assert pc() == 0x1ff
  bra('sound3')                   #200,0 <New scan line start>
  align(0x100, size=0x100)
  ld([channel])                   #1 AC already contains [channel]

  # Back porch A: first of 4 repeated scan lines
  # - Fetch next Yi and store it for retrieval in the next scan lines
  # - Calculate Xi from dXi, but there is no cycle time left to store it as well
  label('videoA')
  ld('videoB')                    #29 1st scanline of 4 (always visible)
  st([nextVideo])                 #30
  ld(videoTable>>8,Y)             #31
  ld([videoY],X)                  #32
  ld([Y,X])                       #33
  st([Y,Xpp])                     #34 Just X++
  st([frameY])                    #35
  ld([Y,X])                       #36
  adda([frameX],X)                #37
  label('pixels')
  ld([frameY],Y)                  #38
  ld(syncBits)                    #39

  # Stream 160 pixels from memory location <Yi,Xi> onwards
  # Superimpose the sync signal bits to be robust against misprogramming
  for i in range(qqVgaWidth):
    ora([Y,Xpp],OUT)              #40-199 Pixel burst
  ld(syncBits,OUT)                #0 <New scan line start> Back to black

  # Front porch
  ld([channel])                   #1 Advance to next sound channel
  label('sound3')                 # Return from vCPU interpreter
  anda([channelMask])             #2
  adda(1)                         #3
  ld(syncBits^hSync,OUT)          #4 Start horizontal pulse

  # Horizontal sync and sound channel update for scanlines outside vBlank
  label('sound2')
  st([channel],Y)                 #5
  ld(0x7f)                        #6
  anda([Y,oscL])                  #7
  adda([Y,keyL])                  #8
  st([Y,oscL])                    #9
  anda(0x80,X)                    #10
  ld([X])                         #11
  adda([Y,oscH])                  #12
  adda([Y,keyH])                  #13
  st([Y,oscH] )                   #14
  anda(0xfc)                      #15
  xora([Y,wavX])                  #16
  ld(AC,X)                        #17
  ld([Y,wavA])                    #18
  ld(soundTable>>8,Y)             #19
  adda([Y,X])                     #20
  bmi(pc()+3)                     #21
  bra(pc()+3)                     #22
  anda(63)                        #23
  ld(63)                          #23(!)
  adda([sample])                  #24
  st([sample])                    #25

  ld([xout])                      #26 Gets copied to XOUT
  bra([nextVideo])                #27
  ld(syncBits,OUT)                #28 End horizontal pulse

  # Back porch B: second of 4 repeated scan lines
  # - Recompute Xi from dXi and store for retrieval in the next scan lines
  label('videoB')
  ld('videoC')                    #29 2nd scanline of 4
  st([nextVideo])                 #30
  ld(videoTable>>8,Y)             #31
  ld([videoY])                    #32
  adda(1,X)                       #33
  ld([frameX])                    #34
  adda([Y,X])                     #35
  bra([videoModeB])               #36
  st([frameX],X)                  #37 Store in RAM and X

  # Back porch C: third of 4 repeated scan lines
  # - Nothing new to for video do as Yi and Xi are known,
  # - This is the time to emit and reset the next sound sample
  label('videoC')
  ld('videoD')                    #29 3rd scanline of 4
  st([nextVideo])                 #30
  ld([sample])                    #31 New sound sample is ready (didn't fit in audio loop)
  ora(0x0f)                       #32
  anda([xoutMask])                #33
  st([xout])                      #34 Update [xout] with new sample (4 channels just updated)
  st(sample, [sample])            #35 Reset for next sample
  bra([videoModeC])               #36
  ld([frameX],X)                  #37

  # Back porch D: last of 4 repeated scan lines
  # - Calculate the next frame index
  # - Decide if this is the last line or not
  label('videoD')                 # Default video mode
  ld([frameX], X)                 #29 4th scanline of 4
  ld([videoY])                    #30
  suba((120-1)*2)                 #31
  beq('.lastpixels#34')           #32
  adda(120*2)                     #33 More pixel lines to go
  st([videoY])                    #34
  ld('videoA')                    #35
  bra([videoModeD])               #36
  st([nextVideo])                 #37

  label('.lastpixels#34')
  if soundDiscontinuity == 1:
    st(sample, [sample])          #34 Sound continuity
  else:
    nop()                         #34
  ld('videoE')                    #35 No more pixel lines to go
  bra([videoModeD])               #36
  st([nextVideo])                 #37

  # Back porch "E": after the last line
  # - Go back and and enter vertical blank (program page 2)
  label('videoE') # Exit visible area
  ld(hi('vBlankStart'),Y)         #29 Return to vertical blank interval
  jmp(Y,'vBlankStart')            #30
  ld(syncBits)                    #31

  # Video mode that blacks out one or more pixel lines from the top of screen.
  # This yields some speed, but also frees up screen memory for other purposes.
  # Note: Sound output becomes choppier the more pixel lines are skipped
  # Note: The vertical blank driver leaves 0x80 behind in [videoSync1]
  label('videoF')
  ld([videoSync1])                #29 Completely black pixel line
  adda(0x80)                      #30
  st([videoSync1],X)              #31
  ld([frameX])                    #32
  suba([X])                       #33 Decrements every two VGA scanlines
  beq('.videoF#36')               #34
  st([frameX])                    #35
  bra('nopixels')                 #36
  label('.videoF#36')
  ld('videoA')                    #36,37 Transfer to visible screen area
  st([nextVideo])                 #37
  #
  # Alternative for pixel burst: faster application mode
  label('nopixels')
  runVcpu(200-38, 'ABCD line 40-520',
          returnTo=0x1ff)         #38 Application interpreter (black scanlines)


#-----------------------------------------------------------------------
#
#  $0300 ROM page 3: Application interpreter primary page
#
#-----------------------------------------------------------------------

# Enter the timing-aware application interpreter (aka virtual CPU, vCPU)
#
# This routine will execute as many as possible instructions in the
# allotted time. When time runs out, it synchronizes such that the total
# duration matches the caller's request. Durations are counted in `ticks',
# which are multiples of 2 clock cycles.
#
# Synopsis: Use the runVcpu() macro as entry point

# We let 'ENTER' begin one word before the page boundary, for a bit extra
# precious space in the packed interpreter code page. Although ENTER's
# first instruction is bra() which normally doesn't cross page boundaries,
# in this case it will still jump into the right space, because branches
# from $xxFF land in the next page anyway.
while pc()&255 < 255:
  nop()
label('ENTER')
bra('.next2')                   #0 Enter at '.next2' (so no startup overhead)
# --- Page boundary ---
align(0x100,size=0x100)
label('NEXTY')                  # Alternative for REENTER
ld([vPC+1],Y)                   #1

# Fetch next instruction and execute it, but only if there are sufficient
# ticks left for the slowest instruction.
label('NEXT')
adda([vTicks])                  #0 Track elapsed ticks (actually counting down: AC<0)
blt('EXIT')                     #1 Escape near time out
label('.next2')
st([vTicks])                    #2
ld([vPC])                       #3 Advance vPC
adda(2)                         #4
st([vPC],X)                     #5
ld([Y,X])                       #6 Fetch opcode (actually a branch target)
st([Y,Xpp])                     #7 Just X++
bra(AC)                         #8 Dispatch
ld([Y,X])                       #9 Prefetch operand

# Resync with video driver and transfer control
label('EXIT')
adda(maxTicks)                  #3
label('RESYNC')
bgt(pc()&255)                   #4 Resync
suba(1)                         #5
ld(hi('vBlankStart'),Y)         #6
jmp(Y,[vReturn])                #7 To video driver
ld([channel])                   #8 with channel in AC
assert vCPU_overhead ==          9

# Instruction LDWI: Load immediate word constant (vAC=D), 20 cycles
label('LDWI')
st([vAC])                       #10
st([Y,Xpp])                     #11 Just X++
ld([Y,X])                       #12 Fetch second operand
st([vAC+1])                     #13
ld([vPC])                       #14 Advance vPC one more
adda(1)                         #15
st([vPC])                       #16
bra('NEXTY')                    #18
ld(-20/2)                       #18

# Instruction LD: Load byte from zero page (vAC=[D]), 22 cycles
label('LD')
ld(AC,X)                        #10,19
ld([X])                         #11
ld(hi('ld#15'),Y)               #12
jmp(Y,'ld#15')                  #13
st([vAC])                       #14

# Instruction CMPHS: Adjust high byte for signed compare (vACH=XXX), 28 cycles
label('CMPHS_v5')
ld(hi('cmphs#13'),Y)            #10
jmp(Y,'cmphs#13')               #11
#ld(AC,X)                       #12 Overlap
#
# Instruction LDW: Load word from zero page (vAC=[D]+256*[D+1]), 20 cycles
label('LDW')
ld(AC,X)                        #10,12
adda(1)                         #11
st([vTmp])                      #12 Address of high byte
ld([X])                         #13
st([vAC])                       #14
ld([vTmp],X)                    #15
ld([X])                         #16
st([vAC+1])                     #17
bra('NEXT')                     #18
ld(-20/2)                       #19

# Instruction STW: Store word in zero page ([D],[D+1]=vAC&255,vAC>>8), 20 cycles
label('STW')
ld(AC,X)                        #10,20
adda(1)                         #11
st([vTmp])                      #12 Address of high byte
ld([vAC])                       #13
st([X])                         #14
ld([vTmp],X)                    #15
ld([vAC+1])                     #16
st([X])                         #17
bra('NEXT')                     #18
ld(-20/2)                       #19

# Instruction PREFIX35: (used to be BCC)
label('BCC')
label('PREFIX35')
st([Y,Xpp])                     #10
ld(hi('PREFIX35_PAGE'),Y)       #11
jmp(Y,AC)                       #12
ld([vPC+1],Y)                   #13

# Instruction MOVQB (39 ii vv), 28 cycles
# * Store immediate ii into byte [vv]:=ii
label('MOVQB_v7')
ld(hi('movqb#13'),Y)            #10
jmp(Y,'movqb#13')               #11

# Instruction MOVQW (3b ii vv), 30 cycles
# * Store immediate ii into word [vv]:=ii [vv+1]:=0
label('MOVQW_v7')
ld(hi('movqw#13'),Y)            #10,12
jmp(Y,'movqw#13')               #11

# Instruction DEEKA (3d xx), 30 cycles
# * Load word at location [vAC] and store into [xx]
# * Uses vTmp0 as a scratch register
label('DEEKA_v7')
ld(hi('deeka#13'),Y)            #10,12
jmp(Y,'deeka#13')               #11

# Instruction JEQ (3f ll hh), 26 cycles (was EQ)
# * Original idea from at67
# * Branch if zero (if(vACL==0)vPC=hhll[+2])
label('EQ')
label('JEQ_v7')
ld(hi('jeq#13'),Y)              #10,12
jmp(Y,'jeq#13')                 #11

# Instruction DEEKV (41 vv), 28 cycles
# * Original idea from at67
# * shortcut for LDW(vv);DEEK()
label('DEEKV_v7')
ld(hi('deekv#13'),Y)            #10,12
jmp(Y,'deekv#13')               #11
st([vTmp])                      #12

# Instruction DOKEQ (44 ii), 22 cycles
# * Store immediate ii into word pointed by vAC
label('DOKEQ_v7')
ld(hi('dokeq#13'),Y)            #10,12
jmp(Y,'dokeq#13')               #11

# Instruction POKEQ (46 ii), 20 cycles
# * Store immediate ii into byte pointed by vAC
label('POKEQ_v7')
ld(hi('pokeq#13'),Y)            #10,12
jmp(Y,'pokeq#13')               #11

# Instruction POKEA (48 xx), 28 cycles
# * Store word [xx] at location [vAC]
label('POKEA_v7')
ld(hi('pokea#13'),Y)            #10,12
jmp(Y,'pokea#13')               #11

# Instruction slot (4a ..)
nop()                           #10,12
nop()                           #11
nop()                           #11

# Instruction JGT (4d ll hh), 26 cycles (was GT)
# * Branch if positive (if(vACL>0)vPC=hhll[+2])
# * Original idea from at67
label('GT')
label('JGT_v7')
ld(hi('jgt#13'),Y)              #10,12
jmp(Y,'jgt#13')                 #11
ld([vAC+1])                     #12

# Instruction JLT (50 ll hh), 26 cycles (was LT)
# * Branch if negative (if(vACL<0)vPC=hhll[+2])
# * Original idea from at67
label('LT')
label('JLT_v7')
ld(hi('jlt#13'),Y)              #10
jmp(Y,'jlt#13')                 #11
ld([vAC+1])                     #12

# Instruction JGE (53 ll hh), 26 cycles (was GE)
# * Branch if positive or zero (if(vACL>=0)vPC=hhll[+2])
# * Original idea from at67
label('GE')
label('JGE_v7')
ld(hi('jge#13'),Y)              #10
jmp(Y,'jge#13')                 #11
ld([vAC+1])                     #12

# Instruction JLE (56 ll hh), 26 cycles (was LE)
# * Branch if negative or zero (if(vACL<=0)vPC=hhll[+2])
# * Original idea from at67
label('JLE_v7')
ld(hi('jle#13'),Y)              #10
jmp(Y,'jle#13')                 #11
ld([vAC+1])                     #12

# Instruction LDI: Load immediate small positive constant (vAC=D), 16 cycles
label('LDI')
st([vAC])                       #10
ld(0)                           #11
st([vAC+1])                     #12
bra('NEXTY')                    #13
ld(-16/2)                       #14

# Instruction ST: Store byte in zero page ([D]=vAC&255), 16 cycles
label('ST')
ld(AC,X)                        #10,15
ld([vAC])                       #11
st([X])                         #12
bra('NEXTY')                    #13
ld(-16/2)                       #14

# Instruction POP: Pop address from stack (vLR,vSP==[vSP]+256*[vSP+1],vSP+2), 26 cycles
label('POP')
ld(hi('pop#13'),Y)              #10
jmp(Y,'pop#13')                 #11
ld([vSP],X)                     #12

# Instruction ADDV (66 vv), 30 cycles
# * Add vAC to word [vv]
label('ADDV_v7')
ld(hi('addv#13'),Y)             #10,12
jmp(Y,'addv#13')                #11

# Instruction SUBV (68 vv), 30 cycles
# * Subtract vAC from word [vv]
label('SUBV_v7')
ld(hi('subv#13'),Y)             #10,12
jmp(Y,'subv#13')                #11

# Instruction slot (6a ..)
nop()                           #10,12
nop()                           #11

# Instruction slot (6c ..)
nop()                           #10,12
nop()                           #11

# Instruction slot (6e ..)
nop()                           #10,12
nop()                           #11

# Instruction slot (70 ..)
nop()                           #10,12
nop()                           #11

# Instruction JNE (72 ii jj), 26 cycles (was NE)
# * Original idea from at67
# * Branch if not zero (if(vACL!=0)vPC=iijj)
label('NE')
label('JNE_v7')
ld(hi('jne#13'),Y)              #10
jmp(Y,'jne#13')                 #11
nop()                           #12

# Instruction PUSH: Push vLR on stack ([vSP-2],v[vSP-1],vSP=vLR&255,vLR>>8,vLR-2), 26 cycles
label('PUSH')
ld(hi('push#13'),Y)             #10
jmp(Y,'push#13')                #11
ld(0,Y)                         #12

# Instruction LDNI (78 xx), 16 cycles
# * Load negative constant vAC:=0xffxx
label('LDNI_v7')
st([vAC])                       #10
ld(0xff)                        #11
st([vAC+1])                     #12
bra('NEXTY')                    #13
ld(-16/2)                       #14

# Instruction DOKEA (7d xx), 28 cycles
# * Store word [xx] at location [vAC]
label('DOKEA_v7')
ld(hi('dokea#13'),Y)            #10
jmp(Y,'dokea#13')               #11+overlap

# Instruction LUP: ROM lookup (vAC=ROM[vAC+D]), 26 cycles
label('LUP')
ld([vAC+1],Y)                   #10
jmp(Y,251)                      #11 Trampoline offset
adda([vAC])                     #12

# Instruction ANDI: Logical-AND with small constant (vAC&=D), 22 cycles
label('ANDI')
ld(hi('andi#13'),Y)             #10
jmp(Y,'andi#13')                #11
anda([vAC])                     #12

# Instruction CALLI: Goto immediate address and remember vPC (vLR,vPC=vPC+3,$HHLL-2), 28 cycles
label('CALLI_v5')
ld(hi('calli#13'),Y)            #10
jmp(Y,'calli#13')               #11
ld([vPC])                       #12

# Instruction ORI: Logical-OR with small constant (vAC|=D), 14 cycles
label('ORI')
ora([vAC])                      #10
st([vAC])                       #11
bra('NEXT')                     #12
ld(-14/2)                       #13

# Instruction XORI: Logical-XOR with small constant (vAC^=D), 14 cycles
label('XORI')
xora([vAC])                     #10
st([vAC])                       #11
bra('NEXT')                     #12
ld(-14/2)                       #13

# Instruction BRA: Branch unconditionally (vPC=(vPC&0xff00)+D), 14 cycles
label('BRA')
st([vPC])                       #10
bra('NEXTY')                    #11
ld(-14/2)                       #12

# Instruction INC: Increment zero page byte ([D]++), 20 cycles
label('INC')
ld(AC,X)                        #10,13
ld(hi('inc#14'),Y)              #11
jmp(Y,'inc#14')                 #12
ld(1)                           #13

# Instruction CMPHU: Adjust high byte for unsigned compare (vACH=XXX), 28 cycles
label('CMPHU_v5')
ld(hi('cmphu#13'),Y)            #10
jmp(Y,'cmphu#13')               #11
#ld(AC,X)                       #12 Overlap
#
# Instruction ADDW: Word addition with zero page (vAC+=[D]+256*[D+1]), 28 cycles
label('ADDW')
# The non-carry paths could be 26 cycles at the expense of (much) more code.
# But a smaller size is better so more instructions fit in this code page.
# 28 cycles is still 4.5 usec. The 6502 equivalent takes 20 cycles or 20 usec.
ld(AC,X)                        #10,12 Address of low byte to be added
adda(1)                         #11
st([vTmp])                      #12 Address of high byte to be added
ld([vAC])                       #13 Add the low bytes
adda([X])                       #14
st([vAC])                       #15 Store low result
bmi('.addw#18')                 #16 Now figure out if there was a carry
suba([X])                       #17 Gets back the initial value of vAC
bra('.addw#20')                 #18
ora([X])                        #19 Carry in bit 7
label('.addw#18')
anda([X])                       #18 Carry in bit 7
nop()                           #19
label('.addw#20')
anda(0x80,X)                    #20 Move carry to bit 0
ld([X])                         #21
adda([vAC+1])                   #22 Add the high bytes with carry
ld([vTmp],X)                    #23
adda([X])                       #24
st([vAC+1])                     #25 Store high result
bra('NEXT')                     #26
ld(-28/2)                       #27

# Instruction PEEK: Read byte from memory (vAC=[vAC]), 26 cycles
label('PEEK')
ld(hi('peek'),Y)                #10
jmp(Y,'peek')                   #11

# SYS restart
label('.sys#13')
ld(hi('.sys#16'),Y)              #13,12
jmp(Y,'.sys#16')                 #14

# Instruction slot (b1 ..)
nop()                            #10,15
nop()                            #11
nop()                            #12

# Instruction SYS: Native call, <=256 cycles (<=128 ticks, in reality less)
#
# The 'SYS' vCPU instruction first checks the number of desired ticks given by
# the operand. As long as there are insufficient ticks available in the current
# time slice, the instruction will be retried. This will effectively wait for
# the next scan line if the current slice is almost out of time. Then a jump to
# native code is made. This code can do whatever it wants, but it must return
# to the 'REENTER' label when done. When returning, AC must hold (the negative
# of) the actual consumed number of whole ticks for the entire virtual
# instruction cycle (from NEXT to NEXT). This duration may not exceed the prior
# declared duration in the operand + 28 (or maxTicks). The operand specifies the
# (negative) of the maximum number of *extra* ticks that the native call will
# need. The GCL compiler automatically makes this calculation from gross number
# of cycles to excess number of ticks.
# SYS functions can modify vPC to implement repetition. For example to split
# up work into multiple chucks.
label('SYS')
adda([vTicks])                  #10
blt('.sys#13')                  #11
ld([sysFn+1],Y)                 #12
jmp(Y,[sysFn])                  #13
#dummy()                        #14 Overlap
#
# Instruction SUBW: Word subtract with zero page (AC-=[D]+256*[D+1]), 28 cycles
# All cases can be done in 26 cycles, but the code will become much larger
label('SUBW')
ld(AC,X)                        #10,14 Address of low byte to be subtracted
adda(1)                         #11
st([vTmp])                      #12 Address of high byte to be subtracted
ld([vAC])                       #13
bmi('.subw#16')                 #14
suba([X])                       #15
st([vAC])                       #16 Store low result
bra('.subw#19')                 #17
ora([X])                        #18 Carry in bit 7
label('.subw#16')
st([vAC])                       #16 Store low result
anda([X])                       #17 Carry in bit 7
nop()                           #18
label('.subw#19')
anda(0x80,X)                    #19 Move carry to bit 0
ld([vAC+1])                     #20
suba([X])                       #21
ld([vTmp],X)                    #22
suba([X])                       #23
st([vAC+1])                     #24
label('REENTER_28')
ld(-28/2)                       #25
label('REENTER')
bra('NEXT')                     #26 Return from SYS calls
ld([vPC+1],Y)                   #27

# Instruction DEF: Define data or code (vAC,vPC=vPC+2,(vPC&0xff00)+D), 24 cycles
label('DEF')
ld(hi('def#13'),Y)              #10
jmp(Y,'def#13')                 #11
#st([vTmp])                     #12 Overlap
#
# Instruction CALL: Goto address and remember vPC (vLR,vPC=vPC+2,[D]+256*[D+1]-2), 26 cycles
label('CALL')
st([vTmp])                      #10,12
ld(hi('call#14'),Y)             #11
jmp(Y,'call#14')                #12
adda(1,X)                       #13

# Instruction CMPWS (d3 vv), 26-30 cycles
# * Signed compare of vAC and [vv]. Faster than CMPHS+SUBW
label('CMPWS_v7')
ld(hi('cmpws#13'),Y)            #10
jmp(Y,'cmpws#13')               #11
st([vTmp])                      #12

# Instruction CMPWU (d6 vv), 26-30 cycles
# * Unsigned compare of vAC and [vv]. Faster than CMPHU+SUBW
label('CMPWU_v7')
ld(hi('cmpwu#13'),Y)            #10
jmp(Y,'cmpwu#13')               #11
st([vTmp])                      #12

# Instruction CMPIS (d9 ii), 22-30 cycles
# * Signed compare of vAC and byte ii.
label('CMPIS_v7')
ld(hi('cmpis#13'),Y)            #10
jmp(Y,'cmpis#13')               #11

# Instruction CMPIU (db ii), 24-30 cycles
# * Unsigned compare of vAC and byte ii.
label('CMPIU_v7')
ld(hi('cmpiu#13'),Y)            #10,12
jmp(Y,'cmpiu#13')               #11

# Instruction PEEKV (dd vv), 28 cycles
# * Shortcut for LDW(vv);DEEK()
label('PEEKV_v7')
ld(hi('peekv#13'),Y)            #10,12
jmp(Y,'peekv#13')               #11

# Instruction ALLOC: Create or destroy stack frame (vSP+=D), 14 cycles
label('ALLOC')
ld(hi('alloc#13'),Y)            #10,12
jmp(Y,'alloc#13')               #11

# Instruction slot (e1 ..)
nop()                           #10
nop()                           #11

# The instructions below are all implemented in the second code page. Jumping
# back and forth makes each 6 cycles slower, but it also saves space in the
# primary page for the instructions above. Most of them are in fact not very
# critical, as evidenced by the fact that they weren't needed for the first
# Gigatron applications (Snake, Racer, Mandelbrot, Loader). By providing them
# in this way, at least they don't need to be implemented as a SYS extension.

# Instruction ADDI: Add small positive constant (vAC+=D), 28 cycles
label('ADDI')
ld(hi('addi'),Y)                #10,12
jmp(Y,'addi')                   #11
st([vTmp])                      #12

# Instruction SUBI: Subtract small positive constant (vAC+=D), 28 cycles
label('SUBI')
ld(hi('subi'),Y)                #10
jmp(Y,'subi')                   #11
st([vTmp])                      #12

# Instruction LSLW: Logical shift left (vAC<<=1), 28 cycles
# Useful, because ADDW can't add vAC to itself. Also more compact.
label('LSLW')
ld(hi('lslw'),Y)                #10
jmp(Y,'lslw')                   #11
ld([vAC])                       #12

# Instruction STLW: Store word in stack frame ([vSP+D],[vSP+D+1]=vAC&255,vAC>>8), 26 cycles
label('STLW')
ld(hi('stlw'),Y)                #10
jmp(Y,'stlw')                   #11
#dummy()                        #12 Overlap
#
# Instruction LDLW: Load word from stack frame (vAC=[vSP+D]+256*[vSP+D+1]), 26 cycles
label('LDLW')
ld(hi('ldlw'),Y)                #10,12
jmp(Y,'ldlw')                   #11
#dummy()                        #12 Overlap
#
# Instruction POKE: Write byte in memory ([[D+1],[D]]=vAC&255), 28 cycles
label('POKE')
ld(hi('poke'),Y)                #10,12
jmp(Y,'poke')                   #11
st([vTmp])                      #12

# Instruction DOKE: Write word in memory ([[D+1],[D]],[[D+1],[D]+1]=vAC&255,vAC>>8), 28 cycles
label('DOKE')
ld(hi('doke'),Y)                #10
jmp(Y,'doke')                   #11
st([vTmp])                      #12

# Instruction DEEK: Read word from memory (vAC=[vAC]+256*[vAC+1]), 28 cycles
label('DEEK')
ld(hi('deek'),Y)                #10
jmp(Y,'deek')                   #11
#dummy()                        #12 Overlap
#
# Instruction ANDW: Word logical-AND with zero page (vAC&=[D]+256*[D+1]), 28 cycles
label('ANDW')
ld(hi('andw'),Y)                #10,12
jmp(Y,'andw')                   #11
#dummy()                        #12 Overlap
#
# Instruction ORW: Word logical-OR with zero page (vAC|=[D]+256*[D+1]), 28 cycles
label('ORW')
ld(hi('orw'),Y)                 #10,12
jmp(Y,'orw')                    #11
#dummy()                        #12 Overlap
#
# Instruction XORW: Word logical-XOR with zero page (vAC^=[D]+256*[D+1]), 26 cycles
label('XORW')
ld(hi('xorw'),Y)                #10,12
jmp(Y,'xorw')                   #11
st([vTmp])                      #12
# We keep XORW 2 cycles faster than ANDW/ORW, because that
# can be useful for comparing numbers for equality a tiny
# bit faster than with SUBW

# Instruction RET: Function return (vPC=vLR-2), 16 cycles
label('RET')
ld([vLR])                       #10
assert pc()&255 == 0

#-----------------------------------------------------------------------
#
#  $0400 ROM page 4: Application interpreter extension
#
#-----------------------------------------------------------------------
align(0x100, size=0x100)

# (Continue RET)
suba(2)                         #11
st([vPC])                       #12
ld([vLR+1])                     #13
st([vPC+1])                     #14
ld(hi('REENTER'),Y)             #15
jmp(Y,'REENTER')                #16
ld(-20/2)                       #17

# DEF implementation
label('def#13')
ld([vPC])                       #13
adda(2)                         #14
st([vAC])                       #15
ld([vPC+1])                     #16
st([vAC+1])                     #17
ld([vTmp])                      #18
st([vPC])                       #19
ld(hi('NEXTY'),Y)               #20
jmp(Y,'NEXTY')                  #21
ld(-24/2)                       #22

# Clear vACH (continuation of ANDI and LD instructions)
label('andi#13')
nop()                           #13
st([vAC])                       #14
#
label('ld#15')
ld(0)                           #15 Clear high byte
st([vAC+1])                     #16
ld(hi('REENTER'),Y)             #17
jmp(Y,'REENTER')                #18
ld(-22/2)                       #19

# ADDI implementation
label('addi')
adda([vAC])                     #13
st([vAC])                       #14 Store low result
bmi('.addi#17')                 #15 Now figure out if there was a carry
suba([vTmp])                    #16 Gets back the initial value of vAC
bra('.addi#19')                 #17
ora([vTmp])                     #18 Carry in bit 7
label('.addi#17')
anda([vTmp])                    #17 Carry in bit 7
nop()                           #18
label('.addi#19')
anda(0x80,X)                    #19 Move carry to bit 0
ld([X])                         #20
adda([vAC+1])                   #21 Add the high bytes with carry
ld(hi('REENTER_28'),Y)          #22
jmp(Y,'REENTER_28')             #23
st([vAC+1])                     #24 Store high result

# SUBI implementation
label('subi')
ld([vAC])                       #13
bmi('.subi#16')                 #14
suba([vTmp])                    #15
st([vAC])                       #16 Store low result
bra('.subi#19')                 #17
ora([vTmp])                     #18 Carry in bit 7
label('.subi#16')
st([vAC])                       #16 Store low result
anda([vTmp])                    #17 Carry in bit 7
nop()                           #18
label('.subi#19')
anda(0x80,X)                    #19 Move carry to bit 0
ld([vAC+1])                     #20
suba([X])                       #21
ld(hi('REENTER_28'),Y)          #22
jmp(Y,'REENTER_28')             #23
st([vAC+1])                     #24

# LSLW implementation
label('lslw')
anda(128,X)                     #13
adda([vAC])                     #14
st([vAC])                       #15
ld([X])                         #16
adda([vAC+1])                   #17
adda([vAC+1])                   #18
st([vAC+1])                     #19
ld([vPC])                       #20
suba(1)                         #21
ld(hi('REENTER_28'),Y)          #22
jmp(Y,'REENTER_28')             #23
st([vPC])                       #24

# POKE implementation
label('poke')
adda(1,X)                       #13
ld([X])                         #14
ld(AC,Y)                        #15
ld([vTmp],X)                    #16
ld([X])                         #17
ld(AC,X)                        #18
ld([vAC])                       #19
st([Y,X])                       #20
ld(hi('REENTER'),Y)             #21
jmp(Y,'REENTER')                #22
ld(-26/2)                       #23

# PEEK implementation
label('peek')
ld([vPC])                       #13
suba(1)                         #14
st([vPC])                       #15
ld([vAC],X)                     #16
ld([vAC+1],Y)                   #17
ld([Y,X])                       #18
st([vAC])                       #19
ld(0)                           #20
st([vAC+1])                     #21
ld(hi('NEXTY'),Y)               #22
jmp(Y,'NEXTY')                  #23
ld(-26/2)                       #24

# DOKE implementation
label('doke')
adda(1,X)                       #13
ld([X])                         #14
ld(AC,Y)                        #15
ld([vTmp],X)                    #16
ld([X])                         #17
ld(AC,X)                        #18
ld([vAC])                       #19
st([Y,Xpp])                     #20
ld([vAC+1])                     #21
st([Y,X])                       #22 Incompatible with REENTER_28
ld(hi('REENTER'),Y)             #23
jmp(Y,'REENTER')                #24
ld(-28/2)                       #25

# DEEK implementation
label('deek')
ld([vPC])                       #13
suba(1)                         #14
st([vPC])                       #15
ld([vAC],X)                     #16
ld([vAC+1],Y)                   #17
ld([Y,X])                       #18
st([Y,Xpp])                     #19 Just X++
st([vAC])                       #20
ld([Y,X])                       #21
ld(hi('REENTER_28'),Y)          #22
jmp(Y,'REENTER_28')             #23
st([vAC+1])                     #24

# ANDW implementation
label('andw')
st([vTmp])                      #13
adda(1,X)                       #14
ld([X])                         #15
anda([vAC+1])                   #16
st([vAC+1])                     #17
ld([vTmp],X)                    #18
ld([X])                         #19
anda([vAC])                     #20
st([vAC])                       #21
ld(hi('REENTER_28'),Y)          #22
jmp(Y,'REENTER_28')             #23
#dummy()                        #24 Overlap
#
# ORW implementation
label('orw')
st([vTmp])                      #13,24
adda(1,X)                       #14
ld([X])                         #15
ora([vAC+1])                    #16
st([vAC+1])                     #17
ld([vTmp],X)                    #18
ld([X])                         #19
ora([vAC])                      #20
st([vAC])                       #21
ld(hi('REENTER_28'),Y)          #22
jmp(Y,'REENTER_28')             #23
#dummy()                        #24 Overlap
#
# XORW implementation
label('xorw')
adda(1,X)                       #13,24
ld([X])                         #14
xora([vAC+1])                   #15
st([vAC+1])                     #16
ld([vTmp],X)                    #17
ld([X])                         #18
xora([vAC])                     #19
st([vAC])                       #20
ld(hi('REENTER'),Y)             #21
jmp(Y,'REENTER')                #22
ld(-26/2)                       #23
#
# SYS implementation
label('.sys#16')
nop()                           #16
label('.sys#17')
ld([vPC])                       #17
suba(2)                         #18
st([vPC])                       #19
ld(hi('NEXTY'),Y)               #20
jmp(Y,'NEXTY')                  #21
ld(-24//2)                      #22
#
# CALL implementation
# - Displacing CALL adds 4 cycles.
#   This is less critical when we have CALLI.
label('call#14')
ld([vPC])                       #14
adda(2)                         #15 Point to instruction after CALL
st([vLR])                       #16
ld([vPC+1])                     #17
st([vLR+1])                     #18
ld([X])                         #19
st([vPC+1])                     #20
ld([vTmp],X)                    #21
ld([X])                         #22
suba(2)                         #23 Because NEXT will add 2
st([vPC])                       #24
ld(hi('REENTER'),Y)             #25
jmp(Y,'REENTER')                #26
ld(-30/2)                       #27



#-----------------------------------------------------------------------
#
#  vCPU extension functions (for acceleration and compaction) follow below.
#
#  The naming convention is: SYS_<CamelCase>[_v<V>]_<N>
#
#  With <N> the maximum number of cycles the function will run
#  (counted from NEXT to NEXT). This is the same number that must
#  be passed to the 'SYS' vCPU instruction as operand, and it will
#  appear in the GCL code upon use.
#
#  If a SYS extension got introduced after ROM v1, the version number of
#  introduction is included in the name. This helps the programmer to be
#  reminded to verify the acutal ROM version and fail gracefully on older
#  ROMs than required. See also Docs/GT1-files.txt on using [romType].
#
#-----------------------------------------------------------------------

fillers(until=0xa7)

#-----------------------------------------------------------------------
# Extension SYS_Random_34: Update entropy and copy to vAC
#-----------------------------------------------------------------------

# This same algorithm runs automatically once per vertical blank.
# Use this function to get numbers at a higher rate.
#
# Variables:
#       vAC

label('SYS_Random_34')
ld([vTicks])                    #15
xora([entropy+1])               #16
ld(1,Y)                         #17
adda([entropy+0])               #18
st([entropy+0])                 #19
st([vAC+0])                     #20
adda([Y,entropy2])              #21
st([Y,entropy2])                #22
bmi('.sysRnd0')                 #23
bra('.sysRnd1')                 #24
xora(64+16+2+1)                 #25
label('.sysRnd0')
xora(64+32+8+4)                 #25
label('.sysRnd1')
adda([entropy+1])               #26
st([entropy+1])                 #27
st([vAC+1])                     #28
ld(hi('REENTER'),Y)             #29
jmp(Y,'REENTER')                #30
ld(-34/2)                       #31

label('SYS_LSRW7_30')
ld([vAC])                       #15
anda(128,X)                     #16
ld([vAC+1])                     #17
adda(AC)                        #18
ora([X])                        #19
st([vAC])                       #20
ld([vAC+1])                     #21
anda(128,X)                     #22
ld([X])                         #23
st([vAC+1])                     #24
ld(hi('REENTER'),Y)             #25
jmp(Y,'REENTER')                #26
ld(-30/2)                       #27

label('SYS_LSRW8_24')
ld([vAC+1])                     #15
st([vAC])                       #16
ld(0)                           #17
st([vAC+1])                     #18
ld(hi('REENTER'),Y)             #19
jmp(Y,'REENTER')                #20
ld(-24/2)                       #21

label('SYS_LSLW8_24')
ld([vAC])                       #15
st([vAC+1])                     #16
ld(0)                           #17
st([vAC])                       #18
ld(hi('REENTER'),Y)             #19
jmp(Y,'REENTER')                #20
ld(-24/2)                       #21

#-----------------------------------------------------------------------
# Extension SYS_Draw4_30
#-----------------------------------------------------------------------

# Draw 4 pixels on screen, horizontally next to each other
#
# Variables:
#       sysArgs[0:3]    Pixels (in)
#       sysArgs[4:5]    Position on screen (in)

label('SYS_Draw4_30')
ld([sysArgs+4],X)               #15
ld([sysArgs+5],Y)               #16
ld([sysArgs+0])                 #17
st([Y,Xpp])                     #18
ld([sysArgs+1])                 #19
st([Y,Xpp])                     #20
ld([sysArgs+2])                 #21
st([Y,Xpp])                     #22
ld([sysArgs+3])                 #23
st([Y,Xpp])                     #24
ld(hi('REENTER'),Y)             #25
jmp(Y,'REENTER')                #26
ld(-30/2)                       #27

#-----------------------------------------------------------------------
# Extension SYS_VDrawBits_134:
#-----------------------------------------------------------------------

# Draw slice of a character, 8 pixels vertical
#
# Variables:
#       sysArgs[0]      Color 0 "background" (in)
#       sysArgs[1]      Color 1 "pen" (in)
#       sysArgs[2]      8 bits, highest bit first (in, changed)
#       sysArgs[4:5]    Position on screen (in)

label('SYS_VDrawBits_134')
ld(hi('sys_VDrawBits'),Y)       #15
jmp(Y,'sys_VDrawBits')          #16
ld([sysArgs+4],X)               #17

#-----------------------------------------------------------------------

# INC implementation
label('inc#14')
adda([X])                       #14
st([X])                         #15
ld(hi('NEXTY'),Y)               #16
jmp(Y,'NEXTY')                  #17
ld(-20/2)                       #18


# Interrupt handler:
#       ... IRQ payload ...
#       LDWI $400
#       LUP  $xx  ==> vRTI
fillers(until=251-17)

label('vRTI#18')
ld(-32//2-v6502_adjust)         #18
adda([vTicks])                  #19
bge('vRTI#22')                  #20
ld([vIrqSave+2])                #21
st([vAC])                       #22
ld([vIrqSave+3])                #23
st([vAC+1])                     #24
ld([vIrqSave+4])                #25
st([vCpuSelect])                #26
ld([vTicks])                    #27
adda(maxTicks-28//2)            #28-28=0
ld(hi('RESYNC'),Y)              #1
jmp(Y,'RESYNC')                 #2
nop()                           #3

label('vRTI#22')
ld(hi('vRTI#25'),Y)             #22
jmp(Y,'vRTI#25')                #23
st([vAC])                       #24

# vRTI entry point
assert(pc()&255 == 251)         # The landing offset 251 for LUP trampoline is fixed
ld([vIrqSave+0])                #13
st([vPC])                       #14
ld([vIrqSave+1])                #15
bra('vRTI#18')                  #16
st([vPC+1])                     #17



#-----------------------------------------------------------------------
#
#  $0500 ROM page 5-6: Shift table and code
#
#-----------------------------------------------------------------------

align(0x100, size=0x200)

# Lookup table for i>>n, with n in 1..6
# Indexing ix = i & ~b | (b-1), where b = 1<<(n-1)
#       ...
#       ld   <.ret
#       st   [vTmp]
#       ld   >shiftTable,y
#       <calculate ix>
#       jmp  y,ac
#       bra  $ff
# .ret: ...
#
# i >> 7 can be always be done with RAM: [i&128]
#       ...
#       anda $80,x
#       ld   [x]
#       ...

label('shiftTable')
shiftTable = pc()

for ix in range(255):
  for n in range(1,7): # Find first zero
    if ~ix & (1 << (n-1)):
      break
  pattern = ['x' if i<n else '1' if ix&(1<<i) else '0' for i in range(8)]
  ld(ix>>n); C('0b%s >> %d' % (''.join(reversed(pattern)), n))

assert pc()&255 == 255
bra([vTmp])                     # Jumps back into next page

label('SYS_LSRW1_48')
assert pc()&255 == 0            # First instruction on this page *must* be a nop
nop()                           #15
ld(hi('shiftTable'),Y)          #16 Logical shift right 1 bit (X >> 1)
ld('.sysLsrw1a')                #17 Shift low byte
st([vTmp])                      #18
ld([vAC])                       #19
anda(0b11111110)                #20
jmp(Y,AC)                       #21
bra(255)                        #22 bra shiftTable+255
label('.sysLsrw1a')
st([vAC])                       #26
ld([vAC+1])                     #27 Transfer bit 8
anda(1)                         #28
adda(127)                       #29
anda(128)                       #30
ora([vAC])                      #31
st([vAC])                       #32
ld('.sysLsrw1b')                #33 Shift high byte
st([vTmp])                      #34
ld([vAC+1])                     #35
anda(0b11111110)                #36
jmp(Y,AC)                       #37
bra(255)                        #38 bra shiftTable+255
label('.sysLsrw1b')
st([vAC+1])                     #42
ld(hi('REENTER'),Y)             #43
jmp(Y,'REENTER')                #44
ld(-48/2)                       #45

label('SYS_LSRW2_52')
ld(hi('shiftTable'),Y)          #15 Logical shift right 2 bit (X >> 2)
ld('.sysLsrw2a')                #16 Shift low byte
st([vTmp])                      #17
ld([vAC])                       #18
anda(0b11111100)                #19
ora( 0b00000001)                #20
jmp(Y,AC)                       #21
bra(255)                        #22 bra shiftTable+255
label('.sysLsrw2a')
st([vAC])                       #26
ld([vAC+1])                     #27 Transfer bit 8:9
adda(AC)                        #28
adda(AC)                        #29
adda(AC)                        #30
adda(AC)                        #31
adda(AC)                        #32
adda(AC)                        #33
ora([vAC])                      #34
st([vAC])                       #35
ld('.sysLsrw2b')                #36 Shift high byte
st([vTmp])                      #37
ld([vAC+1])                     #38
anda(0b11111100)                #39
ora( 0b00000001)                #40
jmp(Y,AC)                       #41
bra(255)                        #42 bra shiftTable+255
label('.sysLsrw2b')
st([vAC+1])                     #46
ld(hi('REENTER'),Y)             #47
jmp(Y,'REENTER')                #48
ld(-52/2)                       #49

label('SYS_LSRW3_52')
ld(hi('shiftTable'),Y)          #15 Logical shift right 3 bit (X >> 3)
ld('.sysLsrw3a')                #16 Shift low byte
st([vTmp])                      #17
ld([vAC])                       #18
anda(0b11111000)                #19
ora( 0b00000011)                #20
jmp(Y,AC)                       #21
bra(255)                        #22 bra shiftTable+255
label('.sysLsrw3a')
st([vAC])                       #26
ld([vAC+1])                     #27 Transfer bit 8:10
adda(AC)                        #28
adda(AC)                        #29
adda(AC)                        #30
adda(AC)                        #31
adda(AC)                        #32
ora([vAC])                      #33
st([vAC])                       #34
ld('.sysLsrw3b')                #35 Shift high byte
st([vTmp])                      #36
ld([vAC+1])                     #37
anda(0b11111000)                #38
ora( 0b00000011)                #39
jmp(Y,AC)                       #40
bra(255)                        #41 bra shiftTable+255
label('.sysLsrw3b')
st([vAC+1])                     #45
ld(-52/2)                       #46
ld(hi('REENTER'),Y)             #47
jmp(Y,'REENTER')                #48
#nop()                          #49

label('SYS_LSRW4_50')
ld(hi('shiftTable'),Y)          #15,49 Logical shift right 4 bit (X >> 4)
ld('.sysLsrw4a')                #16 Shift low byte
st([vTmp])                      #17
ld([vAC])                       #18
anda(0b11110000)                #19
ora( 0b00000111)                #20
jmp(Y,AC)                       #21
bra(255)                        #22 bra shiftTable+255
label('.sysLsrw4a')
st([vAC])                       #26
ld([vAC+1])                     #27 Transfer bit 8:11
adda(AC)                        #28
adda(AC)                        #29
adda(AC)                        #30
adda(AC)                        #31
ora([vAC])                      #32
st([vAC])                       #33
ld('.sysLsrw4b')                #34 Shift high byte'
st([vTmp])                      #35
ld([vAC+1])                     #36
anda(0b11110000)                #37
ora( 0b00000111)                #38
jmp(Y,AC)                       #39
bra(255)                        #40 bra shiftTable+255
label('.sysLsrw4b')
st([vAC+1])                     #44
ld(hi('REENTER'),Y)             #45
jmp(Y,'REENTER')                #46
ld(-50/2)                       #47

label('SYS_LSRW5_50')
ld(hi('shiftTable'),Y)          #15 Logical shift right 5 bit (X >> 5)
ld('.sysLsrw5a')                #16 Shift low byte
st([vTmp])                      #17
ld([vAC])                       #18
anda(0b11100000)                #19
ora( 0b00001111)                #20
jmp(Y,AC)                       #21
bra(255)                        #22 bra shiftTable+255
label('.sysLsrw5a')
st([vAC])                       #26
ld([vAC+1])                     #27 Transfer bit 8:13
adda(AC)                        #28
adda(AC)                        #29
adda(AC)                        #30
ora([vAC])                      #31
st([vAC])                       #32
ld('.sysLsrw5b')                #33 Shift high byte
st([vTmp])                      #34
ld([vAC+1])                     #35
anda(0b11100000)                #36
ora( 0b00001111)                #37
jmp(Y,AC)                       #38
bra(255)                        #39 bra shiftTable+255
label('.sysLsrw5b')
st([vAC+1])                     #44
ld(-50/2)                       #45
ld(hi('REENTER'),Y)             #46
jmp(Y,'REENTER')                #47
#nop()                          #48

label('SYS_LSRW6_48')
ld(hi('shiftTable'),Y)          #15,44 Logical shift right 6 bit (X >> 6)
ld('.sysLsrw6a')                #16 Shift low byte
st([vTmp])                      #17
ld([vAC])                       #18
anda(0b11000000)                #19
ora( 0b00011111)                #20
jmp(Y,AC)                       #21
bra(255)                        #22 bra shiftTable+255
label('.sysLsrw6a')
st([vAC])                       #26
ld([vAC+1])                     #27 Transfer bit 8:13
adda(AC)                        #28
adda(AC)                        #29
ora([vAC])                      #30
st([vAC])                       #31
ld('.sysLsrw6b')                #32 Shift high byte
st([vTmp])                      #33
ld([vAC+1])                     #34
anda(0b11000000)                #35
ora( 0b00011111)                #36
jmp(Y,AC)                       #37
bra(255)                        #38 bra shiftTable+255
label('.sysLsrw6b')
st([vAC+1])                     #42
ld(hi('REENTER'),Y)             #43
jmp(Y,'REENTER')                #44
ld(-48/2)                       #45

label('SYS_LSLW4_46')
ld(hi('shiftTable'),Y)          #15 Logical shift left 4 bit (X << 4)
ld('.sysLsrl4')                 #16
st([vTmp])                      #17
ld([vAC+1])                     #18
adda(AC)                        #19
adda(AC)                        #20
adda(AC)                        #21
adda(AC)                        #22
st([vAC+1])                     #23
ld([vAC])                       #24
anda(0b11110000)                #25
ora( 0b00000111)                #26
jmp(Y,AC)                       #27
bra(255)                        #28 bra shiftTable+255
label('.sysLsrl4')
ora([vAC+1])                    #32
st([vAC+1])                     #33
ld([vAC])                       #34
adda(AC)                        #35
adda(AC)                        #36
adda(AC)                        #37
adda(AC)                        #38
st([vAC])                       #39
ld(-46/2)                       #40
ld(hi('REENTER'),Y)             #41
jmp(Y,'REENTER')                #42
#nop()                          #43

#-----------------------------------------------------------------------
# Extension SYS_Read3_40
#-----------------------------------------------------------------------

# Read 3 consecutive bytes from ROM
#
# Note: This function a bit obsolete, as it has very limited use. It's
#       effectively an application-specific SYS function for the Pictures
#       application from ROM v1. It requires the ROM data be organized
#       with trampoline3a and trampoline3b fragments, and their address
#       in ROM to be known. Better avoid using this.
#
# Variables:
#       sysArgs[0:2]    Bytes (out)
#       sysArgs[6:7]    ROM pointer (in)

label('SYS_Read3_40')
ld([sysArgs+7],Y)               #15,32
jmp(Y,128-7)                    #16 trampoline3a
ld([sysArgs+6])                 #17
label('txReturn')
st([sysArgs+2])                 #34
ld(hi('REENTER'),Y)             #35
jmp(Y,'REENTER')                #36
ld(-40/2)                       #37

def trampoline3a():
  """Read 3 bytes from ROM page"""
  while pc()&255 < 128-7:
    nop()
  bra(AC)                       #18
  C('Trampoline for page $%02x00 reading (entry)' % (pc()>>8))
  bra(123)                      #19
  st([sysArgs+0])               #21
  ld([sysArgs+6])               #22
  adda(1)                       #23
  bra(AC)                       #24
  bra(250)                      #25 trampoline3b
  align(1, size=0x80)

def trampoline3b():
  """Read 3 bytes from ROM page (continue)"""
  while pc()&255 < 256-6:
    nop()
  st([sysArgs+1])               #27
  C('Trampoline for page $%02x00 reading (continue)' % (pc()>>8))
  ld([sysArgs+6])               #28
  adda(2)                       #29
  ld(hi('txReturn'),Y)          #30
  bra(AC)                       #31
  jmp(Y,'txReturn')             #32
  align(1, size=0x100)

#-----------------------------------------------------------------------
# Extension SYS_Unpack_56
#-----------------------------------------------------------------------

# Unpack 3 bytes into 4 pixels
#
# Variables:
#       sysArgs[0:2]    Packed bytes (in)
#       sysArgs[0:3]    Pixels (out)

label('SYS_Unpack_56')
ld(soundTable>>8,Y)             #15
ld([sysArgs+2])                 #16 a[2]>>2
ora(0x03,X)                     #17
ld([Y,X])                       #18
st([sysArgs+3])                 #19 -> Pixel 3

ld([sysArgs+2])                 #20 (a[2]&3)<<4
anda(0x03)                      #21
adda(AC)                        #22
adda(AC)                        #23
adda(AC)                        #24
adda(AC)                        #25
st([sysArgs+2])                 #26
ld([sysArgs+1])                 #27 | a[1]>>4
ora(0x03,X)                     #28
ld([Y,X])                       #29
ora(0x03,X)                     #30
ld([Y,X])                       #31
ora([sysArgs+2])                #32
st([sysArgs+2])                 #33 -> Pixel 2

ld([sysArgs+1])                 #34 (a[1]&15)<<2
anda(0x0f)                      #35
adda(AC)                        #36
adda(AC)                        #37
st([sysArgs+1])                 #38

ld([sysArgs+0])                 #39 | a[0]>>6
ora(0x03,X)                     #40
ld([Y,X])                       #41
ora(0x03,X)                     #42
ld([Y,X])                       #43
ora(0x03,X)                     #44
ld([Y,X])                       #45
ora([sysArgs+1])                #46
st([sysArgs+1])                 #47 -> Pixel 1

ld([sysArgs+0])                 #48 a[1]&63
anda(0x3f)                      #49
st([sysArgs+0])                 #50 -> Pixel 0

ld(hi('REENTER'),Y)             #51
jmp(Y,'REENTER')                #52
ld(-56/2)                       #53

#-----------------------------------------------------------------------
#       v6502 right shift instruction
#-----------------------------------------------------------------------

label('v6502_lsr#30')
ld([v6502_ADH],Y)               #30 Result
st([Y,X])                       #31
st([v6502_Qz])                  #32 Z flag
st([v6502_Qn])                  #33 N flag
ld(hi('v6502_next'),Y)          #34
ld(-38/2)                       #35
jmp(Y,'v6502_next')             #36
#nop()                          #37 Overlap
#
label('v6502_ror#38')
ld([v6502_ADH],Y)               #38,38 Result
ora([v6502_BI])                 #39 Transfer bit 8
st([Y,X])                       #40
st([v6502_Qz])                  #41 Z flag
st([v6502_Qn])                  #42 N flag
ld(hi('v6502_next'),Y)          #43
jmp(Y,'v6502_next')             #44
ld(-46/2)                       #45

#-----------------------------------------------------------------------
#       Reserved
#-----------------------------------------------------------------------

# XXX Reserve space for LSRW?

#-----------------------------------------------------------------------
#
#  $0700 ROM page 7-8: Gigatron font data
#
#-----------------------------------------------------------------------

align(0x100, size=0x100)

label('font32up')
for ch in range(32, 32+50):
  comment = 'Char %s' % repr(chr(ch))
  for byte in font.font[ch-32]:
    ld(byte)
    comment = C(comment)

trampoline()

#-----------------------------------------------------------------------

align(0x100, size=0x100)

label('font82up')
for ch in range(32+50, 132):
  comment = 'Char %s' % repr(chr(ch))
  for byte in font.font[ch-32]:
    ld(byte)
    comment = C(comment)

trampoline()

#-----------------------------------------------------------------------
#
#  $0900 ROM page 9: Key table for music
#
#-----------------------------------------------------------------------

align(0x100, size=0x100)
notes = 'CCDDEFFGGAAB'
sampleRate = cpuClock / 200.0 / 4
label('notesTable')
ld(0)
ld(0)
for i in range(0, 250, 2):
  j = i//2-1
  freq = 440.0*2.0**((j-57)/12.0)
  if j>=0 and freq <= sampleRate/2.0:
    key = int(round(32768 * freq / sampleRate))
    octave, note = j//12, notes[j%12]
    sharp = '-' if notes[j%12-1] != note else '#'
    comment = '%s%s%s (%0.1f Hz)' % (note, sharp, octave, freq)
    ld(key&127); C(comment); ld(key>>7)

trampoline()

#-----------------------------------------------------------------------
#
#  $0a00 ROM page 10: Inversion table
#
#-----------------------------------------------------------------------

align(0x100, size=0x100)
label('invTable')

# Unit 64, table offset 16 (=1/4), value offset 1: (x+16)*(y+1) == 64*64 - e
for i in range(251):
  ld(4096//(i+16)-1)

trampoline()

#-----------------------------------------------------------------------
#
#  $0d00 ROM page 11: More SYS functions
#
#-----------------------------------------------------------------------

align(0x100, size=0x100)

#-----------------------------------------------------------------------
# Extension SYS_SetMode_v2_80
#-----------------------------------------------------------------------

# Set video mode to 0 to 3 black scanlines per pixel line.
#
# Mainly for making the MODE command available in Tiny BASIC, so that
# the user can experiment. It's adviced to refrain from using
# SYS_SetMode_v2_80 in regular applications. Video mode is a deeply
# personal preference, and the programmer shouldn't overrule the user
# in that choice. The Gigatron philisophy is that the end user has
# the final say on what happens on the system, not the application,
# even if that implies a degraded performance. This doesn't mean that
# all applications must work well in all video modes: mode 1 is still
# the default. If an application really doesn't work at all in that
# mode, it's acceptable to change mode once after loading.
#
# There's no "SYS_GetMode" function.
#
# Variables:
#       vAC bit 0:1     Mode:
#                         0      "ABCD" -> Full mode (slowest)
#                         1      "ABC-" -> Default mode after reset
#                         2      "A-C-" -> at67's mode
#                         3      "A---" -> HGM's mode
#       vAC bit 2:15    Ignored bits and should be 0
#
# Special values (ROM v4):
#       vAC = 1975      Zombie mode (no video signals, no input,
#                        no blinkenlights).
#       vAC = -1        Leave zombie mode and restore previous mode.

# Actual duration is <80 cycles, but keep some room for future extensions
label('SYS_SetMode_v2_80')
ld(hi('sys_SetMode'),Y)         #15
jmp(Y,'sys_SetMode')            #16
ld([vReturn])                   #17

#-----------------------------------------------------------------------
# Extension SYS_SetMemory_v2_54
#-----------------------------------------------------------------------

# SYS function for setting 1..256 bytes
#
# sysArgs[0]   Copy count (in, changed)
# sysArgs[1]   Copy value (in)
# sysArgs[2:3] Destination address (in, changed)
#
# Sets up to 8 bytes per invocation before restarting itself through vCPU.
# Doesn't wrap around page boundary. Can run 3 times per 148-cycle time slice.
# All combined that gives a 300% speedup over ROMv4 and before.

label('SYS_SetMemory_v2_54')
ld([sysArgs+0])                 #15
bra('sys_SetMemory#18')         #16
ld([sysArgs+2],X)               #17

#-----------------------------------------------------------------------
# Extension SYS_SendSerial1_v3_80
#-----------------------------------------------------------------------

# SYS function for sending data over serial controller port using
# pulse width modulation of the vertical sync signal.
#
# Variables:
#       sysArgs[0:1]    Source address               (in, changed)
#       sysArgs[2]      Start bit mask (typically 1) (in, changed)
#       sysArgs[3]      Number of send frames X      (in, changed)
#
# The sending will abort if input data is detected on the serial port.
# Returns 0 in case of all bits sent, or <>0 in case of abort
#
# This modulates the next upcoming X vertical pulses with the supplied
# data. A zero becomes a 7 line vPulse, a one will be 9 lines.
# After that, the vPulse width falls back to 8 lines (idle).

label('SYS_SendSerial1_v3_80')
ld([videoY])                    #15
bra('sys_SendSerial1')          #16
xora(videoYline0)               #17 First line of vertical blank

#-----------------------------------------------------------------------
# Extension SYS_ExpanderControl_v4_40
#-----------------------------------------------------------------------

# Sets the I/O and RAM expander's control register
#
# Variables:
#       vAC bit 2       Device enable /SS0
#           bit 3       Device enable /SS1
#           bit 4       Device enable /SS2
#           bit 5       Device enable /SS3
#           bit 6       Banking B0
#           bit 7       Banking B1
#           bit 15      Data out MOSI
#       sysArgs[7]      Cache for control state (written to)
#
# Intended for prototyping, and probably too low-level for most applications
# Still there's a safeguard: it's not possible to disable RAM using this

label('SYS_ExpanderControl_v4_40')
ld(hi('sys_ExpanderControl'),Y) #15
jmp(Y,'sys_ExpanderControl')    #16
ld(0b00001100)                  #17
#    ^^^^^^^^
#    |||||||`-- SCLK
#    ||||||`--- Not connected
#    |||||`---- /SS0
#    ||||`----- /SS1
#    |||`------ /SS2 or /CPOL
#    ||`------- /SS3 or /ZPBANK
#    |`-------- B0
#    `--------- B1

#-----------------------------------------------------------------------
# Extension SYS_Run6502_v4_80
#-----------------------------------------------------------------------

# Transfer control to v6502
#
# Calling 6502 code from vCPU goes (only) through this SYS function.
# Directly modifying the vCpuSelect variable is unreliable. The
# control transfer is immediate, without waiting for the current
# time slice to end or first returning to vCPU.
#
# vCPU code and v6502 code can interoperate without much hassle:
# - The v6502 program counter is vLR, and v6502 doesn't touch vPC
# - Returning to vCPU is with the BRK instruction
# - BRK doesn't dump process state on the stack
# - vCPU can save/restore the vLR with PUSH/POP
# - Stacks are shared, vAC is shared
# - vAC can indicate what the v6502 code wants. vAC+1 will be cleared
# - Alternative is to leave a word in sysArgs[6:7] (v6502 X and Y registers)
# - Another way is to set vPC before BRK, and vCPU will continue there(+2)
#
# Calling v6502 code from vCPU looks like this:
#       LDWI  SYS_Run6502_v4_80
#       STW   sysFn
#       LDWI  $6502_start_address
#       STW   vLR
#       SYS   80
#
# Variables:
#       vAC             Accumulator
#       vLR             Program Counter
#       vSP             Stack Pointer (+1)
#       sysArgs[6]      Index Register X
#       sysArgs[7]      Index Register Y
# For info:
#       sysArgs[0:1]    Address Register, free to clobber
#       sysArgs[2]      Instruction Register, free to clobber
#       sysArgs[3:5]    Flags, don't touch
#
# Implementation details::
#
#  The time to reserve for this transition is the maximum time
#  between NEXT and v6502_check. This is
#       SYS call duration + 2*v6502_maxTicks + (v6502_overhead - vCPU_overhead)
#     = 22 + 28 + (11 - 9) = 62 cycles.
#  So reserving 80 cycles is future proof. This isn't overhead, as it includes
#  the fetching of the first 6502 opcode and its operands..
#
#                      0            10                 28=0         9
#    ---+----+---------+------------+------------------+-----------+---
# video | nop| runVcpu |   ENTER    | At least one ins |   EXIT    | video
#    ---+----+---------+------------+------------------+-----------+---
#        sync  prelude  ENTER-to-ins    ins-to-NEXT     NEXT-to-video
#       |<-->|
#        0/1 |<------->|
#                 5    |<----------------------------->|
#          runVCpu_overhead           28               |<--------->|
#                                 2*maxTicks                 9
#                                                      vCPU_overhead
#
#                      0                21                    38=0       11
#    ---+----+---------+----------------+--------------------+-----------+---
# video | nop| runVcpu |   v6502_ENTER  | At least one fetch |v6502_exitB| video
#    ---+----+---------+----------------+--------------------+-----------+---
#        sync  prelude   enter-to-fetch     fetch-to-check    check-to-video
#       |<-->|
#        0/1 |<------->|
#                 5    |<----------------------------------->|
#          runVcpu_overhead           38                     |<--------->|
#                              2*v6520_maxTicks                    11
#                                                            v6502_overhead

label('SYS_Run6502_v4_80')
ld(hi('sys_v6502'),Y)           #15
jmp(Y,'sys_v6502')              #16
ld(hi('v6502_ENTER'))           #17 Activate v6502

#-----------------------------------------------------------------------
# Extension SYS_ResetWaveforms_v4_50
#-----------------------------------------------------------------------

# soundTable[4x+0] = sawtooth, to be modified into metallic/noise
# soundTable[4x+1] = pulse
# soundTable[4x+2] = triangle
# soundTable[4x+3] = sawtooth, also useful to right shift 2 bits

label('SYS_ResetWaveforms_v4_50')
ld(hi('sys_ResetWaveforms'),Y)  #15 Initial setup of waveforms. [vAC+0]=i
jmp(Y,'sys_ResetWaveforms')     #16
ld(soundTable>>8,Y)             #17

#-----------------------------------------------------------------------
# Extension SYS_ShuffleNoise_v4_46
#-----------------------------------------------------------------------

# Use simple 6-bits variation of RC4 to permutate waveform 0 in soundTable

label('SYS_ShuffleNoise_v4_46')
ld(hi('sys_ShuffleNoise'),Y)    #15 Shuffle soundTable[4i+0]. [vAC+0]=4j, [vAC+1]=4i
jmp(Y,'sys_ShuffleNoise')       #16
ld(soundTable>>8,Y)             #17

#-----------------------------------------------------------------------
# Extension SYS_SpiExchangeBytes_v4_134
#-----------------------------------------------------------------------

# Send AND receive 1..256 bytes over SPI interface

# Variables:
#       sysArgs[0]      Page index start, for both send/receive (in, changed)
#       sysArgs[1]      Memory page for send data (in)
#       sysArgs[2]      Page index stop (in)
#       sysArgs[3]      Memory page for receive data (in)
#       sysArgs[4]      Scratch (changed)

label('SYS_SpiExchangeBytes_v4_134')
ld(hi('sys_SpiExchangeBytes'),Y)#15
jmp(Y,'sys_SpiExchangeBytes')   #16
ld(hi(ctrlBits),Y)              #17 Control state as saved by SYS_ExpanderControl


#-----------------------------------------------------------------------
# Extension SYS_ReceiveSerial1_v6_32
#-----------------------------------------------------------------------

# SYS function for receiving one byte over the serial controller port.
# This is a public version of SYS_NextByteIn from the loader private
# extension.  A byte is read from IN when videoY reaches
# sysArgs[3]. The byte is added to the checksum sysArgs[2] then stored
# at address sysArgs[0:1] which gets incremented.
#
# The 65 bytes of a serial frame can be read for the following values
# of videoY: 207 (protocol byte) 219 (length, 6 bits only) 235, 251
# (address) then 2, 6, 10, .. 238 stepping by four, then 185.
#
# Variables:
#     sysArgs[0:1] Address
#     sysArgs[2]   Checksum
#     sysArgs[3]   Wait value (videoY)

label('SYS_ReceiveSerial1_v6_32')
bra('sys_ReceiveSerial1')       #15
ld([sysArgs+3])                 #16

#-----------------------------------------------------------------------
#  Implementations
#-----------------------------------------------------------------------

# SYS_SetMemory_54 implementation
label('sys_SetMemory#18')
ld([sysArgs+3],Y)               #18
ble('.sysSb#21')                #19 Enter fast lane if >=128 or at 0 (-> 256)
suba(8)                         #20
bge('.sysSb#23')                #21 Or when >=8
st([sysArgs+0])                 #22
anda(4)                         #23
beq('.sysSb#26')                #24
ld([sysArgs+1])                 #25 Set 4 pixels
st([Y,Xpp])                     #26
st([Y,Xpp])                     #27
st([Y,Xpp])                     #28
bra('.sysSb#31')                #29
st([Y,Xpp])                     #30
label('.sysSb#26')
wait(31-26)                     #26
label('.sysSb#31')
ld([sysArgs+0])                 #31
anda(2)                         #32
beq('.sysSb#35')                #33
ld([sysArgs+1])                 #34 Set 2 pixels
st([Y,Xpp])                     #35
bra('.sysSb#38')                #36
st([Y,Xpp])                     #37
label('.sysSb#35')
wait(38-35)                     #35
label('.sysSb#38')
ld([sysArgs+0])                 #38
anda(1)                         #39
beq(pc()+3)                     #40
bra(pc()+3)                     #41
ld([sysArgs+1])                 #42 Set 1 pixel
ld([Y,X])                       #42(!) No change
st([Y,X])                       #43
ld(hi('NEXTY'),Y)               #44 Return
jmp(Y,'NEXTY')                  #45 All done
ld(-48/2)                       #46
label('.sysSb#21')
nop()                           #21
st([sysArgs+0])                 #22
label('.sysSb#23')
ld([sysArgs+1])                 #23 Set 8 pixels
st([Y,Xpp])                     #24
st([Y,Xpp])                     #25
st([Y,Xpp])                     #26
st([Y,Xpp])                     #27
st([Y,Xpp])                     #28
st([Y,Xpp])                     #29
st([Y,Xpp])                     #30
st([Y,Xpp])                     #31
ld([sysArgs+2])                 #32 Advance write pointer
adda(8)                         #33
st([sysArgs+2])                 #34
ld([sysArgs+0])                 #35
beq(pc()+3)                     #36
bra(pc()+3)                     #37
ld(-2)                          #38 Self-restart when more to do
ld(0)                           #38(!)
adda([vPC])                     #39
st([vPC])                       #40
ld(hi('REENTER'),Y)             #41
jmp(Y,'REENTER')                #42
ld(-46/2)                       #43

# SYS_SetMode_80 implementation
label('sys_SetMode')
bne(pc()+3)                     #18
bra(pc()+2)                     #19
ld('startVideo')                #20 First enable video if disabled
st([vReturn])                   #20,21
ld([vAC+1])                     #22
beq('.sysSm#25')                #23
ld(hi('REENTER'),Y)             #24
xora([vAC])                     #25
xora((1975>>8)^(1975&255))      #26 Poor man\'s 1975 detection
bne(pc()+3)                     #27
bra(pc()+3)                     #28
assert videoZ == 0x0100
st([vReturn])                   #29 DISABLE video/audio/serial/etc
nop()                           #29(!) Ignore and return
jmp(Y,'REENTER')                #30
ld(-34/2)                       #31
label('.sysSm#25')
ld([vAC])                       #25 Mode 0,1,2,3
anda(3)                         #26
adda('.sysSm#30')               #27
bra(AC)                         #28
bra('.sysSm#31')                #29
label('.sysSm#30')
ld('pixels')                    #30 videoB lines
ld('pixels')                    #30
ld('nopixels')                  #30
ld('nopixels')                  #30
label('.sysSm#31')
st([videoModeB])                #31
ld([vAC])                       #32
anda(3)                         #33
adda('.sysSm#37')               #34
bra(AC)                         #35
bra('.sysSm#38')                #36
label('.sysSm#37')
ld('pixels')                    #37 videoC lines
ld('pixels')                    #37
ld('pixels')                    #37
ld('nopixels')                  #37
label('.sysSm#38')
if WITH_512K_BOARD:
  nop()                           #38
else:
  st([videoModeC])                #38
ld([vAC])                       #39
anda(3)                         #40
adda('.sysSm#44')               #41
bra(AC)                         #42
bra('.sysSm#45')                #43
label('.sysSm#44')
ld('pixels')                    #44 videoD lines
ld('nopixels')                  #44
ld('nopixels')                  #44
ld('nopixels')                  #44
label('.sysSm#45')
st([videoModeD])                #45
jmp(Y,'REENTER')                #46
ld(-50/2)                       #47

# SYS_SendSerial1_v3_80 implementation
label('sys_SendSerial1')
beq('.sysSs#20')                #18
ld([sysArgs+0],X)               #19
ld([vPC])                       #20 Wait for vBlank
suba(2)                         #21
ld(hi('REENTER_28'),Y)          #22
jmp(Y,'REENTER_28')             #23
st([vPC])                       #24
label('.sysSs#20')
ld([sysArgs+1],Y)               #20 Synchronized with vBlank
ld([Y,X])                       #21 Copy next bit
anda([sysArgs+2])               #22
bne(pc()+3)                     #23
bra(pc()+3)                     #24
ld(7*2)                         #25
ld(9*2)                         #25
st([videoPulse])                #26
ld([sysArgs+2])                 #27 Rotate input bit
adda(AC)                        #28
bne(pc()+3)                     #29
bra(pc()+2)                     #30
ld(1)                           #31
st([sysArgs+2])                 #31,32 (must be idempotent)
anda(1)                         #33 Optionally increment pointer
adda([sysArgs+0])               #34
st([sysArgs+0],X)               #35
ld([sysArgs+3])                 #36 Frame counter
suba(1)                         #37
beq('.sysSs#40')                #38
ld(hi('REENTER'),Y)             #39
st([sysArgs+3])                 #40
ld([serialRaw])                 #41 Test for anything being sent back
xora(255)                       #42
beq('.sysSs#45')                #43
st([vAC])                       #44 Abort after key press with non-zero error
st([vAC+1])                     #45
jmp(Y,'REENTER')                #46
ld(-50/2)                       #47
label('.sysSs#45')
ld([vPC])                       #45 Continue sending bits
suba(2)                         #46
st([vPC])                       #47
jmp(Y,'REENTER')                #48
ld(-52/2)                       #49
label('.sysSs#40')
st([vAC])                       #40 Stop sending bits, no error
st([vAC+1])                     #41
jmp(Y,'REENTER')                #42
ld(-46/2)                       #43

# SYS_ReceiveSerialByte implementation
label('sys_ReceiveSerial1')
xora([videoY])                  #17
bne('.sysRsb#20')               #18
ld([sysArgs+0],X)               #19
ld([sysArgs+1],Y)               #20
ld(IN)                          #21
st([Y,X])                       #22
adda([sysArgs+2])               #23
st([sysArgs+2])                 #24
ld([sysArgs+0])                 #25
adda(1)                         #26
st([sysArgs+0])                 #27
ld(hi('NEXTY'),Y)               #28
jmp(Y,'NEXTY')                  #29
ld(-32/2)                       #30
# Restart the instruction in the next timeslice
label('.sysRsb#20')
ld([vPC])                       #20
suba(2)                         #21
st([vPC])                       #22
ld(hi('REENTER'),Y)             #23
jmp(Y,'REENTER')                #24
ld(-28/2)                       #25

# CALLI implementation (vCPU instruction)
label('calli#13')
adda(3)                         #13,43
st([vLR])                       #14
ld([vPC+1])                     #15
st([vLR+1],Y)                   #16
ld([Y,X])                       #17
st([Y,Xpp])                     #18 Just X++
suba(2)                         #19
st([vPC])                       #20
ld([Y,X])                       #21
ld(hi('REENTER_28'),Y)          #22
jmp(Y,'REENTER_28')             #23
st([vPC+1])                     #24

# -------------------------------------------------------------
# vCPU instructions for comparisons between two 16-bit operands
# -------------------------------------------------------------
#
# vCPU's conditional branching (BCC) always compares vAC against 0,
# treating vAC as a two's complement 16-bit number. When we need to
# compare two arbitrary numnbers we normally first take their difference
# with SUBW.  However, when this difference is too large, the subtraction
# overflows and we get the wrong outcome. To get it right over the
# entire range, an elaborate sequence is needed. TinyBASIC uses this
# blurp for its relational operators. (It compares stack variable $02
# with zero page variable $3a.)
#
#       0461  ee 02            LDLW  $02
#       0463  fc 3a            XORW  $3a
#       0465  35 53 6a         BGE   $046c
#       0468  ee 02            LDLW  $02
#       046a  90 6e            BRA   $0470
#       046c  ee 02            LDLW  $02
#       046e  b8 3a            SUBW  $3a
#       0470  35 56 73         BLE   $0475
#
# The CMPHS and CMPHU instructions were introduced to simplify this.
# They inspect both operands to see if there is an overflow risk. If
# so, they modify vAC such that their difference gets smaller, while
# preserving the relation between the two operands. After that, the
# SUBW instruction can't overflow and we achieve a correct comparison.
# Use CMPHS for signed comparisons and CMPHU for unsigned. With these,
# the sequence above becomes:
#
#       0461  ee 02            LDLW  $02
#       0463  1f 3b            CMPHS $3b        Note: high byte of operand
#       0465  b8 3a            SUBW  $3a
#       0467  35 56 73         BLE   $0475
#
# CMPHS/CMPHU don't make much sense other than in combination with
# SUBW. These modify vACH, if needed, as given in the following table:
#
#       vACH  varH  |     vACH
#       bit7  bit7  | CMPHS  CMPHU
#       ---------------------------
#         0     0   |  vACH   vACH      no change needed
#         0     1   | varH+1 varH-1     narrowing the range
#         1     0   | varH-1 varH+1     narrowing the range
#         1     1   |  vACH   vACH      no change needed
#       ---------------------------

# CMPHS implementation (vCPU instruction)
label('cmphs#13')
ld(hi('REENTER'),Y)             #13
ld([X])                         #14
xora([vAC+1])                   #15
bpl('.cmphu#18')                #16 Skip if same sign
ld([vAC+1])                     #17
bmi(pc()+3)                     #18
bra(pc()+3)                     #19
label('.cmphs#20')
ld(+1)                          #20    vAC < variable
ld(-1)                          #20(!) vAC > variable
label('.cmphs#21')
adda([X])                       #21
st([vAC+1])                     #22
jmp(Y,'REENTER_28')             #23
#dummy()                        #24 Overlap
#
# CMPHS implementation (vCPU instruction)
label('cmphu#13')
ld(hi('REENTER'),Y)             #13,24
ld([X])                         #14
xora([vAC+1])                   #15
bpl('.cmphu#18')                #16 Skip if same sign
ld([vAC+1])                     #17
bmi('.cmphs#20')                #18
bra('.cmphs#21')                #19
ld(-1)                          #20    vAC > variable

# No-operation for CMPHS/CMPHU when high bits are equal
label('.cmphu#18')
jmp(Y,'REENTER')                #18
ld(-22/2)                       #19

#-----------------------------------------------------------------------
#
#  $0c00 ROM page 12: More SYS functions (sprites)
#
#       Page 1: vertical blank interval
#       Page 2: visible scanlines
#
#-----------------------------------------------------------------------

align(0x100, size=0x100)

#-----------------------------------------------------------------------
# Extension SYS_Sprite6_v3_64
# Extension SYS_Sprite6x_v3_64
# Extension SYS_Sprite6y_v3_64
# Extension SYS_Sprite6xy_v3_64
#-----------------------------------------------------------------------

# Blit sprite in screen memory
#
# Variables
#       vAC             Destination address in screen
#       sysArgs[0:1]    Source address of 6xY pixels (colors 0..63) terminated
#                       by negative byte value N (typically N = -Y)
#       sysArgs[2:7]    Scratch (user as copy buffer)
#
# This SYS function draws a sprite of 6 pixels wide and Y pixels high.
# The pixel data is read sequentually from RAM, in horizontal chunks
# of 6 pixels at a time, and then written to the screen through the
# destination pointer (each chunk underneath the previous), thus
# drawing a 6xY stripe. Pixel values should be non-negative. The first
# negative byte N after a chunk signals the end of the sprite data.
# So the sprite's height Y is determined by the source data and is
# therefore flexible. This negative byte value, typically N == -Y,
# is then used to adjust the destination pointer's high byte, to make
# it easier to draw sprites wider than 6 pixels: just repeat the SYS
# call for as many 6-pixel wide stripes you need. All arguments are
# already left in place to facilitate this. After one call, the source
# pointer will point past that source data, effectively:
#       src += Y * 6 + 1
# The destination pointer will have been adjusted as:
#       dst += (Y + N) * 256 + 6
# (With arithmetic wrapping around on the same memory page)
#
# Y is only limited by source memory, not by CPU cycles. The
# implementation is such that the SYS function self-repeats, each
# time drawing the next 6-pixel chunk. It can typically draw 12
# pixels per scanline this way.

label('SYS_Sprite6_v3_64')

ld([sysArgs+0],X)               #15 Pixel data source address
ld([sysArgs+1],Y)               #16
ld([Y,X])                       #17 Next pixel or stop
bpl('.sysDpx0')                 #18
st([Y,Xpp])                     #19 Just X++

adda([vAC+1])                   #20 Adjust dst for convenience
st([vAC+1])                     #21
ld([vAC])                       #22
adda(6)                         #23
st([vAC])                       #24
ld([sysArgs+0])                 #25 Adjust src for convenience
adda(1)                         #26
st([sysArgs+0])                 #27
nop()                           #28
ld(hi('REENTER'),Y)             #29 Normal exit (no self-repeat)
jmp(Y,'REENTER')                #30
ld(-34/2)                       #31

label('.sysDpx0')
st([sysArgs+2])                 #20 Gobble 6 pixels into buffer
ld([Y,X])                       #21
st([Y,Xpp])                     #22 Just X++
st([sysArgs+3])                 #23
ld([Y,X])                       #24
st([Y,Xpp])                     #25 Just X++
st([sysArgs+4])                 #26
ld([Y,X])                       #27
st([Y,Xpp])                     #28 Just X++
st([sysArgs+5])                 #29
ld([Y,X])                       #30
st([Y,Xpp])                     #31 Just X++
st([sysArgs+6])                 #32
ld([Y,X])                       #33
st([Y,Xpp])                     #34 Just X++
st([sysArgs+7])                 #35

ld([vAC],X)                     #36 Screen memory destination address
ld([vAC+1],Y)                   #37
ld([sysArgs+2])                 #38 Write 6 pixels
st([Y,Xpp])                     #39
ld([sysArgs+3])                 #40
st([Y,Xpp])                     #41
ld([sysArgs+4])                 #42
st([Y,Xpp])                     #43
ld([sysArgs+5])                 #44
st([Y,Xpp])                     #45
ld([sysArgs+6])                 #46
st([Y,Xpp])                     #47
ld([sysArgs+7])                 #48
st([Y,Xpp])                     #49

ld([sysArgs+0])                 #50 src += 6
adda(6)                         #51
st([sysArgs+0])                 #52
ld([vAC+1])                     #53 dst += 256
adda(1)                         #54
st([vAC+1])                     #55

ld([vPC])                       #56 Self-repeating SYS call
suba(2)                         #57
st([vPC])                       #58
ld(hi('REENTER'),Y)             #59
jmp(Y,'REENTER')                #60
ld(-64/2)                       #61

align(64)
label('SYS_Sprite6x_v3_64')

ld([sysArgs+0],X)               #15 Pixel data source address
ld([sysArgs+1],Y)               #16
ld([Y,X])                       #17 Next pixel or stop
bpl('.sysDpx1')                 #18
st([Y,Xpp])                     #19 Just X++

adda([vAC+1])                   #20 Adjust dst for convenience
st([vAC+1])                     #21
ld([vAC])                       #22
suba(6)                         #23
st([vAC])                       #24
ld([sysArgs+0])                 #25 Adjust src for convenience
adda(1)                         #26
st([sysArgs+0])                 #27
nop()                           #28
ld(hi('REENTER'),Y)             #29 Normal exit (no self-repeat)
jmp(Y,'REENTER')                #30
ld(-34/2)                       #31

label('.sysDpx1')
st([sysArgs+7])                 #20 Gobble 6 pixels into buffer (backwards)
ld([Y,X])                       #21
st([Y,Xpp])                     #22 Just X++
st([sysArgs+6])                 #23
ld([Y,X])                       #24
st([Y,Xpp])                     #25 Just X++
st([sysArgs+5])                 #26
ld([Y,X])                       #27
st([Y,Xpp])                     #28 Just X++
st([sysArgs+4])                 #29
ld([Y,X])                       #30
st([Y,Xpp])                     #31 Just X++
st([sysArgs+3])                 #32
ld([Y,X])                       #33
st([Y,Xpp])                     #34 Just X++

ld([vAC],X)                     #35 Screen memory destination address
ld([vAC+1],Y)                   #36
st([Y,Xpp])                     #37 Write 6 pixels
ld([sysArgs+3])                 #38
st([Y,Xpp])                     #39
ld([sysArgs+4])                 #40
st([Y,Xpp])                     #41
ld([sysArgs+5])                 #42
st([Y,Xpp])                     #43
ld([sysArgs+6])                 #44
st([Y,Xpp])                     #45
ld([sysArgs+7])                 #46
st([Y,Xpp])                     #47

ld([sysArgs+0])                 #48 src += 6
adda(6)                         #49
st([sysArgs+0])                 #50
ld([vAC+1])                     #51 dst += 256
adda(1)                         #52
st([vAC+1])                     #53

ld([vPC])                       #54 Self-repeating SYS call
suba(2)                         #55
st([vPC])                       #56
ld(hi('REENTER'),Y)             #57
jmp(Y,'REENTER')                #58
ld(-62/2)                       #59

align(64)
label('SYS_Sprite6y_v3_64')

ld([sysArgs+0],X)               #15 Pixel data source address
ld([sysArgs+1],Y)               #16
ld([Y,X])                       #17 Next pixel or stop
bpl('.sysDpx2')                 #18
st([Y,Xpp])                     #19 Just X++

xora(255)                       #20 Adjust dst for convenience
adda(1)                         #21
adda([vAC+1])                   #22
st([vAC+1])                     #23
ld([vAC])                       #24
adda(6)                         #25
st([vAC])                       #26
ld([sysArgs+0])                 #27 Adjust src for convenience
adda(1)                         #28
st([sysArgs+0])                 #29
nop()                           #30
ld(hi('REENTER'),Y)             #31 Normal exit (no self-repeat)
jmp(Y,'REENTER')                #32
ld(-36/2)                       #33

label('.sysDpx2')
st([sysArgs+2])                 #20 Gobble 6 pixels into buffer
ld([Y,X])                       #21
st([Y,Xpp])                     #22 Just X++
st([sysArgs+3])                 #23
ld([Y,X])                       #24
st([Y,Xpp])                     #25 Just X++
st([sysArgs+4])                 #26
ld([Y,X])                       #27
st([Y,Xpp])                     #28 Just X++
st([sysArgs+5])                 #29
ld([Y,X])                       #30
st([Y,Xpp])                     #31 Just X++
st([sysArgs+6])                 #32
ld([Y,X])                       #33
st([Y,Xpp])                     #34 Just X++
st([sysArgs+7])                 #35

ld([vAC],X)                     #36 Screen memory destination address
ld([vAC+1],Y)                   #37
ld([sysArgs+2])                 #38 Write 6 pixels
st([Y,Xpp])                     #39
ld([sysArgs+3])                 #40
st([Y,Xpp])                     #41
ld([sysArgs+4])                 #42
st([Y,Xpp])                     #43
ld([sysArgs+5])                 #44
st([Y,Xpp])                     #45
ld([sysArgs+6])                 #46
st([Y,Xpp])                     #47
ld([sysArgs+7])                 #48
st([Y,Xpp])                     #49

ld([sysArgs+0])                 #50 src += 6
adda(6)                         #51
st([sysArgs+0])                 #52
ld([vAC+1])                     #53 dst -= 256
suba(1)                         #54
st([vAC+1])                     #55

ld([vPC])                       #56 Self-repeating SYS call
suba(2)                         #57
st([vPC])                       #58
ld(hi('REENTER'),Y)             #59
jmp(Y,'REENTER')                #60
ld(-64/2)                       #61

align(64)
label('SYS_Sprite6xy_v3_64')

ld([sysArgs+0],X)               #15 Pixel data source address
ld([sysArgs+1],Y)               #16
ld([Y,X])                       #17 Next pixel or stop
bpl('.sysDpx3')                 #18
st([Y,Xpp])                     #19 Just X++

xora(255)                       #20 Adjust dst for convenience
adda(1)                         #21
adda([vAC+1])                   #22
st([vAC+1])                     #23
ld([vAC])                       #24
suba(6)                         #25
st([vAC])                       #26
ld([sysArgs+0])                 #27 Adjust src for convenience
adda(1)                         #28
st([sysArgs+0])                 #29
nop()                           #30
ld(hi('REENTER'),Y)             #31 Normal exit (no self-repeat)
jmp(Y,'REENTER')                #32
ld(-36/2)                       #33

label('.sysDpx3')
st([sysArgs+7])                 #20 Gobble 6 pixels into buffer (backwards)
ld([Y,X])                       #21
st([Y,Xpp])                     #22 Just X++
st([sysArgs+6])                 #23
ld([Y,X])                       #24
st([Y,Xpp])                     #25 Just X++
st([sysArgs+5])                 #26
ld([Y,X])                       #27
st([Y,Xpp])                     #28 Just X++
st([sysArgs+4])                 #29
ld([Y,X])                       #30
st([Y,Xpp])                     #31 Just X++
st([sysArgs+3])                 #32
ld([Y,X])                       #33
st([Y,Xpp])                     #34 Just X++

ld([vAC],X)                     #35 Screen memory destination address
ld([vAC+1],Y)                   #36
st([Y,Xpp])                     #37 Write 6 pixels
ld([sysArgs+3])                 #38
st([Y,Xpp])                     #39
ld([sysArgs+4])                 #40
st([Y,Xpp])                     #41
ld([sysArgs+5])                 #42
st([Y,Xpp])                     #43
ld([sysArgs+6])                 #44
st([Y,Xpp])                     #45
ld([sysArgs+7])                 #46
st([Y,Xpp])                     #47

ld([sysArgs+0])                 #48 src += 6
adda(6)                         #49
st([sysArgs+0])                 #50
ld([vAC+1])                     #51 dst -= 256
suba(1)                         #52
st([vAC+1])                     #53

ld([vPC])                       #54 Self-repeating SYS call
suba(2)                         #55
st([vPC])                       #56
ld(hi('REENTER'),Y)             #57
jmp(Y,'REENTER')                #58
ld(-62/2)                       #59

#-----------------------------------------------------------------------

align(0x100)

label('sys_ExpanderControl')
ld(hi(ctrlBits),Y)                  #18
anda([vAC])                         #19 check for special ctrl code space
beq('sysEx#22')                     #20
ld([vAC])                           #21 load low byte of ctrl code in delay slot
anda(0xfc)                          #22 sanitize normal ctrl code
st([Y,ctrlBits])                    #23 store in ctrlBits
if WITH_512K_BOARD:
  ld(AC,X)                            #24
  ld([vAC+1],Y)                       #25
  ctrl(Y,X)                           #26 issue ctrl code
  label('sysEx#27') 
  ld(hi('REENTER'),Y)                 #27
  jmp(Y,'REENTER')                    #28
  ld(-32/2)                           #29
  label('sysEx#22')
  anda(0xfc,X)                        #22 special ctrl code
  ld([vAC+1],Y)                       #23
  xora(0xf0)                          #24
  bne('sysEx#27')                     #25
  ctrl(Y,X)                           #26 issue ctrl code
  ld(hi('sysEx#30'),Y)                #27
  jmp(Y,'sysEx#30')                   #28 jump to a place with more space
  ld([vAC+1])                         #29
elif WITH_128K_BOARD:
  st([ctrlBitsCopy],X)                #24
  anda(0x3c)                          #25
  ora(0x40)                           #26
  st([ctrlBitsVideo])                 #27
  label('sysEx#28')
  ld([vAC+1],Y)                       #28
  ctrl(Y,X)                           #29 issue ctrl code
  ld([ctrlBitsCopy])                  #30 always read after ctrl
  ld(hi('REENTER'),Y)                 #31
  jmp(Y,'REENTER')                    #32
  ld(-36/2)                           #33
  label('sysEx#22')
  anda(0xfc,X)                        #22 special ctrl code
  ld([vAC+1],Y)                       #23
  ctrl(Y,X)                           #24 issue special code
  ld([ctrlBitsCopy],X)                #25 from last time (hopefully)
  bra('sysEx#28')                     #26
  nop()                               #27
else:
  st([vTmp])                          #24 store in vTmp
  bra('sysEx#27')                     #25 jump to issuing normal ctrl code
  ld([vAC+1],Y)                       #26 load high byte of ctrl code in delay slot
  label('sysEx#22')
  anda(0xfc,X)                        #22 * special ctrl code
  ld([Y,ctrlBits])                    #23 get previous normal code from ctrlBits
  st([vTmp])                          #24 save it in vTmp
  ld([vAC+1],Y)                       #25 load high byte of ctrl code
  ctrl(Y,X)                           #26 issue special ctrl code
  label('sysEx#27')
  ld([vTmp])                          #27 load saved normal ctrl code
  anda(0xfc,X)                        #28 sanitize ctrlBits
  ctrl(Y,X)                           #29 issue normal ctrl code
  ld([vTmp])                          #30 always load something after ctrl
  ld(hi('REENTER'),Y)                 #31
  jmp(Y,'REENTER')                    #32
  ld(-36/2)                           #33

  
#-----------------------------------------------------------------------

label('sys_SpiExchangeBytes')

ld([Y,ctrlBits])                #18
st([sysArgs+4])                 #19

ld([sysArgs+0],X)               #20 Fetch byte to send
ld([sysArgs+1],Y)               #21
ld([Y,X])                       #22

for i in range(8):
  st([vTmp],Y);C('Bit %d'%(7-i))#23+i*12
  ld([sysArgs+4],X)             #24+i*12
  ctrl(Y,Xpp)                   #25+i*12 Set MOSI
  ctrl(Y,Xpp)                   #26+i*12 Raise SCLK, disable RAM!
  ld([0])                       #27+i*12 Get MISO
  if WITH_NOVATRON_PATCH:
    anda(0b00000011)            #28+i*12 Novatron only drives bits 0 and 1
  else:
    anda(0b00001111)            #28+i*12 This is why R1 as pull-DOWN is simpler
  beq(pc()+3)                   #29+i*12
  bra(pc()+2)                   #30+i*12
  ld(1)                         #31+i*12
  ctrl(Y,X)                     #32+i*12,29+i*12 (Must be idempotent) Lower SCLK
  adda([vTmp])                  #33+i*12 Shift
  adda([vTmp])                  #34+i*12

ld([sysArgs+0],X)               #119 Store received byte
ld([sysArgs+3],Y)               #120
st([Y,X])                       #121

ld([sysArgs+0])                 #122 Advance pointer
adda(1)                         #123
st([sysArgs+0])                 #124

xora([sysArgs+2])               #125 Reached end?
beq('.sysSpi#128')              #126

ld([vPC])                       #127 Self-repeating SYS call
suba(2)                         #128
st([vPC])                       #129
ld(hi('NEXTY'),Y)               #130
jmp(Y,'NEXTY')                  #131
ld(-134/2)                      #132

label('.sysSpi#128')
ld(hi('NEXTY'),Y)               #128 Continue program
jmp(Y,'NEXTY')                  #129
ld(-132/2)                      #130

#-----------------------------------------------------------------------

label('sys_v6502')

st([vCpuSelect],Y)              #18 Activate v6502
ld(-22/2)                       #19
jmp(Y,'v6502_ENTER')            #20 Transfer control in the same time slice
adda([vTicks])                  #21
assert (38 - 22)//2 >= v6502_adjust

#-----------------------------------------------------------------------
#       MOS 6502 emulator
#-----------------------------------------------------------------------

# Some quirks:
# - Stack in zero page instead of page 1
# - No interrupts
# - No decimal mode (may never be added). D flag is emulated but ignored.
# - BRK switches back to running 16-bits vCPU
# - Illegal opcodes map to BRK, but can read ghost operands before trapping
# - Illegal opcode $ff won't be trapped and cause havoc instead

# Big things TODO:
# XXX Tuning, put most frequent instructions in the primary page

label('v6502_ror')
assert v6502_Cflag == 1
ld([v6502_ADH],Y)               #12
ld(-46//2+v6502_maxTicks)       #13 Is there enough time for the excess ticks?
adda([vTicks])                  #14
blt('.recheck17')               #15
ld([v6502_P])                   #16 Transfer C to "bit 8"
anda(1)                         #17
adda(127)                       #18
anda(128)                       #19
st([v6502_BI])                  #20 The real 6502 wouldn't use BI for this
ld([v6502_P])                   #21 Transfer bit 0 to C
anda(~1)                        #22
st([v6502_P])                   #23
ld([Y,X])                       #24
anda(1)                         #25
ora([v6502_P])                  #26
st([v6502_P])                   #27
ld('v6502_ror#38')              #28 Shift table lookup
st([vTmp])                      #29
ld([Y,X])                       #30
anda(~1)                        #31
ld(hi('shiftTable'),Y)          #32
jmp(Y,AC)                       #33
bra(255)                        #34 bra shiftTable+255
label('.recheck17')
ld(hi('v6502_check'),Y)         #17 Go back to time check before dispatch
jmp(Y,'v6502_check')            #18
ld(-20/2)                       #19

label('v6502_lsr')
assert v6502_Cflag == 1
ld([v6502_ADH],Y)               #12
ld([v6502_P])                   #13 Transfer bit 0 to C
anda(~1)                        #14
st([v6502_P])                   #15
ld([Y,X])                       #16
anda(1)                         #17
ora([v6502_P])                  #18
st([v6502_P])                   #19
ld('v6502_lsr#30')              #20 Shift table lookup
st([vTmp])                      #21
ld([Y,X])                       #22
anda(~1)                        #23
ld(hi('shiftTable'),Y)          #24
jmp(Y,AC)                       #25
bra(255)                        #26 bra shiftTable+255

label('v6502_rol')
assert v6502_Cflag == 1
ld([v6502_ADH],Y)               #12
ld([Y,X])                       #13
anda(0x80)                      #14
st([v6502_Tmp])                 #15
ld([v6502_P])                   #16
anda(1)                         #17
label('.rol#18')
adda([Y,X])                     #18
adda([Y,X])                     #19
st([Y,X])                       #20
st([v6502_Qz])                  #21 Z flag
st([v6502_Qn])                  #22 N flag
ld([v6502_P])                   #23 C Flag
anda(~1)                        #24
ld([v6502_Tmp],X)               #25
ora([X])                        #26
st([v6502_P])                   #27
ld(hi('v6502_next'),Y)          #28
ld(-32/2)                       #29
jmp(Y,'v6502_next')             #30
#nop()                          #31 Overlap
#
label('v6502_asl')
ld([v6502_ADH],Y)               #12,32
ld([Y,X])                       #13
anda(0x80)                      #14
st([v6502_Tmp])                 #15
bra('.rol#18')                  #16
ld(0)                           #17

label('v6502_jmp1')
nop()                           #12
ld([v6502_ADL])                 #13
st([v6502_PCL])                 #14
ld([v6502_ADH])                 #15
st([v6502_PCH])                 #16
ld(hi('v6502_next'),Y)          #17
jmp(Y,'v6502_next')             #18
ld(-20/2)                       #19

label('v6502_jmp2')
nop()                           #12
ld([v6502_ADH],Y)               #13
ld([Y,X])                       #14
st([Y,Xpp])                     #15 (Just X++) Wrap around: bug compatible with NMOS
st([v6502_PCL])                 #16
ld([Y,X])                       #17
st([v6502_PCH])                 #18
ld(hi('v6502_next'),Y)          #19
jmp(Y,'v6502_next')             #20
ld(-22/2)                       #21

label('v6502_pla')
ld([v6502_S])                   #12
ld(AC,X)                        #13
adda(1)                         #14
st([v6502_S])                   #15
ld([X])                         #16
st([v6502_A])                   #17
st([v6502_Qz])                  #18 Z flag
st([v6502_Qn])                  #19 N flag
ld(hi('v6502_next'),Y)          #20
ld(-24/2)                       #21
jmp(Y,'v6502_next')             #22
#nop()                          #23 Overlap
#
label('v6502_pha')
ld(hi('v6502_next'),Y)          #12,24
ld([v6502_S])                   #13
suba(1)                         #14
st([v6502_S],X)                 #15
ld([v6502_A])                   #16
st([X])                         #17
jmp(Y,'v6502_next')             #18
ld(-20/2)                       #19

label('v6502_brk')
ld(hi('ENTER'))                 #12 Switch to vCPU
st([vCpuSelect])                #13
assert v6502_A == vAC
ld(0)                           #14
st([vAC+1])                     #15
ld(hi('REENTER'),Y)             #16 Switch in the current time slice
ld(-22//2+v6502_adjust)         #17
jmp(Y,'REENTER')                #18
nop()                           #19

# All interpreter entry points must share the same page offset, because
# this offset is hard-coded as immediate operand in the video driver.
# The Gigatron's original vCPU's 'ENTER' label is already at $2ff, so we
# just use $dff for 'v6502_ENTER'. v6502 actually has two entry points.
# The other is 'v6502_RESUME' at $10ff. It is used for instructions
# that were fetched but not yet executed. Allowing the split gives finer
# granulariy, and hopefully more throughput for the simpler instructions.
# (There is no "overhead" for allowing instruction splitting, because
#  both emulation phases must administer [vTicks] anyway.)
while pc()&255 < 255:
  nop()
label('v6502_ENTER')
bra('v6502_next2')              #0 v6502 primary entry point
# --- Page boundary ---
suba(v6502_adjust)              #1,19 Adjust for vCPU/v6520 timing differences

#19 Addressing modes
(   'v6502_mode0'  ); bra('v6502_modeIZX'); bra('v6502_modeIMM'); bra('v6502_modeILL') # $00 xxx000xx
bra('v6502_modeZP');  bra('v6502_modeZP');  bra('v6502_modeZP');  bra('v6502_modeILL') # $04 xxx001xx
bra('v6502_modeIMP'); bra('v6502_modeIMM'); bra('v6502_modeACC'); bra('v6502_modeILL') # $08 xxx010xx
bra('v6502_modeABS'); bra('v6502_modeABS'); bra('v6502_modeABS'); bra('v6502_modeILL') # $0c xxx011xx
bra('v6502_modeREL'); bra('v6502_modeIZY'); bra('v6502_modeIMM'); bra('v6502_modeILL') # $10 xxx100xx
bra('v6502_modeZPX'); bra('v6502_modeZPX'); bra('v6502_modeZPX'); bra('v6502_modeILL') # $14 xxx101xx
bra('v6502_modeIMP'); bra('v6502_modeABY'); bra('v6502_modeIMP'); bra('v6502_modeILL') # $18 xxx110xx
bra('v6502_modeABX'); bra('v6502_modeABX'); bra('v6502_modeABX'); bra('v6502_modeILL') # $1c xxx111xx

# Special encoding cases for emulator:
#     $00 BRK -         but gets mapped to #$DD      handled in v6502_mode0
#     $20 JSR $DDDD     but gets mapped to #$DD      handled in v6502_mode0 and v6502_JSR
#     $40 RTI -         but gets mapped to #$DD      handled in v6502_mode0
#     $60 RTS -         but gets mapped to #$DD      handled in v6502_mode0
#     $6C JMP ($DDDD)   but gets mapped to $DDDD     handled in v6502_JMP2
#     $96 STX $DD,Y     but gets mapped to $DD,X     handled in v6502_STX2
#     $B6 LDX $DD,Y     but gets mapped to $DD,X     handled in v6502_LDX2
#     $BE LDX $DDDD,Y   but gets mapped to $DDDD,X   handled in v6502_modeABX

label('v6502_next')
adda([vTicks])                  #0
blt('v6502_exitBefore')         #1 No more ticks
label('v6502_next2')
st([vTicks])                    #2
#
# Fetch opcode
ld([v6502_PCL],X)               #3
ld([v6502_PCH],Y)               #4
ld([Y,X])                       #5 Fetch IR
st([v6502_IR])                  #6
ld([v6502_PCL])                 #7 PC++
adda(1)                         #8
st([v6502_PCL],X)               #9
beq(pc()+3)                     #10
bra(pc()+3)                     #11
ld(0)                           #12
ld(1)                           #12(!)
adda([v6502_PCH])               #13
st([v6502_PCH],Y)               #14
#
# Get addressing mode and fetch operands
ld([v6502_IR])                  #15 Get addressing mode
anda(31)                        #16
bra(AC)                         #17
bra('.next20')                  #18
# (jump table)                  #19
label('.next20')
ld([Y,X])                       #20 Fetch L
# Most opcodes branch away at this point, but IR & 31 == 0 falls through
#
# Implicit Mode for  BRK JSR RTI RTS (<  0x80) -- 26 cycles
# Immediate Mode for LDY CPY CPX     (>= 0x80) -- 36 cycles
label('v6502_mode0')
ld([v6502_IR])                  #21 'xxx0000'
bmi('.imm24')                   #22
ld([v6502_PCH])                 #23
bra('v6502_check')              #24
ld(-26/2)                       #25

# Resync with video driver. At this point we're returning BEFORE
# fetching and executing the next instruction.
label('v6502_exitBefore')
adda(v6502_maxTicks)            #3 Exit BEFORE fetch
bgt(pc()&255)                   #4 Resync
suba(1)                         #5
ld(hi('v6502_ENTER'))           #6 Set entry point to before 'fetch'
st([vCpuSelect])                #7
ld(hi('vBlankStart'),Y)         #8
jmp(Y,[vReturn])                #9 To video driver
ld([channel])                   #10
assert v6502_overhead ==         11

# Immediate Mode: #$FF -- 36 cycles
label('v6502_modeIMM')
nop()                           #21 Wait for v6502_mode0 to join
nop()                           #22
ld([v6502_PCH])                 #23 Copy PC
label('.imm24')
st([v6502_ADH])                 #24
ld([v6502_PCL])                 #25
st([v6502_ADL],X)               #26
adda(1)                         #27 PC++
st([v6502_PCL])                 #28
beq(pc()+3)                     #29
bra(pc()+3)                     #30
ld(0)                           #31
ld(1)                           #31(!)
adda([v6502_PCH])               #32
st([v6502_PCH])                 #33
bra('v6502_check')              #34
ld(-36/2)                       #35

# Accumulator Mode: ROL ROR LSL ASR -- 28 cycles
label('v6502_modeACC')
ld(v6502_A&255)                 #21 Address of AC
st([v6502_ADL],X)               #22
ld(v6502_A>>8)                  #23
st([v6502_ADH])                 #24
ld(-28/2)                       #25
bra('v6502_check')              #26
#nop()                          #27 Overlap
#
# Implied Mode: no operand -- 24 cycles
label('v6502_modeILL')
label('v6502_modeIMP')
nop()                           #21,27
bra('v6502_check')              #22
ld(-24/2)                       #23

# Zero Page Modes: $DD $DD,X $DD,Y -- 36 cycles
label('v6502_modeZPX')
bra('.zp23')                    #21
adda([v6502_X])                 #22
label('v6502_modeZP')
bra('.zp23')                    #21
nop()                           #22
label('.zp23')
st([v6502_ADL],X)               #23
ld(0)                           #24 H=0
st([v6502_ADH])                 #25
ld(1)                           #26 PC++
adda([v6502_PCL])               #27
st([v6502_PCL])                 #28
beq(pc()+3)                     #29
bra(pc()+3)                     #30
ld(0)                           #31
ld(1)                           #31(!)
adda([v6502_PCH])               #32
st([v6502_PCH])                 #33
bra('v6502_check')              #34
ld(-36/2)                       #35

# Possible retry loop for modeABS and modeIZY. Because these need
# more time than the v6502_maxTicks of 38 Gigatron cycles, we may
# have to restart them after the next horizontal pulse.
label('.retry28')
beq(pc()+3)                     #28,37 PC--
bra(pc()+3)                     #29
ld(0)                           #30
ld(-1)                          #30(!)
adda([v6502_PCH])               #31
st([v6502_PCH])                 #32
ld([v6502_PCL])                 #33
suba(1)                         #34
st([v6502_PCL])                 #35
bra('v6502_next')               #36 Retry until sufficient time
ld(-38/2)                       #37

# Absolute Modes: $DDDD $DDDD,X $DDDD,Y -- 64 cycles
label('v6502_modeABS')
bra('.abs23')                   #21
ld(0)                           #22
label('v6502_modeABX')
bra('.abs23')                   #21
label('v6502_modeABY')
ld([v6502_X])                   #21,22
ld([v6502_Y])                   #22
label('.abs23')
st([v6502_ADL])                 #23
ld(-64//2+v6502_maxTicks)       #24 Is there enough time for the excess ticks?
adda([vTicks])                  #25
blt('.retry28')                 #26
ld([v6502_PCL])                 #27
ld([v6502_IR])                  #28 Special case $BE: LDX $DDDD,Y (we got X in ADL)
xora(0xbe)                      #29
beq(pc()+3)                     #30
bra(pc()+3)                     #31
ld([v6502_ADL])                 #32
ld([v6502_Y])                   #32(!)
adda([Y,X])                     #33 Fetch and add L
st([v6502_ADL])                 #34
bmi('.abs37')                   #35 Carry?
suba([Y,X])                     #36 Gets back original operand
bra('.abs39')                   #37
ora([Y,X])                      #38 Carry in bit 7
label('.abs37')
anda([Y,X])                     #37 Carry in bit 7
nop()                           #38
label('.abs39')
anda(0x80,X)                    #39 Move carry to bit 0
ld([X])                         #40
st([v6502_ADH])                 #41
ld([v6502_PCL])                 #42 PC++
adda(1)                         #43
st([v6502_PCL],X)               #44
beq(pc()+3)                     #45
bra(pc()+3)                     #46
ld(0)                           #47
ld(1)                           #47(!)
adda([v6502_PCH])               #48
st([v6502_PCH],Y)               #49
ld([Y,X])                       #50 Fetch H
adda([v6502_ADH])               #51
st([v6502_ADH])                 #52
ld([v6502_PCL])                 #53 PC++
adda(1)                         #54
st([v6502_PCL])                 #55
beq(pc()+3)                     #56
bra(pc()+3)                     #57
ld(0)                           #58
ld(1)                           #58(!)
adda([v6502_PCH])               #59
st([v6502_PCH])                 #60
ld([v6502_ADL],X)               #61
bra('v6502_check')              #62
ld(-64/2)                       #63

# Indirect Indexed Mode: ($DD),Y -- 54 cycles
label('v6502_modeIZY')
ld(AC,X)                        #21 $DD
ld(0,Y)                         #22 $00DD
ld(-54//2+v6502_maxTicks)       #23 Is there enough time for the excess ticks?
adda([vTicks])                  #24
nop()                           #25
blt('.retry28')                 #26
ld([v6502_PCL])                 #27
adda(1)                         #28 PC++
st([v6502_PCL])                 #29
beq(pc()+3)                     #30
bra(pc()+3)                     #31
ld(0)                           #32
ld(1)                           #32(!)
adda([v6502_PCH])               #33
st([v6502_PCH])                 #34
ld([Y,X])                       #35 Read word from zero-page
st([Y,Xpp])                     #36 (Just X++) Wrap-around is correct
st([v6502_ADL])                 #37
ld([Y,X])                       #38
st([v6502_ADH])                 #39
ld([v6502_Y])                   #40 Add Y
adda([v6502_ADL])               #41
st([v6502_ADL])                 #42
bmi('.izy45')                   #43 Carry?
suba([v6502_Y])                 #44 Gets back original operand
bra('.izy47')                   #45
ora([v6502_Y])                  #46 Carry in bit 7
label('.izy45')
anda([v6502_Y])                 #45 Carry in bit 7
nop()                           #46
label('.izy47')
anda(0x80,X)                    #47 Move carry to bit 0
ld([X])                         #48
adda([v6502_ADH])               #49
st([v6502_ADH])                 #50
ld([v6502_ADL],X)               #51
bra('v6502_check')              #52
ld(-54/2)                       #53

# Relative Mode: BEQ BNE BPL BMI BCC BCS BVC BVS -- 36 cycles
label('v6502_modeREL')
st([v6502_ADL],X)               #21 Offset (Only needed for branch)
bmi(pc()+3)                     #22 Sign extend
bra(pc()+3)                     #23
ld(0)                           #24
ld(255)                         #24(!)
st([v6502_ADH])                 #25
ld([v6502_PCL])                 #26 PC++ (Needed for both cases)
adda(1)                         #27
st([v6502_PCL])                 #28
beq(pc()+3)                     #29
bra(pc()+3)                     #30
ld(0)                           #31
ld(1)                           #31(!)
adda([v6502_PCH])               #32
st([v6502_PCH])                 #33
bra('v6502_check')              #34
ld(-36/2)                       #53

# Indexed Indirect Mode: ($DD,X) -- 38 cycles
label('v6502_modeIZX')
adda([v6502_X])                 #21 Add X
st([v6502_Tmp])                 #22
adda(1,X)                       #23 Read word from zero-page
ld([X])                         #24
st([v6502_ADH])                 #25
ld([v6502_Tmp],X)               #26
ld([X])                         #27
st([v6502_ADL],X)               #28
ld([v6502_PCL])                 #29 PC++
adda(1)                         #30
st([v6502_PCL])                 #31
beq(pc()+3)                     #32
bra(pc()+3)                     #33
ld(0)                           #34
ld(1)                           #34(!)
adda([v6502_PCH])               #35
st([v6502_PCH])                 #36
ld(-38/2)                       #37 !!! Fall through to v6502_check !!!
#
# Update elapsed time for the addressing mode processing.
# Then check if we can immediately execute this instruction.
# Otherwise transfer control to the video driver.
label('v6502_check')
adda([vTicks])                  #0
blt('v6502_exitAfter')          #1 No more ticks
st([vTicks])                    #2
ld(hi('v6502_execute'),Y)       #3
jmp(Y,[v6502_IR])               #4
bra(255)                        #5

# Otherwise resync with video driver. At this point we're returning AFTER
# addressing mode decoding, but before executing the instruction.
label('v6502_exitAfter')
adda(v6502_maxTicks)            #3 Exit AFTER fetch
bgt(pc()&255)                   #4 Resync
suba(1)                         #5
ld(hi('v6502_RESUME'))          #6 Set entry point to before 'execute'
st([vCpuSelect])                #7
ld(hi('vBlankStart'),Y)         #8
jmp(Y,[vReturn])                #9 To video driver
ld([channel])                   #10
assert v6502_overhead ==         11

align(0x100,size=0x100)
label('v6502_execute')
# This page works as a 255-entry (0..254) jump table for 6502 opcodes.
# Jumping into this page must have 'bra 255' in the branch delay slot
# in order to get out again and dispatch to the right continuation.
# X must hold [v6502_ADL],
# Y will hold hi('v6502_execute'),
# A will be loaded with the code offset (this is skipped at offset $ff)
ld('v6502_BRK'); ld('v6502_ORA'); ld('v6502_ILL'); ld('v6502_ILL') #6 $00
ld('v6502_ILL'); ld('v6502_ORA'); ld('v6502_ASL'); ld('v6502_ILL') #6
ld('v6502_PHP'); ld('v6502_ORA'); ld('v6502_ASL'); ld('v6502_ILL') #6
ld('v6502_ILL'); ld('v6502_ORA'); ld('v6502_ASL'); ld('v6502_ILL') #6
ld('v6502_BPL'); ld('v6502_ORA'); ld('v6502_ILL'); ld('v6502_ILL') #6 $10
ld('v6502_ILL'); ld('v6502_ORA'); ld('v6502_ASL'); ld('v6502_ILL') #6
ld('v6502_CLC'); ld('v6502_ORA'); ld('v6502_ILL'); ld('v6502_ILL') #6
ld('v6502_ILL'); ld('v6502_ORA'); ld('v6502_ASL'); ld('v6502_ILL') #6
ld('v6502_JSR'); ld('v6502_AND'); ld('v6502_ILL'); ld('v6502_ILL') #6 $20
ld('v6502_BIT'); ld('v6502_AND'); ld('v6502_ROL'); ld('v6502_ILL') #6
ld('v6502_PLP'); ld('v6502_AND'); ld('v6502_ROL'); ld('v6502_ILL') #6
ld('v6502_BIT'); ld('v6502_AND'); ld('v6502_ROL'); ld('v6502_ILL') #6
ld('v6502_BMI'); ld('v6502_AND'); ld('v6502_ILL'); ld('v6502_ILL') #6 $30
ld('v6502_ILL'); ld('v6502_AND'); ld('v6502_ROL'); ld('v6502_ILL') #6
ld('v6502_SEC'); ld('v6502_AND'); ld('v6502_ILL'); ld('v6502_ILL') #6
ld('v6502_ILL'); ld('v6502_AND'); ld('v6502_ROL'); ld('v6502_ILL') #6
ld('v6502_RTI'); ld('v6502_EOR'); ld('v6502_ILL'); ld('v6502_ILL') #6 $40
ld('v6502_ILL'); ld('v6502_EOR'); ld('v6502_LSR'); ld('v6502_ILL') #6
ld('v6502_PHA'); ld('v6502_EOR'); ld('v6502_LSR'); ld('v6502_ILL') #6
ld('v6502_JMP1');ld('v6502_EOR'); ld('v6502_LSR'); ld('v6502_ILL') #6
ld('v6502_BVC'); ld('v6502_EOR'); ld('v6502_ILL'); ld('v6502_ILL') #6 $50
ld('v6502_ILL'); ld('v6502_EOR'); ld('v6502_LSR'); ld('v6502_ILL') #6
ld('v6502_CLI'); ld('v6502_EOR'); ld('v6502_ILL'); ld('v6502_ILL') #6
ld('v6502_ILL'); ld('v6502_EOR'); ld('v6502_LSR'); ld('v6502_ILL') #6
ld('v6502_RTS'); ld('v6502_ADC'); ld('v6502_ILL'); ld('v6502_ILL') #6 $60
ld('v6502_ILL'); ld('v6502_ADC'); ld('v6502_ROR'); ld('v6502_ILL') #6
ld('v6502_PLA'); ld('v6502_ADC'); ld('v6502_ROR'); ld('v6502_ILL') #6
ld('v6502_JMP2');ld('v6502_ADC'); ld('v6502_ROR'); ld('v6502_ILL') #6
ld('v6502_BVS'); ld('v6502_ADC'); ld('v6502_ILL'); ld('v6502_ILL') #6 $70
ld('v6502_ILL'); ld('v6502_ADC'); ld('v6502_ROR'); ld('v6502_ILL') #6
ld('v6502_SEI'); ld('v6502_ADC'); ld('v6502_ILL'); ld('v6502_ILL') #6
ld('v6502_ILL'); ld('v6502_ADC'); ld('v6502_ROR'); ld('v6502_ILL') #6
ld('v6502_ILL'); ld('v6502_STA'); ld('v6502_ILL'); ld('v6502_ILL') #6 $80
ld('v6502_STY'); ld('v6502_STA'); ld('v6502_STX'); ld('v6502_ILL') #6
ld('v6502_DEY'); ld('v6502_ILL'); ld('v6502_TXA'); ld('v6502_ILL') #6
ld('v6502_STY'); ld('v6502_STA'); ld('v6502_STX'); ld('v6502_ILL') #6
ld('v6502_BCC'); ld('v6502_STA'); ld('v6502_ILL'); ld('v6502_ILL') #6 $90
ld('v6502_STY'); ld('v6502_STA'); ld('v6502_STX2');ld('v6502_ILL') #6
ld('v6502_TYA'); ld('v6502_STA'); ld('v6502_TXS'); ld('v6502_ILL') #6
ld('v6502_ILL'); ld('v6502_STA'); ld('v6502_ILL'); ld('v6502_ILL') #6
ld('v6502_LDY'); ld('v6502_LDA'); ld('v6502_LDX'); ld('v6502_ILL') #6 $A0
ld('v6502_LDY'); ld('v6502_LDA'); ld('v6502_LDX'); ld('v6502_ILL') #6
ld('v6502_TAY'); ld('v6502_LDA'); ld('v6502_TAX'); ld('v6502_ILL') #6
ld('v6502_LDY'); ld('v6502_LDA'); ld('v6502_LDX'); ld('v6502_ILL') #6
ld('v6502_BCS'); ld('v6502_LDA'); ld('v6502_ILL'); ld('v6502_ILL') #6 $B0
ld('v6502_LDY'); ld('v6502_LDA'); ld('v6502_LDX2');ld('v6502_ILL') #6
ld('v6502_CLV'); ld('v6502_LDA'); ld('v6502_TSX'); ld('v6502_ILL') #6
ld('v6502_LDY'); ld('v6502_LDA'); ld('v6502_LDX'); ld('v6502_ILL') #6
ld('v6502_CPY'); ld('v6502_CMP'); ld('v6502_ILL'); ld('v6502_ILL') #6 $C0
ld('v6502_CPY'); ld('v6502_CMP'); ld('v6502_DEC'); ld('v6502_ILL') #6
ld('v6502_INY'); ld('v6502_CMP'); ld('v6502_DEX'); ld('v6502_ILL') #6
ld('v6502_CPY'); ld('v6502_CMP'); ld('v6502_DEC'); ld('v6502_ILL') #6
ld('v6502_BNE'); ld('v6502_CMP'); ld('v6502_ILL'); ld('v6502_ILL') #6 $D0
ld('v6502_ILL'); ld('v6502_CMP'); ld('v6502_DEC'); ld('v6502_ILL') #6
ld('v6502_CLD'); ld('v6502_CMP'); ld('v6502_ILL'); ld('v6502_ILL') #6
ld('v6502_ILL'); ld('v6502_CMP'); ld('v6502_DEC'); ld('v6502_ILL') #6
ld('v6502_CPX'); ld('v6502_SBC'); ld('v6502_ILL'); ld('v6502_ILL') #6 $E0
ld('v6502_CPX'); ld('v6502_SBC'); ld('v6502_INC'); ld('v6502_ILL') #6
ld('v6502_INX'); ld('v6502_SBC'); ld('v6502_NOP'); ld('v6502_ILL') #6
ld('v6502_CPX'); ld('v6502_SBC'); ld('v6502_INC'); ld('v6502_ILL') #6
ld('v6502_BEQ'); ld('v6502_SBC'); ld('v6502_ILL'); ld('v6502_ILL') #6 $F0
ld('v6502_ILL'); ld('v6502_SBC'); ld('v6502_INC'); ld('v6502_ILL') #6
ld('v6502_SED'); ld('v6502_SBC'); ld('v6502_ILL'); ld('v6502_ILL') #6
ld('v6502_ILL'); ld('v6502_SBC'); ld('v6502_INC')                  #6
bra(AC)                         #6,7 Dispatch into next page
# --- Page boundary ---
align(0x100,size=0x100)
ld(hi('v6502_next'),Y)          #8 Handy for instructions that don't clobber Y

label('v6502_ADC')
assert pc()&255 == 1
assert v6502_Cflag == 1
assert v6502_Vemu == 128
ld([v6502_ADH],Y)               #9 Must be at page offset 1, so A=1
anda([v6502_P])                 #10 Carry in (AC=1 because lo('v6502_ADC')=1)
adda([v6502_A])                 #11 Sum
beq('.adc14')                   #12 Danger zone for dropping a carry
adda([Y,X])                     #13
st([v6502_Qz])                  #14 Z flag, don't overwrite left-hand side (A) yet
st([v6502_Qn])                  #15 N flag
xora([v6502_A])                 #16 V flag, (Q^A) & (B^Q) & 0x80
st([v6502_A])                   #17
ld([Y,X])                       #18
xora([v6502_Qz])                #19
anda([v6502_A])                 #20
anda(0x80)                      #21
st([v6502_Tmp])                 #22
ld([v6502_Qz])                  #23 Update A
st([v6502_A])                   #24
bmi('.adc27')                   #25 C flag
suba([Y,X])                     #26
bra('.adc29')                   #27
ora([Y,X])                      #28
label('.adc27')
anda([Y,X])                     #27
nop()                           #28
label('.adc29')
anda(0x80,X)                    #29
ld([v6502_P])                   #30 Update P
anda(~v6502_Vemu&~v6502_Cflag)  #31
ora([X])                        #32
ora([v6502_Tmp])                #33
st([v6502_P])                   #34
ld(hi('v6502_next'),Y)          #35
jmp(Y,'v6502_next')             #36
ld(-38/2)                       #37
# Cin=1, A=$FF, B=$DD --> Result=$DD, Cout=1, V=0
# Cin=0, A=$00, B=$DD --> Result=$DD, Cout=0, V=0
label('.adc14')
st([v6502_A])                   #14 Special case
st([v6502_Qz])                  #15 Z flag
st([v6502_Qn])                  #16 N flag
ld([v6502_P])                   #17
anda(0x7f)                      #18 V=0, keep C
st([v6502_P])                   #19
ld(hi('v6502_next'),Y)          #20
ld(-24/2)                       #21
jmp(Y,'v6502_next')             #22
#nop()                          #23 Overlap
#
label('v6502_SBC')
# No matter how hard we try, v6502_SBC always comes out a lot clumsier
# than v6502_ADC. And that one already barely fits in 38 cycles and is
# hard to follow. So we use a hack: transmorph our SBC into an ADC with
# inverted operand, and then dispatch again. Simple and effective.
ld([v6502_ADH],Y)               #9,24
ld([Y,X])                       #10
xora(255)                       #11 Invert right-hand side operand
st([v6502_BI])                  #12 Park modified operand for v6502_ADC
ld(v6502_BI&255)                #13 Address of BI
st([v6502_ADL],X)               #14
ld(v6502_BI>>8)                 #15
st([v6502_ADH])                 #16
ld(0x69)                        #17 ADC #$xx (Any ADC opcode will do)
st([v6502_IR])                  #18
ld(hi('v6502_check'),Y)         #20 Go back to time check before dispatch
jmp(Y,'v6502_check')            #20
ld(-22/2)                       #21

# Carry calculation table
#   L7 R7 C7   RX UC SC
#   -- -- -- | -- -- --
#    0  0  0 |  0  0  0
#    0  0  1 |  0  0  0
#    1  0  0 |  0  1 +1
#    1  0  1 |  0  0  0
#    0  1  0 | -1  1  0
#    0  1  1 | -1  0 -1
#    1  1  0 | -1  1  0
#    1  1  1 | -1  1  0
#   -- -- -- | -- -- --
#    ^  ^  ^    ^  ^  ^
#    |  |  |    |  |  `--- Carry of unsigned L + signed R: SC = RX + UC
#    |  |  |    |  `----- Carry of unsigned L + unsigned R: UC = C7 ? L7&R7 : L7|R7
#    |  |  |    `------- Sign extension of signed R
#    |  |  `--------- MSB of unextended L + R
#    |  `----------- MSB of right operand R
#    `------------- MSB of left operand L

label('v6502_CLC')
ld([v6502_P])                   #9
bra('.sec12')                   #10
label('v6502_SEC')
anda(~v6502_Cflag)              #9,11 Overlap
ld([v6502_P])                   #10
ora(v6502_Cflag)                #11
label('.sec12')
st([v6502_P])                   #12
nop()                           #13
label('.next14')
jmp(Y,'v6502_next')             #14
ld(-16/2)                       #15

label('v6502_BPL')
ld([v6502_Qn])                  #9
bmi('.next12')                  #10
bpl('.branch13')                #11
#nop()                          #12 Overlap
label('v6502_BMI')
ld([v6502_Qn])                  #9,12
bpl('.next12')                  #10
bmi('.branch13')                #11
#nop()                          #12 Overlap
label('v6502_BVC')
ld([v6502_P])                   #9,12
anda(v6502_Vemu)                #10
beq('.branch13')                #11
bne('.next14')                  #12
#nop()                          #13 Overlap
label('v6502_BVS')
ld([v6502_P])                   #9,13
anda(v6502_Vemu)                #10
bne('.branch13')                #11
beq('.next14')                  #12
#nop()                          #13 Overlap
label('v6502_BCC')
ld([v6502_P])                   #9,13
anda(v6502_Cflag)               #10
beq('.branch13')                #11
bne('.next14')                  #12
#nop()                          #13 Overlap
label('v6502_BCS')
ld([v6502_P])                   #9,13
anda(v6502_Cflag)               #10
bne('.branch13')                #11
beq('.next14')                  #12
#nop()                          #13 Overlap
label('v6502_BNE')
ld([v6502_Qz])                  #9,13
beq('.next12')                  #10
bne('.branch13')                #11
#nop()                          #12 Overlap
label('v6502_BEQ')
ld([v6502_Qz])                  #9,12
bne('.next12')                  #10
beq('.branch13')                #11
#nop()                          #12 Overlap
label('.branch13')
ld([v6502_ADL])                 #13,12 PC + offset
adda([v6502_PCL])               #14
st([v6502_PCL])                 #15
bmi('.bra0')                    #16 Carry
suba([v6502_ADL])               #17
bra('.bra1')                    #18
ora([v6502_ADL])                #19
label('.bra0')
anda([v6502_ADL])               #18
nop()                           #19
label('.bra1')
anda(0x80,X)                    #20
ld([X])                         #21
adda([v6502_ADH])               #22
adda([v6502_PCH])               #23
st([v6502_PCH])                 #24
nop()                           #25
jmp(Y,'v6502_next')             #26
ld(-28/2)                       #27

label('v6502_INX')
nop()                           #9
ld([v6502_X])                   #10
adda(1)                         #11
st([v6502_X])                   #12
label('.inx13')
st([v6502_Qz])                  #13 Z flag
st([v6502_Qn])                  #14 N flag
ld(-18/2)                       #15
jmp(Y,'v6502_next')             #16
nop()                           #17

label('.next12')
jmp(Y,'v6502_next')             #12
ld(-14/2)                       #13

label('v6502_DEX')
ld([v6502_X])                   #9
suba(1)                         #10
bra('.inx13')                   #11
st([v6502_X])                   #12

label('v6502_INY')
ld([v6502_Y])                   #9
adda(1)                         #10
bra('.inx13')                   #11
st([v6502_Y])                   #12

label('v6502_DEY')
ld([v6502_Y])                   #9
suba(1)                         #10
bra('.inx13')                   #11
st([v6502_Y])                   #12

label('v6502_NOP')
ld(-12/2)                       #9
jmp(Y,'v6502_next')             #10
#nop()                          #11 Overlap
#
label('v6502_AND')
ld([v6502_ADH],Y)               #9,11
ld([v6502_A])                   #10
bra('.eor13')                   #11
anda([Y,X])                     #12

label('v6502_ORA')
ld([v6502_ADH],Y)               #9
ld([v6502_A])                   #10
bra('.eor13')                   #11
label('v6502_EOR')
ora([Y,X])                      #12,9
#
#label('v6502_EOR')
#nop()                          #9 Overlap
ld([v6502_ADH],Y)               #10
ld([v6502_A])                   #11
xora([Y,X])                     #12
label('.eor13')
st([v6502_A])                   #13
st([v6502_Qz])                  #14 Z flag
st([v6502_Qn])                  #15 N flag
ld(hi('v6502_next'),Y)          #16
ld(-20/2)                       #17
jmp(Y,'v6502_next')             #18
#nop()                          #19 Overlap
#
label('v6502_JMP1')
ld(hi('v6502_jmp1'),Y)          #9,19 JMP $DDDD
jmp(Y,'v6502_jmp1')             #10
#nop()                          #11 Overlap
label('v6502_JMP2')
ld(hi('v6502_jmp2'),Y)          #9 JMP ($DDDD)
jmp(Y,'v6502_jmp2')             #10
#nop()                          #11 Overlap
label('v6502_JSR')
ld([v6502_S])                   #9,11
suba(2)                         #10
st([v6502_S],X)                 #11
ld(v6502_Stack>>8,Y)            #12
ld([v6502_PCH])                 #13 Let ADL,ADH point to L operand
st([v6502_ADH])                 #14
ld([v6502_PCL])                 #15
st([v6502_ADL])                 #16
adda(1)                         #17 Push ++PC
st([v6502_PCL])                 #18 Let PCL,PCH point to H operand
st([Y,Xpp])                     #19
beq(pc()+3)                     #20
bra(pc()+3)                     #21
ld(0)                           #22
ld(1)                           #22(!)
adda([v6502_PCH])               #23
st([v6502_PCH])                 #24
st([Y,X])                       #25
ld([v6502_ADL],X)               #26 Fetch L
ld([v6502_ADH],Y)               #27
ld([Y,X])                       #28
ld([v6502_PCL],X)               #29 Fetch H
st([v6502_PCL])                 #30
ld([v6502_PCH],Y)               #31
ld([Y,X])                       #32
st([v6502_PCH])                 #33
ld(hi('v6502_next'),Y)          #34
ld(-38/2)                       #35
jmp(Y,'v6502_next')             #36
#nop()                          #37 Overlap
#
label('v6502_INC')
ld(hi('v6502_inc'),Y)           #9,37
jmp(Y,'v6502_inc')              #10
#nop()                          #11 Overlap
label('v6502_LDA')
ld(hi('v6502_lda'),Y)           #9,11
jmp(Y,'v6502_lda')              #10
#nop()                          #11 Overlap
label('v6502_LDX')
ld(hi('v6502_ldx'),Y)           #9,11
jmp(Y,'v6502_ldx')              #10
#nop()                          #11 Overlap
label('v6502_LDX2')
ld(hi('v6502_ldx2'),Y)          #9,11
jmp(Y,'v6502_ldx2')             #10
#nop()                          #11 Overlap
label('v6502_LDY')
ld(hi('v6502_ldy'),Y)           #9,11
jmp(Y,'v6502_ldy')              #10
#nop()                          #11 Overlap
label('v6502_STA')
ld(hi('v6502_sta'),Y)           #9,11
jmp(Y,'v6502_sta')              #10
#nop()                          #11 Overlap
label('v6502_STX')
ld(hi('v6502_stx'),Y)           #9,11
jmp(Y,'v6502_stx')              #10
#nop()                          #11 Overlap
label('v6502_STX2')
ld(hi('v6502_stx2'),Y)          #9,11
jmp(Y,'v6502_stx2')             #10
#nop()                          #11 Overlap
label('v6502_STY')
ld(hi('v6502_sty'),Y)           #9,11
jmp(Y,'v6502_sty')              #10
#nop()                          #11 Overlap
label('v6502_TAX')
ld(hi('v6502_tax'),Y)           #9,11
jmp(Y,'v6502_tax')              #10
#nop()                          #11 Overlap
label('v6502_TAY')
ld(hi('v6502_tay'),Y)           #9,11
jmp(Y,'v6502_tay')              #10
#nop()                          #11 Overlap
label('v6502_TXA')
ld(hi('v6502_txa'),Y)           #9,11
jmp(Y,'v6502_txa')              #10
#nop()                          #11 Overlap
label('v6502_TYA')
ld(hi('v6502_tya'),Y)           #9,11
jmp(Y,'v6502_tya')              #10
#nop()                          #11 Overlap
label('v6502_CLV')
ld(hi('v6502_clv'),Y)           #9,11
jmp(Y,'v6502_clv')              #10
#nop()                          #11 Overlap
label('v6502_RTI')
ld(hi('v6502_rti'),Y)           #9,11
jmp(Y,'v6502_rti')              #10
#nop()                          #11 Overlap
label('v6502_ROR')
ld(hi('v6502_ror'),Y)           #9,11
jmp(Y,'v6502_ror')              #10
#nop()                          #11 Overlap
label('v6502_LSR')
ld(hi('v6502_lsr'),Y)           #9,11
jmp(Y,'v6502_lsr')              #10
#nop()                          #11 Overlap
label('v6502_PHA')
ld(hi('v6502_pha'),Y)           #9,11
jmp(Y,'v6502_pha')              #10
#nop()                          #11 Overlap
label('v6502_CLI')
ld(hi('v6502_cli'),Y)           #9,11
jmp(Y,'v6502_cli')              #10
#nop()                          #11 Overlap
label('v6502_RTS')
ld(hi('v6502_rts'),Y)           #9,11
jmp(Y,'v6502_rts')              #10
#nop()                          #11 Overlap
label('v6502_PLA')
ld(hi('v6502_pla'),Y)           #9,11
jmp(Y,'v6502_pla')              #10
#nop()                          #11 Overlap
label('v6502_SEI')
ld(hi('v6502_sei'),Y)           #9,11
jmp(Y,'v6502_sei')              #10
#nop()                          #11 Overlap
label('v6502_TXS')
ld(hi('v6502_txs'),Y)           #9,11
jmp(Y,'v6502_txs')              #10
#nop()                          #11 Overlap
label('v6502_TSX')
ld(hi('v6502_tsx'),Y)           #9,11
jmp(Y,'v6502_tsx')              #10
#nop()                          #11 Overlap
label('v6502_CPY')
ld(hi('v6502_cpy'),Y)           #9,11
jmp(Y,'v6502_cpy')              #10
#nop()                          #11 Overlap
label('v6502_CMP')
ld(hi('v6502_cmp'),Y)           #9,11
jmp(Y,'v6502_cmp')              #10
#nop()                          #11 Overlap
label('v6502_DEC')
ld(hi('v6502_dec'),Y)           #9,11
jmp(Y,'v6502_dec')              #10
#nop()                          #11 Overlap
label('v6502_CLD')
ld(hi('v6502_cld'),Y)           #9,11
jmp(Y,'v6502_cld')              #10
#nop()                          #11 Overlap
label('v6502_CPX')
ld(hi('v6502_cpx'),Y)           #9,11
jmp(Y,'v6502_cpx')              #10
#nop()                          #11 Overlap
label('v6502_ASL')
ld(hi('v6502_asl'),Y)           #9,11
jmp(Y,'v6502_asl')              #10
#nop()                          #11 Overlap
label('v6502_PHP')
ld(hi('v6502_php'),Y)           #9,11
jmp(Y,'v6502_php')              #10
#nop()                          #11 Overlap
label('v6502_BIT')
ld(hi('v6502_bit'),Y)           #9
jmp(Y,'v6502_bit')              #10
#nop()                          #11 Overlap
label('v6502_ROL')
ld(hi('v6502_rol'),Y)           #9
jmp(Y,'v6502_rol')              #10
#nop()                          #11 Overlap
label('v6502_PLP')
ld(hi('v6502_plp'),Y)           #9
jmp(Y,'v6502_plp')              #10
#nop()                          #11 Overlap
label('v6502_SED')              # Decimal mode not implemented
ld(hi('v6502_sed'),Y)           #9,11
jmp(Y,'v6502_sed')              #10
#nop()                          #11 Overlap
label('v6502_ILL') # All illegal opcodes map to BRK, except $FF which will crash
label('v6502_BRK')
ld(hi('v6502_brk'),Y)           #9
jmp(Y,'v6502_brk')              #10
#nop()                          #11 Overlap

while pc()&255 < 255:
  nop()

# `v6502_RESUME' is the interpreter's secondary entry point for when
# the opcode and operands were already fetched, just before the last hPulse.
# It must be at $xxff, prefably somewhere in v6502's own code pages.
label('v6502_RESUME')
assert (pc()&255) == 255
suba(v6502_adjust)              #0,11 v6502 secondary entry point
# --- Page boundary ---
align(0x100,size=0x200)
st([vTicks])                    #1
ld([v6502_ADL],X)               #2
ld(hi('v6502_execute'),Y)       #3
jmp(Y,[v6502_IR])               #4
bra(255)                        #5

label('v6502_dec')
ld([v6502_ADH],Y)               #12
ld([Y,X])                       #13
suba(1)                         #14
st([Y,X])                       #15
st([v6502_Qz])                  #16 Z flag
st([v6502_Qn])                  #17 N flag
ld(hi('v6502_next'),Y)          #18
ld(-22/2)                       #19
jmp(Y,'v6502_next')             #20
#nop()                          #21 Overlap
#
label('v6502_inc')
ld([v6502_ADH],Y)               #12,22
ld([Y,X])                       #13
adda(1)                         #14
st([Y,X])                       #15
st([v6502_Qz])                  #16 Z flag
st([v6502_Qn])                  #17 N flag
ld(hi('v6502_next'),Y)          #18
ld(-22/2)                       #19
jmp(Y,'v6502_next')             #20
nop()                           #21

label('v6502_lda')
nop()                           #12
ld([v6502_ADH],Y)               #13
ld([Y,X])                       #14
st([v6502_A])                   #15
label('.lda16')
st([v6502_Qz])                  #16 Z flag
st([v6502_Qn])                  #17 N flag
nop()                           #18
ld(hi('v6502_next'),Y)          #19
jmp(Y,'v6502_next')             #20
ld(-22/2)                       #21

label('v6502_ldx')
ld([v6502_ADH],Y)               #12
ld([Y,X])                       #13
bra('.lda16')                   #14
st([v6502_X])                   #15

label('v6502_ldy')
ld([v6502_ADH],Y)               #12
ld([Y,X])                       #13
bra('.lda16')                   #14
st([v6502_Y])                   #15

label('v6502_ldx2')
ld([v6502_ADL])                 #12 Special case $B6: LDX $DD,Y
suba([v6502_X])                 #13 Undo X offset
adda([v6502_Y],X)               #14 Apply Y instead
ld([X])                         #15
st([v6502_X])                   #16
st([v6502_Qz])                  #17 Z flag
st([v6502_Qn])                  #18 N flag
ld(hi('v6502_next'),Y)          #19
jmp(Y,'v6502_next')             #20
ld(-22/2)                       #21

label('v6502_sta')
ld([v6502_ADH],Y)               #12
ld([v6502_A])                   #13
st([Y,X])                       #14
ld(hi('v6502_next'),Y)          #15
jmp(Y,'v6502_next')             #16
ld(-18/2)                       #17

label('v6502_stx')
ld([v6502_ADH],Y)               #12
ld([v6502_X])                   #13
st([Y,X])                       #14
ld(hi('v6502_next'),Y)          #15
jmp(Y,'v6502_next')             #16
ld(-18/2)                       #17

label('v6502_stx2')
ld([v6502_ADL])                 #12 Special case $96: STX $DD,Y
suba([v6502_X])                 #13 Undo X offset
adda([v6502_Y],X)               #14 Apply Y instead
ld([v6502_X])                   #15
st([X])                         #16
ld(hi('v6502_next'),Y)          #17
jmp(Y,'v6502_next')             #18
ld(-20/2)                       #19

label('v6502_sty')
ld([v6502_ADH],Y)               #12
ld([v6502_Y])                   #13
st([Y,X])                       #14
ld(hi('v6502_next'),Y)          #15
jmp(Y,'v6502_next')             #16
label('v6502_tax')
ld(-18/2)                       #17,12
#
#label('v6502_tax')
#nop()                          #12 Overlap
ld([v6502_A])                   #13
st([v6502_X])                   #14
label('.tax15')
st([v6502_Qz])                  #15 Z flag
st([v6502_Qn])                  #16 N flag
ld(hi('v6502_next'),Y)          #17
jmp(Y,'v6502_next')             #18
label('v6502_tsx')
ld(-20/2)                       #19
#
#label('v6502_tsx')
#nop()                          #12 Overlap
ld([v6502_S])                   #13
suba(1)                         #14 Shift down on export
st([v6502_X])                   #15
label('.tsx16')
st([v6502_Qz])                  #16 Z flag
st([v6502_Qn])                  #17 N flag
nop()                           #18
ld(hi('v6502_next'),Y)          #19
jmp(Y,'v6502_next')             #20
ld(-22/2)                       #21

label('v6502_txs')
ld([v6502_X])                   #12
adda(1)                         #13 Shift up on import
bra('.tsx16')                   #14
st([v6502_S])                   #15

label('v6502_tay')
ld([v6502_A])                   #12
bra('.tax15')                   #13
st([v6502_Y])                   #14

label('v6502_txa')
ld([v6502_X])                   #12
bra('.tax15')                   #13
st([v6502_A])                   #14

label('v6502_tya')
ld([v6502_Y])                   #12
bra('.tax15')                   #13
st([v6502_A])                   #14

label('v6502_cli')
ld([v6502_P])                   #12
bra('.clv15')                   #13
anda(~v6502_Iflag)              #14

label('v6502_sei')
ld([v6502_P])                   #12
bra('.clv15')                   #13
ora(v6502_Iflag)                #14

label('v6502_cld')
ld([v6502_P])                   #12
bra('.clv15')                   #13
anda(~v6502_Dflag)              #14

label('v6502_sed')
ld([v6502_P])                   #12
bra('.clv15')                   #13
label('v6502_clv')
ora(v6502_Dflag)                #14,12 Overlap
#
#label('v6502_clv')
#nop()                          #12
ld([v6502_P])                   #13
anda(~v6502_Vemu)               #14
label('.clv15')
st([v6502_P])                   #15
ld(hi('v6502_next'),Y)          #16
ld(-20/2)                       #17
jmp(Y,'v6502_next')             #18
label('v6502_bit')
nop()                           #19,12
#
#label('v6502_bit')
#nop()                          #12 Overlap
ld([v6502_ADL],X)               #13
ld([v6502_ADH],Y)               #14
ld([Y,X])                       #15
st([v6502_Qn])                  #16 N flag
anda([v6502_A])                 #17 This is a reason we keep N and Z in separate bytes
st([v6502_Qz])                  #18 Z flag
ld([v6502_P])                   #19
anda(~v6502_Vemu)               #20
st([v6502_P])                   #21
ld([Y,X])                       #22
adda(AC)                        #23
anda(v6502_Vemu)                #24
ora([v6502_P])                  #25
st([v6502_P])                   #26 Update V
ld(hi('v6502_next'),Y)          #27
jmp(Y,'v6502_next')             #28
ld(-30/2)                       #29

label('v6502_rts')
ld([v6502_S])                   #12
ld(AC,X)                        #13
adda(2)                         #14
st([v6502_S])                   #15
ld(0,Y)                         #16
ld([Y,X])                       #17
st([Y,Xpp])                     #18 Just X++
adda(1)                         #19
st([v6502_PCL])                 #20
beq(pc()+3)                     #21
bra(pc()+3)                     #22
ld(0)                           #23
ld(1)                           #23(!)
adda([Y,X])                     #24
st([v6502_PCH])                 #25
nop()                           #26
ld(hi('v6502_next'),Y)          #27
jmp(Y,'v6502_next')             #28
ld(-30/2)                       #29

label('v6502_php')
ld([v6502_S])                   #12
suba(1)                         #13
st([v6502_S],X)                 #14
ld([v6502_P])                   #15
anda(~v6502_Vflag&~v6502_Zflag) #16 Keep Vemu,B,D,I,C
bpl(pc()+3)                     #17 V to bit 6 and clear N
bra(pc()+2)                     #18
xora(v6502_Vflag^v6502_Vemu)    #19
st([X])                         #19,20
ld([v6502_Qz])                  #21 Z flag
beq(pc()+3)                     #22
bra(pc()+3)                     #23
ld(0)                           #24
ld(v6502_Zflag)                 #24(!)
ora([X])                        #25
st([X])                         #26
ld([v6502_Qn])                  #27 N flag
anda(0x80)                      #28
ora([X])                        #29
ora(v6502_Uflag)                #30 Unused bit
st([X])                         #31
nop()                           #32
ld(hi('v6502_next'),Y)          #33
jmp(Y,'v6502_next')             #34
ld(-36/2)                       #35

label('v6502_cpx')
bra('.cmp14')                   #12
ld([v6502_X])                   #13

label('v6502_cpy')
bra('.cmp14')                   #12
label('v6502_cmp')
ld([v6502_Y])                   #13,12
#
#label('v6502_cmp')             #12 Overlap
assert v6502_Cflag == 1
ld([v6502_A])                   #13
label('.cmp14')
ld([v6502_ADH],Y)               #14
bmi('.cmp17')                   #15 Carry?
suba([Y,X])                     #16
st([v6502_Qz])                  #17 Z flag
st([v6502_Qn])                  #18 N flag
bra('.cmp21')                   #19
ora([Y,X])                      #20
label('.cmp17')
st([v6502_Qz])                  #17 Z flag
st([v6502_Qn])                  #18 N flag
anda([Y,X])                     #19
nop()                           #20
label('.cmp21')
xora(0x80)                      #21
anda(0x80,X)                    #22 Move carry to bit 0
ld([v6502_P])                   #23 C flag
anda(~1)                        #24
ora([X])                        #25
st([v6502_P])                   #26
ld(hi('v6502_next'),Y)          #27
jmp(Y,'v6502_next')             #28
ld(-30/2)                       #29

label('v6502_plp')
assert v6502_Nflag == 128
assert 2*v6502_Vflag == v6502_Vemu
ld([v6502_S])                   #12
ld(AC,X)                        #13
adda(1)                         #14
st([v6502_S])                   #15
ld([X])                         #16
st([v6502_Qn])                  #17 N flag
anda(v6502_Zflag)               #18
xora(v6502_Zflag)               #19
st([v6502_Qz])                  #20 Z flag
ld([X])                         #21
anda(~v6502_Vemu)               #22 V to bit 7
adda(v6502_Vflag)               #23
st([v6502_P])                   #24 All other flags
ld(hi('v6502_next'),Y)          #25
jmp(Y,'v6502_next')             #26
ld(-28/2)                       #27

label('v6502_rti')
ld([v6502_S])                   #12
ld(AC,X)                        #13
adda(3)                         #14
st([v6502_S])                   #15
ld([X])                         #16
st([v6502_Qn])                  #17 N flag
anda(v6502_Zflag)               #18
xora(v6502_Zflag)               #19
st([v6502_Qz])                  #20 Z flag
ld(0,Y)                         #21
ld([Y,X])                       #22
st([Y,Xpp])                     #23 Just X++
anda(~v6502_Vemu)               #24 V to bit 7
adda(v6502_Vflag)               #25
st([v6502_P])                   #26 All other flags
ld([Y,X])                       #27
st([Y,Xpp])                     #28 Just X++
st([v6502_PCL])                 #29
ld([Y,X])                       #30
st([v6502_PCH])                 #31
nop()                           #32
ld(hi('v6502_next'),Y)          #33
jmp(Y,'v6502_next')             #34
ld(-36/2)                       #35


#-----------------------------------------------------------------------
#
#  $1200 ROM page 18: Extended vbl & SYS calls
#
#-----------------------------------------------------------------------

align(0x100, size=0x100)

#-----------------------------------------------------------------------
#       Extended vertical blank logic: interrupts
#-----------------------------------------------------------------------

# Check if an IRQ handler is defined
label('vBlankFirst#75')
ld([Y,vIRQ_v5])                 #75
ora([Y,vIRQ_v5+1])              #76
bne('vBlankFirst#79')           #77
ld([vPC])                       #78
runVcpu(190-79-extra,           #79 Application cycles (scan line 0)
    '---D line 0 timeout but no irq',
    returnTo='vBlankFirst#190')

label('vBlankFirst#79')
st([vIrqSave+0])                #79 Save vPC
ld([vPC+1])                     #80
st([vIrqSave+1])                #81
ld([vAC])                       #82 Save vAC
st([vIrqSave+2])                #83
ld([vAC+1])                     #84
st([vIrqSave+3])                #85
ld([Y,vIRQ_v5])                 #86 Set vPC to vIRQ
suba(2)                         #87
st([vPC])                       #88
ld([Y,vIRQ_v5+1])               #89
st([vPC+1])                     #90
ld([vCpuSelect])                #91 Save vCpuSelect
st([vIrqSave+4])                #92
ld(hi('ENTER'))                 #93 Set vCpuSelect to ENTER (=regular vCPU)
st([vCpuSelect])                #94
runVcpu(190-95-extra,           #95 Application cycles (scan line 0)
    '---D line 0 timeout with irq',
    returnTo='vBlankFirst#190')

# vRTI immediate resume
label('vRTI#25')
ld([vIrqSave+3])                #25
st([vAC+1])                     #26
ld([vIrqSave+4])                #27
st([vCpuSelect],Y)              #28
ld(-32//2)                      #29
jmp(Y,'ENTER')                  #30
adda([vTicks])                  #31-32=-1


# Entered last line of vertical blank (line 40)
label('vBlankLast#34')

#-----------------------------------------------------------------------
#       Extended vertical blank logic: game controller decoding
#-----------------------------------------------------------------------

# Game controller types
# TypeA: Based on 74LS165 shift register (not supported)
# TypeB: Based on CD4021B shift register (standard)
# TypeC: Based on priority encoder
#
# Notes:
# - TypeA was only used during development and first beta test, before ROM v1
# - TypeB appears as type A with negative logic levels
# - TypeB is the game controller type that comes with the original kit and ROM v1
# - TypeB is mimicked by BabelFish / Pluggy McPlugface
# - TypeB requires a prolonged /SER_LATCH, therefore vPulse is 8 scanlines, not 2
# - TypeB and TypeC can be sampled in the same scanline
# - TypeA is 1 scanline shifted as it looks at a different edge (XXX up or down?)
# - TypeC gives incomplete information: lower buttons overshadow higher ones
#
#       TypeC    Alias    Button TypeB
#       00000000  ^@   -> Right  11111110
#       00000001  ^A   -> Left   11111101
#       00000011  ^C   -> Down   11111011
#       00000111  ^G   -> Up     11110111
#       00001111  ^O   -> Start  11101111
#       00011111  ^_   -> Select 11011111
#       00111111  ?    -> B      10111111
#       01111111  DEL  -> A      01111111
#       11111111       -> (None) 11111111
#
#       Conversion formula:
#               f(x) := 254 - x

# Detect controller TypeC codes
ld([serialRaw])                 #34 if serialRaw in [0,1,3,7,15,31,63,127,255]
adda(1)                         #35
anda([serialRaw])               #36
bne('.buttons#39')              #37

# TypeC
ld([serialRaw])                 #38 [TypeC] if serialRaw < serialLast
adda(1)                         #39
anda([serialLast])              #40
bne('.buttons#43')              #41
ld(254)                         #42 then clear the selected bit
nop()                           #43
bra('.buttons#46')              #44
label('.buttons#43')
suba([serialRaw])               #43,45
anda([buttonState])             #44
st([buttonState])               #45
label('.buttons#46')
ld([serialRaw])                 #46 Set the lower bits
ora([buttonState])              #47
label('.buttons#48')
st([buttonState])               #48
ld([serialRaw])                 #49 Update serialLast for next pass
jmp(Y,'vBlankLast#52')          #50
st([serialLast])                #51

# TypeB
# pChange = pNew & ~pOld
# nChange = nNew | ~nOld {DeMorgan}
label('.buttons#39')
ld(255)                         #39 [TypeB] Bitwise edge-filter to detect button presses
xora([serialLast])              #40
ora([serialRaw])                #41 Catch button-press events
anda([buttonState])             #42 Keep active button presses
ora([serialRaw])                #43
nop()                           #44
nop()                           #45
bra('.buttons#48')              #46
nop()                           #47


#-----------------------------------------------------------------------
#       More SYS functions
#-----------------------------------------------------------------------


# SYS_VDrawBits_134 implementation
label('sys_VDrawBits')
ld(0)                           #18
label('.sysVdb0')
st([vTmp])                      #19+i*25
adda([sysArgs+5],Y)             #20+i*25 Y=[sysPos+1]+[vTmp]
ld([sysArgs+2])                 #21+i*25 Select color
bmi(pc()+3)                     #22+i*25
bra(pc()+3)                     #23+i*25
ld([sysArgs+0])                 #24+i*25
ld([sysArgs+1])                 #24+i*25(!)
st([Y,X])                       #25+i*25 Draw pixel
ld([sysArgs+2])                 #26+i*25 Shift byte left
adda(AC)                        #27+i*25
st([sysArgs+2])                 #28+i*25
ld([vTmp])                      #29+i*25 Unrolled loop (once)
adda([sysArgs+5])               #31+i*25
adda(1,Y)                       #30+i*25 Y=[sysPos+1]+[vTmp]+1
ld([sysArgs+2])                 #32+i*25 Select color
bmi(pc()+3)                     #33+i*25
bra(pc()+3)                     #34+i*25
ld([sysArgs+0])                 #35+i*25
ld([sysArgs+1])                 #35+i*25(!)
st([Y,X])                       #36+i*25 Draw pixel
ld([sysArgs+2])                 #37+i*25 Shift byte left
adda(AC)                        #38+i*25
st([sysArgs+2])                 #39+i*25
ld([vTmp])                      #40+i*25 Loop counter
suba(6)                         #41+i*25
bne('.sysVdb0')                 #42+i*25
adda(8)                         #43+i*25 Steps of 2
ld(hi('REENTER'),Y)             #119
jmp(Y,'REENTER')                #120
ld(-124/2)                      #121

# SYS_ResetWaveforms_v4_50 implementation
label('sys_ResetWaveforms')
ld([vAC+0])                     #18 X=4i
adda(AC)                        #19
adda(AC,X)                      #20
ld([vAC+0])                     #21
st([Y,Xpp])                     #22 Sawtooth: T[4i+0] = i
anda(0x20)                      #23 Triangle: T[4i+1] = 2i if i<32 else 127-2i
bne(pc()+3)                     #24
ld([vAC+0])                     #25
bra(pc()+3)                     #26
adda([vAC+0])                   #26,27
xora(127)                       #27
st([Y,Xpp])                     #28
ld([vAC+0])                     #29 Pulse: T[4i+2] = 0 if i<32 else 63
anda(0x20)                      #30
bne(pc()+3)                     #31
bra(pc()+3)                     #32
ld(0)                           #33
ld(63)                          #33(!)
st([Y,Xpp])                     #34
ld([vAC+0])                     #35 Sawtooth: T[4i+3] = i
st([Y,X])                       #36
adda(1)                         #37 i += 1
st([vAC+0])                     #38
xora(64)                        #39 For 64 iterations
beq(pc()+3)                     #40
bra(pc()+3)                     #41
ld(-2)                          #42
ld(0)                           #42(!)
adda([vPC])                     #43
st([vPC])                       #44
ld(hi('REENTER'),Y)             #45
jmp(Y,'REENTER')                #46
ld(-50/2)                       #47

# SYS_ShuffleNoise_v4_46 implementation
label('sys_ShuffleNoise')
ld([vAC+0],X)                   #18 tmp = T[4j]
ld([Y,X])                       #19
st([vTmp])                      #20
ld([vAC+1],X)                   #21 T[4j] = T[4i]
ld([Y,X])                       #22
ld([vAC+0],X)                   #23
st([Y,X])                       #24
adda(AC)                        #25 j += T[4i]
adda(AC,)                       #26
adda([vAC+0])                   #27
st([vAC+0])                     #28
ld([vAC+1],X)                   #29 T[4i] = tmp
ld([vTmp])                      #30
st([Y,X])                       #31
ld([vAC+1])                     #32 i += 1
adda(4)                         #33
st([vAC+1])                     #34
beq(pc()+3)                     #35 For 64 iterations
bra(pc()+3)                     #36
ld(-2)                          #37
ld(0)                           #37(!)
adda([vPC])                     #38
st([vPC])                       #39
ld(hi('NEXTY'),Y)               #40
jmp(Y,'NEXTY')                  #41
ld(-44/2)                       #42

# SYS_ScanMemory_DEVROM_50 implementation
label('sys_ScanMemory')
ld([sysArgs+0],X)                    #18
ld([Y,X])                            #19
label('.sysSme#20')
xora([sysArgs+2])                    #20
beq('.sysSme#23')                    #21
ld([Y,X])                            #22
xora([sysArgs+3])                    #23
beq('.sysSme#26')                    #24
ld([sysArgs+0])                      #25
adda(1);                             #26
st([sysArgs+0],X)                    #27
ld([vAC])                            #28
suba(1)                              #29
beq('.sysSme#32')                    #30 return zero
st([vAC])                            #31
ld(-18/2)                            #14 = 32 - 18
adda([vTicks])                       #15
st([vTicks])                         #16
adda(min(0,maxTicks -(28+18)/2))     #17
bge('.sysSme#20')                    #18
ld([Y,X])                            #19
ld(-2)                               #20 restart
adda([vPC])                          #21
st([vPC])                            #22
ld(hi('REENTER'),Y)                  #23
jmp(Y,'REENTER')                     #24
ld(-28/2)                            #25
label('.sysSme#32')
st([vAC+1])                          #32 return zero
ld(hi('REENTER'),Y)                  #33
jmp(Y,'REENTER')                     #34
ld(-38/2)                            #35
label('.sysSme#23')
nop()                                #23 success
nop()                                #24
ld([sysArgs+0])                      #25
label('.sysSme#26')
st([vAC])                            #26 success
ld([sysArgs+1])                      #27
st([vAC+1])                          #28
ld(hi('REENTER'),Y)                  #29
jmp(Y,'REENTER')                     #30
ld(-34/2)                            #31

# SYS_ScanMemoryExt_DEVROM_50 implementation
label('sys_ScanMemoryExt')
ora(0x3c,X)                          #18
ctrl(X)                              #19
ld([sysArgs+1],Y)                    #20
ld([sysArgs+0],X)                    #21
ld([Y,X])                            #22
nop()                                #23
label('.sysSmx#24')
xora([sysArgs+2])                    #24
beq('.sysSmx#27')                    #25
ld([Y,X])                            #26
xora([sysArgs+3])                    #27
beq('.sysSmx#30')                    #28
ld([sysArgs+0])                      #29
adda(1);                             #30
st([sysArgs+0],X)                    #31
ld([vAC])                            #32
suba(1)                              #33
beq('.sysSmx#36')                    #34 return zero
st([vAC])                            #35
ld(-18/2)                            #18 = 36 - 18
adda([vTicks])                       #19
st([vTicks])                         #20
adda(min(0,maxTicks -(30+18)/2))     #21
bge('.sysSmx#24')                    #22
ld([Y,X])                            #23
ld([vPC])                            #24
suba(2)                              #25 restart
st([vPC])                            #26
ld(hi(ctrlBits),Y)                   #27 restore and return
ld([Y,ctrlBits])                     #28
anda(0xfc,X)                         #29
ctrl(X)                              #30
ld([vTmp])                           #31
ld(hi('NEXTY'),Y)                    #32
jmp(Y,'NEXTY')                       #33
ld(-36/2)                            #34
label('.sysSmx#27')
nop()                                #27 success
nop()                                #28
ld([sysArgs+0])                      #29
label('.sysSmx#30')
st([vAC])                            #30 success
ld([sysArgs+1])                      #31
nop()                                #32
nop()                                #33
nop()                                #34
nop()                                #35
label('.sysSmx#36')
st([vAC+1])                          #36
ld(hi(ctrlBits),Y)                   #37 restore and return
ld([Y,ctrlBits])                     #38
anda(0xfc,X)                         #39
ctrl(X)                              #40
ld([vTmp])                           #41
ld(hi('NEXTY'),Y)                    #42
jmp(Y,'NEXTY')                       #43
ld(-46/2)                            #44


#-----------------------------------------------------------------------
#
#  $1300 ROM page 19: SYS calls
#
#-----------------------------------------------------------------------

align(0x100, size=0x100)

# SYS_CopyMemory_v6_80 implementation

label('sys_CopyMemory')
ble('.sysCm#20')                     #18   goto burst6
suba(6)                              #19
bge('.sysCm#22')                     #20   goto burst6
ld([sysArgs+3],Y)                    #21
adda(3)                              #22
bge('.sysCm#25')                     #23   goto burst3
ld([sysArgs+2],X)                    #24

adda(2)                              #25   single
st([vAC])                            #26
ld([Y,X])                            #27
ld([sysArgs+1],Y)                    #28
ld([sysArgs+0],X)                    #29
st([Y,X])                            #30
ld([sysArgs+0])                      #31
adda(1)                              #32
st([sysArgs+0])                      #33
ld([sysArgs+2])                      #34
adda(1)                              #35
st([sysArgs+2])                      #36
ld([vAC])                            #37
beq(pc()+3)                          #38
bra(pc()+3)                          #39
ld(-2)                               #40
ld(0)                                #40!
adda([vPC])                          #41
st([vPC])                            #42
ld(hi('REENTER'),Y)                  #43
jmp(Y,'REENTER')                     #44
ld(-48/2)                            #45

label('.sysCm#25')
st([vAC])                            #25   burst3
for i in range(3):
  ld([Y,X])                            #26+3*i
  st([sysArgs+4+i])                    #27+3*i
  st([Y,Xpp]) if i<2 else None         #28+3*i
ld([sysArgs+1],Y)                    #34
ld([sysArgs+0],X)                    #35
for i in range(3):
  ld([sysArgs+4+i])                    #36+2*i
  st([Y,Xpp])                          #37+2*i
ld([sysArgs+0])                      #42
adda(3)                              #43
st([sysArgs+0])                      #44
ld([sysArgs+2])                      #45
adda(3)                              #46
st([sysArgs+2])                      #47
ld([vAC])                            #48
beq(pc()+3)                          #49
bra(pc()+3)                          #50
ld(-2)                               #51
ld(0)                                #51!
adda([vPC])                          #52
st([vPC])                            #53
ld(hi('NEXTY'),Y)                    #54
jmp(Y,'NEXTY')                       #55
ld(-58/2)                            #56

label('.sysCm#20')
nop()                                #20   burst6
ld([sysArgs+3],Y)                    #21
label('.sysCm#22')
st([vAC])                            #22   burst6
ld([sysArgs+2],X)                    #23
for i in range(6):
  ld([Y,X])                            #24+i*3
  st([vLR+i if i<2 else sysArgs+2+i])  #25+i*3
  st([Y,Xpp]) if i<5 else None         #26+i*3 if i<5
ld([sysArgs+1],Y)                    #41
ld([sysArgs+0],X)                    #42
for i in range(6):
  ld([vLR+i if i<2 else sysArgs+2+i])  #43+i*2
  st([Y,Xpp])                          #44+i*2
ld([sysArgs+0])                      #55
adda(6)                              #56
st([sysArgs+0])                      #57
ld([sysArgs+2])                      #58
adda(6)                              #59
st([sysArgs+2])                      #60

ld([vAC])                            #61
bne('.sysCm#64')                     #62
ld(hi('REENTER'),Y)                  #63
jmp(Y,'REENTER')                     #64
ld(-68/2)                            #65

label('.sysCm#64')
ld(-52/2)                            #64
adda([vTicks])                       #13 = 65 - 52
st([vTicks])                         #14
adda(min(0,maxTicks-(26+52)/2))      #15   could probably be min(0,maxTicks-(26+52)/2)
bge('sys_CopyMemory')                #16
ld([vAC])                            #17
ld(-2)                               #18   notime
adda([vPC])                          #19
st([vPC])                            #20
ld(hi('REENTER'),Y)                  #21
jmp(Y,'REENTER')                     #22
ld(-26/2)                            #23

#-----------------------------------------------------------------------
# SYS_CopyMemoryExt_v6_100 implementation

label('sys_CopyMemoryExt')

adda(AC)                             #18
adda(AC)                             #19
ora(0x3c)                            #20
st([vTmp])                           #21 [vTmp] = src ctrl value
ld([vAC+1])                          #22
anda(0xfc)                           #23
ora(0x3c)                            #24
st([vLR])                            #25 [vLR] = dest ctrl value

label('.sysCme#26')
ld([vAC])                            #26
ble('.sysCme#29')                    #27   goto burst5
suba(5)                              #28
bge('.sysCme#31')                    #29   goto burst5
ld([sysArgs+3],Y)                    #30
adda(4)                              #31

st([vAC])                            #32   single
ld([vTmp],X)                         #33
ctrl(X)                              #34
ld([sysArgs+2],X)                    #35
ld([Y,X])                            #36
ld([vLR],X)                          #37
ctrl(X)                              #38
ld([sysArgs+1],Y)                    #39
ld([sysArgs+0],X)                    #40
st([Y,X])                            #41
ld(hi(ctrlBits), Y)                  #42
ld([Y,ctrlBits])                     #43
ld(AC,X)                             #44
ctrl(X)                              #45
ld([sysArgs+0])                      #46
adda(1)                              #47
st([sysArgs+0])                      #48
ld([sysArgs+2])                      #49
adda(1)                              #50
st([sysArgs+2])                      #51
ld([vAC])                            #52  done?
beq(pc()+3)                          #53
bra(pc()+3)                          #54
ld(-2)                               #55  restart
ld(0)                                #55! finished
adda([vPC])                          #56
st([vPC])                            #57
ld(hi('NEXTY'),Y)                    #58
jmp(Y,'NEXTY')                       #59
ld(-62/2)                            #60

label('.sysCme#29')
nop()                                #29   burst5
ld([sysArgs+3],Y)                    #30
label('.sysCme#31')
st([vAC])                            #31   burst5
ld([vTmp],X)                         #32
ctrl(X)                              #33
ld([sysArgs+2],X)                    #34
for i in range(5):
  ld([Y,X])                            #35+i*3
  st([vLR+1 if i<1 else sysArgs+3+i])  #36+i*3
  st([Y,Xpp]) if i<4 else None         #37+i*3 if i<4
ld([vLR],X)                          #49
ctrl(X)                              #50
ld([sysArgs+1],Y)                    #51
ld([sysArgs+0],X)                    #52
for i in range(5):
  ld([vLR+1 if i<1 else sysArgs+3+i])  #53+i*2
  st([Y,Xpp])                          #54+i*2
ld([sysArgs+0])                      #63
adda(5)                              #64
st([sysArgs+0])                      #65
ld([sysArgs+2])                      #66
adda(5)                              #67
st([sysArgs+2])                      #68

ld([vAC])                            #69
bne('.sysCme#72')                    #70
ld(hi(ctrlBits), Y)                  #71  we're done!
ld([Y,ctrlBits])                     #72
anda(0xfc,X)                         #73
ctrl(X)                              #74
ld([vTmp])                           #75  always read after ctrl
ld(hi('NEXTY'),Y)                    #76
jmp(Y,'NEXTY')                       #77
ld(-80/2)                            #78

label('.sysCme#72')
ld(-52/2)                            #72
adda([vTicks])                       #21 = 72 - 52
st([vTicks])                         #22
adda(min(0,maxTicks-(40+52)/2))      #23
bge('.sysCme#26')                    #24  enough time for another loop
ld(-2)                               #25
adda([vPC])                          #26  restart
st([vPC])                            #27
ld(hi(ctrlBits), Y)                  #28
ld([Y,ctrlBits])                     #29
anda(0xfc,X)                         #30
ctrl(X)                              #31
ld([vTmp])                           #32 always read after ctrl
ld(hi('REENTER'),Y)                  #33
jmp(Y,'REENTER')                     #34
ld(-38/2)                            #35 max: 38 + 52 = 90 cycles


#-----------------------------------------------------------------------
# Trampoline return stub

label('lupReturn#19')
ld(0)                           #19 trampoline returns here
st([vAC+1])                     #20
ld([vCpuSelect])                #21 to current interpreter
adda(1,Y)                       #22
ld(-26/2)                       #23
jmp(Y,'NEXT')                   #24 using NEXT
ld([vPC+1],Y)                   #25


#-----------------------------------------------------------------------
# Continuation of SYS_ExpanderControl
# dealing with extended banking codes

if WITH_512K_BOARD:
  label('sysEx#30')
  xora([videoModeC])                  #30
  anda(0xfe)                          #31 Save 7 bits of extended banking
  xora([videoModeC])                  #32 code into videomodeC.
  st([videoModeC])                    #33 
  ld(hi('NEXTY'),Y)                   #34
  jmp(Y,'NEXTY')                      #35
  ld(-38/2)                           #36




#-----------------------------------------------------------------------
#
#  $1400 ROM page 20: Multiply Divide
#
#-----------------------------------------------------------------------

fillers(until=0xff)
label('FSM14_ENTER')
bra(pc()+4)                     #0
align(0x100, size=0x100)
bra([fsmState])                 #1
assert (pc() & 255) == (symbol('NEXT') & 255)
label('FSM14_NEXT')
adda([vTicks])                  #0
bge([fsmState])                 #1
st([vTicks])                    #2
adda(maxTicks)                  #3
bgt(pc()&255)                   #4
suba(1)                         #5
ld(hi('vBlankStart'),Y)         #6
jmp(Y,[vReturn])                #7
ld([channel])                   #8

#-----------------------------------------------------------------------
# sys_Multiply_s16, sum:s16 = x:s16 * y:s16
# x:args0:1 y:args2:3 sum:args4:5 mask:args6:7
#
# Original implementation by at67.
# Reworked with two loops to better leverage fsm.

label('sys_Multiply_s16')
ld('sysm#3a')                   #18
st([fsmState])                  #19
ld((pc()>>8)-1)                 #20
st([vCpuSelect])                #21
ld(1)                           #22
st([sysArgs+6])                 #23
bra('NEXT')                     #24
ld(-26/2)                       #25

label('sysm#3a')
ld('sysm#3b')                   #3
st([fsmState])                  #4
ld([sysArgs+6])                 #5
anda([sysArgs+2])               #6
nop()                           #7
beq('NEXT')                     #8
ld(-10/2)                       #9
ld([sysArgs+4])                 #10 load sum.lo
adda([sysArgs+0])               #11 load x.lo
st([sysArgs+4])                 #12 sum.lo = sum.lo + x.lo
bmi(pc()+4)                     #13 check for carry
suba([sysArgs+0])               #14 get original sum.lo back
bra(pc()+4)                     #15
ora([sysArgs+0])                #16 carry in bit 7
nop()                           #15
anda([sysArgs+0])               #16 carry in bit 7
anda(0x80,X)                    #17
ld([X])                         #18
adda([sysArgs+5])               #19
adda([sysArgs+1])               #20
st([sysArgs+5])                 #21 sum.hi = sum.hi + x.hi
bra('NEXT')                     #22
ld(-24/2)                       #23

label('sysm#3b')
ld([sysArgs+0])                 #3  AC = x.lo
anda(0x80,X)                    #4  X = AC & 0x80
adda(AC)                        #5  AC = x.lo <<1
st([sysArgs+0])                 #6  x.lo = AC
ld([X])                         #7  AC = X >>7
adda([sysArgs+1])               #8
adda([sysArgs+1])               #9
st([sysArgs+1])                 #10 x.hi = x.hi <<1 + AC
ld([sysArgs+6])                 #11
adda([sysArgs+6])               #12
beq('sysm#15b')                 #13
st([sysArgs+6])                 #14
ld('sysm#3a')                   #15
st([fsmState])                  #16
nop()
bra('NEXT')                     #17
ld(-20/2)                       #18
label('sysm#15b')
ld([sysArgs+3])                 #15
beq(pc()+3)                     #16
bra(pc()+2)                     #17
ld(1)                           #18
st([sysArgs+6])                 #19,18
ld('sysm#3c')                   #20
st([fsmState])                  #21
bra('NEXT')                     #22
ld(-24/2)                       #23

label('sysm#3c')
ld([sysArgs+6])                 #3
beq('sysm#6c')                  #4
anda([sysArgs+3])               #5
beq('sysm#8c')                  #6
ld([sysArgs+1])                 #7 add
adda([sysArgs+5])               #8
st([sysArgs+5])                 #9
label('sysm#10c')
ld([sysArgs+1])                 #10
adda(AC)                        #11
st([sysArgs+1])                 #12
ld([sysArgs+6])                 #13
adda(AC)                        #14
st([sysArgs+6])                 #15
bra('NEXT')                     #16
ld(-18/2)                       #17
label('sysm#8c')
bra('sysm#10c')                 #8  no add
nop()                           #9
label('sysm#6c')
ld([sysArgs+4])                 #6  exit
st([vAC])                       #7
ld([sysArgs+5])                 #8
st([vAC+1])                     #9
ld(hi('ENTER'))                 #10
st([vCpuSelect])                #11
ld(hi('NEXTY'),Y)               #12
jmp(Y,'NEXTY')                  #13
ld(-16//2)                      #14


#-----------------------------------------------------------------------
# sys_Divide_u16
# x:args0:1 y:args2:3 rem:args4:5 counter:args6
#
# Original implementation by at67.
# Reworked to handle unrestricted unsigned divisions

label('sys_Divide_u16')
ld('sysd#3a')                   #18
st([fsmState])                  #19
ld((pc()>>8)-1)                 #20
st([vCpuSelect])                #21
ld(0)                           #22 init
st([sysArgs+4])                 #23
st([sysArgs+5])                 #24
ld(16)                          #25
st([sysArgs+6])                 #26
nop()                           #27
bra('NEXT')                     #28
ld(-30/2)                       #29

label('sysd#3a')
ld('sysd#3b')                   #3 
st([fsmState])                  #4
ld([sysArgs+0])                 #5  lsl sysArgs5<4<1<0
anda(0x80,X)                    #6
adda(AC)                        #7
st([sysArgs+0])                 #8
ld([sysArgs+1])                 #9
bmi('sysd#12a')                 #10
adda(AC)                        #11
adda([X])                       #12
st([sysArgs+1])                 #13
ld([sysArgs+4])                 #14
anda(0x80,X)                    #15 
bra('sysd#18a')                 #16
adda(AC)                        #17
label('sysd#12a')
adda([X])                       #12
st([sysArgs+1])                 #13
ld([sysArgs+4])                 #14
anda(0x80,X)                    #15 
adda(AC)                        #16
adda(1)                         #17
label('sysd#18a')
st([sysArgs+4])                 #18
ld([sysArgs+5])                 #19
adda(AC)                        #20
adda([X])                       #21
st([sysArgs+5])                 #22
nop()                           #23
bra('NEXT')                     #24
ld(-26/2)                       #25

label('sysd#3b')
ld([sysArgs+4])                 #3 vAC=sysArgs[45]-sysArgs[23]
bmi(pc()+5)                     #4>
suba([sysArgs+2])               #5
st([vAC])                       #6
bra(pc()+5)                     #7>
ora([sysArgs+2])                #8
st([vAC])                       #6-
nop()                           #7
anda([sysArgs+2])               #8
anda(0x80,X)                    #9-
ld([sysArgs+5])                 #10
bmi('sysd#13b')                 #11
suba([sysArgs+3])               #12
suba([X])                       #13
st([vAC+1])                     #14
ora([sysArgs+3])                #15
bmi(pc()+3)                     #16
bra(pc()+3)                     #17
ld('sysd#3c')                   #18
ld('sysd#3d')                   #18
st([fsmState])                  #19
bra('NEXT')                     #20
ld(-22/2)                       #21
label('sysd#13b')
suba([X])                       #13
st([vAC+1])                     #14
anda([sysArgs+3])               #15
bmi(pc()+3)                     #16
bra(pc()+3)                     #17
ld('sysd#3c')                   #18
ld('sysd#3d')                   #18
st([fsmState])                  #19
bra('NEXT')                     #20
ld(-22/2)                       #21

label('sysd#3c')
ld([sysArgs+0])                 #3 commit
ora(1)                          #4  quotient|=1
st([sysArgs+0])                 #5
ld([vAC])                       #6  sysArgs[45]=vAC 
st([sysArgs+4])                 #7
ld([vAC+1])                     #8
st([sysArgs+5])                 #9
ld([sysArgs+6])                 #10 counter
suba(1)                         #11
beq('sysd#14c')                 #12
st([sysArgs+6])                 #13
ld('sysd#3a')                   #14
st([fsmState])                  #15
bra('NEXT')                     #16
ld(-18/2)                       #17
label('sysd#14c')
ld('sysd#3e')                   #14
st([fsmState])                  #15
bra('NEXT')                     #16
ld(-18/2)                       #17

label('sysd#3d')
ld('sysd#3a')                   #3
st([fsmState])                  #4
ld([sysArgs+6])                 #5 counter
suba(1)                         #6
st([sysArgs+6])                 #7
bne('NEXT')                     #8
ld(-10/2)                       #9
ld('sysd#3e')                   #10
st([fsmState])                  #11
bra('NEXT')                     #12
ld(-14/2)                       #13

label('sysd#3e')
ld([sysArgs+0])                 #3 copy quotient into vAC
st([vAC])                       #4
ld([sysArgs+1])                 #5
st([vAC+1])                     #6
ld(hi('ENTER'))                 #7 exit fsm
st([vCpuSelect])                #8
ld(hi('REENTER'),Y)             #9
jmp(Y,'REENTER')                #10
ld(-14//2)                      #11


#-----------------------------------------------------------------------
# Opcodes

label('fsm14op1#21')
ld(1)                           #21
adda([vPC])                     #22
st([vPC])                       #23
ld(hi('FSM14_ENTER'))           #24
st([vCpuSelect])                #25
bra('NEXT')                     #26
ld(-28/2)                       #27

# MULW implementation
label('mulw#3a')
ld('sysm#3a')                   #3
st([fsmState])                  #4
ld(1)                           #5
nop()                           #6
label('mulw#7a')
st([vTmp])                      #7
ld([vAC])                       #8
st([sysArgs+2])                 #9
ld([vAC+1])                     #10
st([sysArgs+3])                 #11
ld([sysArgs+6])                 #12
adda(1,X)                       #13
ld([X])                         #14
st([sysArgs+1])                 #15
ld([sysArgs+6],X)               #16
ld([X])                         #17
st([sysArgs+0])                 #18
ld(0)                           #19
st([sysArgs+4])                 #20
st([sysArgs+5])                 #21
ld([vTmp])                      #22
st([sysArgs+6])                 #23
bra('NEXT')                     #24
ld(-26/2)                       #25

# RDIVU implementation
label('rdivu#3a')
ld('sysd#3a')                   #3
st([fsmState])                  #4
bra('mulw#7a')                  #5
ld(16)                          #6



#-----------------------------------------------------------------------
#
#  $1500 ROM page 21: SYS_Exec & SYS_Loader
#
#-----------------------------------------------------------------------

fillers(until=0xff)
label('FSM15_ENTER')
bra(pc()+4)                     #0
align(0x100, size=0x100)
bra([fsmState])                 #1
assert (pc() & 255) == (symbol('NEXT') & 255)
label('FSM15_NEXT')
adda([vTicks])                  #0
bge([fsmState])                 #1
st([vTicks])                    #2
adda(maxTicks)                  #3
bgt(pc()&255)                   #4
suba(1)                         #5
ld(hi('vBlankStart'),Y)         #6
jmp(Y,[vReturn])                #7
ld([channel])                   #8

#-----------------------------------------------------------------------
# Micro FSM instructions

def fsmAsm(op,arg=None):
  bra('fsm-' + op)                    #3
  ld(arg) if arg!=None else nop()     #4

# uFSM opcode 'uANDI'
# - vAC := vAC & arg
label('fsm-uANDI')
anda([vAC])                     #5
st([vAC])                       #6
ld(0)                           #7
st([vAC+1])                     #8
label('fsm-next#9')
ld([fsmState])                  #9
label('fsm-next#10')
adda(2)                         #10
st([fsmState])                  #11
bra('NEXT')                     #12
ld(-14/2)                       #13

# uFSM opcode 'uST'
# - [arg] := vACL
label('fsm-uST')
ld(AC,X)                        #5
ld([vAC])                       #6
st([X])                         #7
label('fsm-next#8')
bra('fsm-next#10')              #8
ld([fsmState])                  #9

# uFSM opcode 'uXORI'
# - vAC := vAC ^ arg
label('fsm-uXORI')
xora([vAC])                     #5
bra('fsm-next#8')               #6
st([vAC])                       #7

# uFSM opcode 'uLDI'
# - vAC := byte [arg]
label('fsm-uLDI')
st([vAC])                       #5
ld(0)                           #6
bra('fsm-next#9')               #7
st([vAC+1])                     #8

# uFSM opcode 'uBNE'
# - branch if vAC!=0
label('fsm-uBNE')
st([vTmp])                      #5
ld([vAC])                       #6
ora([vAC+1])                    #7
beq('fsm-next#10')              #8
ld([fsmState])                  #9
ld([vTmp])                      #10
st([fsmState])                  #11
bra('NEXT')                     #12
ld(-14/2)                       #13

# uFSM opcode 'uLDW'
# - vAC := word [arg]
label('fsm-uLDW')
st([vTmp])                      #5
adda(1,X)                       #6
ld([X])                         #7
st([vAC+1])                     #8
ld([vTmp],X)                    #9
nop()                           #10
label('fsm-ldw#11')
ld([X])                         #11
st([vAC])                       #12
ld([fsmState])                  #13
adda(2)                         #14
st([fsmState])                  #15
bra('NEXT')                     #16
ld(-18/2)                       #17

# uFSM opcode 'uRET'
# - exit fsm and direct vCPU to vLR
label('fsm-uRET')
ld(hi('ENTER'))                 #5
st([vCpuSelect])                #6
ld(hi('RET'),Y)                 #7
jmp(Y,'RET')                    #8
nop()                           #9

# uFSM opcode 'uMSK'
# - clear channelMask if segment [sysArgs[23],sysArgs[23]+sysArgs[4])
#   overlaps OSCL/OSCH for audio channels 1, 2, 3.
label('fsm-uMSK')
ld([sysArgs+3])                 #5
suba(1)                         #6
anda(0xfc)                      #7
st([vTmp])                      #8
ld([sysArgs+2])                 #9
adda([sysArgs+4])               #10
adda(1)                         #11
anda(0xfe)                      #12
ora([vTmp])                     #13
beq(pc()+3)                     #14
bra(pc()+3)                     #15
ld(0xff)                        #16
ld(0xfc)                        #16
anda([channelMask])             #17
st([channelMask])               #18
label('fsm-next#19')
ld([fsmState])                  #19
adda(2)                         #20
st([fsmState])                  #21
bra('NEXT')                     #22
ld(-24/2)                       #23

# uFSM opcode 'uSTX'
# - store vACL at address sysArgs[3:2]
# - increment address sysArgs[2]
# - decrement byte counter sysArgs[4] with copy in vAC
label('fsm-uSTX')
ld([vAC])                       #5
ld([sysArgs+3],Y)               #6
ld([sysArgs+2],X)               #7
st([Y,X])                       #8
ld([sysArgs+2])                 #9
adda(1)                         #10
st([sysArgs+2])                 #11
ld([sysArgs+4])                 #12
suba(1)                         #13
st([sysArgs+4])                 #14
st([vAC])                       #15
ld(0)                           #16
bra('fsm-next#19')              #17
st([vAC+1])                     #18

#-----------------------------------------------------------------------
# SYS_Exec_80 implementation


# uFSM opcode 'uLUP'
# - LUP byte at address sysArgs[1:0]
# - increment sysArgs[0] skipping trampolines
label('fsm-uLUP')
ld([fsmState])                  #5
adda(2)                         #6
st([sysArgs+6])                 #7 save pc
ld('fsm-lup#3')                 #8 next fragment
st([fsmState])                  #9
ld([sysArgs+1],Y)               #10 jump to trampoline
jmp(Y,251)                      #11
ld([sysArgs+0])                 #12 continue to lupReturn#19

label('fsm-lup#3')
ld([sysArgs+6])                 #3
st([fsmState])                  #4 restore pc
ld([sysArgs+0])                 #5
suba(250)                       #6
bne('fsm-lup#9')                #7
st([sysArgs+0])                 #8 wrap at 251
ld([sysArgs+1])                 #9
adda(1)                         #10
st([sysArgs+1])                 #11
label('fsm-lup#12')
bra('NEXT')                     #12
ld(-14/2)                       #13
label('fsm-lup#9')
adda(251)                       #9
bra('fsm-lup#12')               #10
st([sysArgs+0])                 #11

# Exec microprogram
label('syse-prog')
fsmAsm('uLUP')
fsmAsm('uST', sysArgs+3)
label('syse-packet')
fsmAsm('uLUP')
fsmAsm('uST', sysArgs+2)
fsmAsm('uLUP')
fsmAsm('uST', sysArgs+4)
fsmAsm('uMSK')
label('syse-data')
fsmAsm('uLUP')
fsmAsm('uSTX')
fsmAsm('uBNE', 'syse-data')
fsmAsm('uLUP')
fsmAsm('uST', sysArgs+3)
fsmAsm('uBNE', 'syse-packet')
fsmAsm('uLDW', vLR)
fsmAsm('uBNE', 'syse-ret')
fsmAsm('uLUP')
fsmAsm('uST', vLR+1)
fsmAsm('uLUP')
fsmAsm('uST', vLR)
label('syse-ret')
fsmAsm('uRET')

label('sys_Exec')
ld('syse-prog')                 #18
st([fsmState])                  #19
ld((pc()>>8)-1)                 #20
st([vCpuSelect])                #21
bra('NEXT')                     #22
ld(-24/2)                       #23

#-----------------------------------------------------------------------
# SYS_Loader_DEVROM_44 implementation


# uFSM opcode 'uFAR'
# - jump to another page
label('fsm-uFAR')
st([vTmp])                      #5
ld([fsmState])                  #6
adda(2)                         #7
ld(hi('fsm-far-page'),Y)        #8
jmp(Y,[vTmp])                   #9
st([fsmState])                  #10

# uFSM opcode 'uSRIN', SeRialIN
# - wait until videoY==sysArgs0 and save IN into vAC
# - increment sysArgs0 to the next payload scanline
label('fsm-uSRIN')
ld([sysArgs+6])                 #5
xora([videoY])                  #6
st([vAC+1])                     #7 zero eventually
bne('NEXT')                     #8 restart until videoY==sysArgs0
ld(-10/2)                       #9
ld([fsmState])                  #10 increment fsmState
adda(2)                         #11
st([fsmState])                  #12
ld([sysArgs+6])                 #13 next position
anda(1)                         #14 - even or odd?
bne('sys-srin#17')              #15 
ld([sysArgs+6])                 #16
adda(4)                         #17 even
xora(242)                       #18
beq(pc()+3)                     #19
bra(pc()+3)                     #20
xora(242)                       #21
ld(185)                         #21
bra('sys-srin#24')              #22
st([sysArgs+6])                 #23
label('sys-srin#17')
anda(0xf)                       #17 odd magic
adda([sysArgs+6])               #18
xora(4)                         #19
bpl(pc()+3)                     #20
bra(pc()+2)                     #21
ora(11)                         #22
st([sysArgs+6])                 #23,22
label('sys-srin#24')
nop()                           #24
st(IN,[vAC])                    #25 finally read byte
bra('NEXT')                     #26
ld(-28/2)                       #27

# Loader microprogram
label('sysl-prog')
fsmAsm('uLDI', 0x15)            # echo color gray
label('sysl-frame')
fsmAsm('uFAR', 'sysl-echo#11')  # display dot
fsmAsm('uLDI', 207)
fsmAsm('uST', sysArgs+6)        # reset serial index
fsmAsm('uSRIN')
fsmAsm('uXORI', ord('L'))
fsmAsm('uBNE', 'sysl-prog')     # invalid packet
fsmAsm('uSRIN')
fsmAsm('uANDI', 0x3f)           # six valid bits only
fsmAsm('uST', sysArgs+4)        # len
fsmAsm('uBNE', 'sysl-packet')
fsmAsm('uSRIN')
fsmAsm('uST', vLR)              # execl
fsmAsm('uSRIN')
fsmAsm('uST', vLR+1)            # exech
label('sysl-ret')
fsmAsm('uRET')                  # return
label('sysl-packet')
fsmAsm('uSRIN')
fsmAsm('uST', sysArgs+2)        # addrl
fsmAsm('uSRIN')
fsmAsm('uST', sysArgs+3)        # addrh
fsmAsm('uMSK')
fsmAsm('uFAR', 'sysl-chk#11')   # checks
fsmAsm('uBNE', 'sysl-prog')     # invalid packet
label('sysl-data')
fsmAsm('uSRIN')
fsmAsm('uSTX')
fsmAsm('uBNE', 'sysl-data')
fsmAsm('uST', sysArgs+5)        # clear error flag
fsmAsm('uLDI', 0xc)             # next dot color
fsmAsm('uBNE', 'sysl-frame')

#-----------------------------------------------------------------------
#
#   $1600 ROM page 22: Misc overflow
#
#-----------------------------------------------------------------------

align(0x100, size=0x100)

#-----------------------------------------------------------------------
# Loader
#-----------------------------------------------------------------------

label('fsm-far-page')

label('sys_Loader')
suba(12)                        #18
bge(pc()+3)                     #19
bra(pc()+3)                     #20
ld(0)                           #21
ld([sysArgs+0])                 #21
st([sysArgs+0])                 #22
ld('sysl-prog')                 #23
st([fsmState])                  #24
ld(hi('FSM15_ENTER'))           #25
st([vCpuSelect])                #26
adda(1,Y)                       #27
jmp(Y,'NEXT')                   #28
ld(-30/2)                       #29

label('sysl-echo#11')
ld([sysArgs+0])                 #11
bne('sysl-echo#14')             #12
ld(hi('sysl-prog'),Y)           #13
jmp(Y,'NEXT')                   #14
ld(-16/2)                       #15
label('sysl-echo#14')
ld(AC,X)                        #14
suba(11)                        #15
anda(127)                       #16
adda(12)                        #17
st([sysArgs+0])                 #18
ld([sysArgs+1],Y)               #19
ld([vAC])                       #20
st([Y,X])                       #21
ld([sysArgs+0],X)               #22
ld(0x3f)                        #23
st([Y,X])                       #24
ld(hi('sysl-prog'),Y)           #25
jmp(Y,'NEXT')                   #26
ld(-28/2)                       #27

label('sysl-chk#11')
ld([sysArgs+4])                 #11 len>60?
adda(67)                        #12
anda(0x80)                      #13
st([vAC])                       #14
st([vAC+1])                     #15
ld([sysArgs+2])                 #16 writing echo area?
suba(0x20)                      #17
anda([sysArgs+2])               #18
anda(0x80,X)                    #19 X=0 [no] X=0x80 [maybe]
ld([sysArgs+3])                 #20
xora([sysArgs+1])               #21
ora([X])                        #22
beq('sysl-chk#25')              #23
ld(hi('sysl-prog'),Y)           #24
nop()                           #25
jmp(Y,'NEXT')                   #26
ld(-28/2)                       #27
label('sysl-chk#25')
st([sysArgs+0])                 #25
jmp(Y,'NEXT')                   #26
ld(-28/2)                       #27




#-----------------------------------------------------------------------
#
#   $1700 ROM page 23: vCPU Prefix35 page
#
#-----------------------------------------------------------------------

align(0x100, size=0x100)

label('PREFIX35_PAGE')

def oplabel(name):
  define(name, 0x3500 | (pc() & 0xff))

# Self-restart
label('p35restart#18')
nop()                           #18
nop()                           #19
nop()                           #20
ld(-2)                          #21
adda([vPC])                     #22
st([vPC])                       #23
ld(hi('NEXTY'),Y)               #24
jmp(Y,'NEXTY')                  #25
ld(-28/2)                       #26

# Jump into FSM14
label('fsm14op1#16')
st([fsmState])                  #16
ld([Y,X])                       #17
ld(hi('fsm14op1#21'),Y)         #18
jmp(Y,'fsm14op1#21')            #19
st([sysArgs+6])                 #20

# Instruction slots

fillers(until=0x3b)

# Instruction RDIVU (35 3b xx)
# - Divide [xx] by vAC
# - Trashes sysArgs[0..7]
oplabel('RDIVU_v7')
bra('fsm14op1#16')              #14
ld('rdivu#3a')                  #15

# Instruction MULW (35 3d xx)
# - Multiply vAC by var [xx]
# - Trashes sysArgs[0..7]
oplabel('MULW_v7')
bra('fsm14op1#16')              #14
ld('mulw#3a')                   #15

# Instruction BEQ (35 3f xx) [26 cycles]
# - Branch if zero (if(vACL==0)vPCL=xx)
assert (pc() & 255) == (symbol('EQ') & 255)
oplabel('BEQ')
nop()                           #14
nop()                           #15
ld([vAC+1])                     #16
label('beq#17')
ora([vAC])                      #17
beq('bccy#20')                  #18
ld(1)                           #19
label('bccn#20')
adda([vPC])                     #20
st([vPC])                       #21
ld(hi('NEXTY'),Y)               #22
jmp(Y,'NEXTY')                  #23
ld(-26//2)                      #24
nop()
label('bccn#18')
bra('bccn#20')                  #18
ld(1)                           #19

# Instruction BGT (35 4d xx) [26 cycles]
# - Branch if positive (if(vACL>0)vPCL=xx)
assert (pc() & 255) == (symbol('GT') & 255)
oplabel('BGT')
ld([vAC+1])                     #14
bpl('bne#17')                   #15
bmi('bccn#18')                  #16

# Instruction BLT (35 50 xx) [26 cycles]
# - Branch if negative (if(vACL<0)vPCL=xx)
assert (pc() & 255) == (symbol('LT') & 255)
oplabel('BLT')
ld([vAC+1])                     #14,17
bmi('bccy#17')                  #15
bpl('bccn#18')                  #16

# Instruction BGE (35 53 xx) [26 cycles]
# * Branch if positive or zero (if(vACL>=0)vPCL=xx)
assert (pc() & 255) == (symbol('GE') & 255)
oplabel('BGE')
ld([vAC+1])                     #14,17
bpl('bccy#17')                  #15
bmi('bccn#18')                  #16

# Instruction BLE (35 56 xx) [26 cycles]
# * Branch if negative or zero (if(vACL<=0)vPCL=xx)
assert (pc() & 255) == (symbol('LE') & 255)
oplabel('BLE')
ld([vAC+1])                     #14,17
bpl('beq#17')                   #15
nop()                           #16
label('bccy#17')
nop()                           #17
label('bccy#18')
bra('bccy#20')                  #18
ld([Y,X])                       #19

# Instruction RESET_v7.
# * Causes a soft reset. Called by 'vReset' only.
oplabel('RESET_v7')
ld(min(0,maxTicks-88//2))       #14 serious margin
adda([vTicks])                  #15
blt('p35restart#18')            #16
ld(hi('softReset#20'),Y)        #17
jmp(Y,'softReset#20')           #18
ld(0)                           #19

# Instruction DOKEI (35 62 ih il), 28 cycles
# * Store immediate word ihil at location [vAC]
# * Original idea from at67
oplabel('DOKEI_v7')
ld([Y,X])                       #14
st([Y,Xpp])                     #15
st([vTmp])                      #16 ih
ld([Y,X])                       #17 il
ld([vAC],X)                     #18
ld([vAC+1],Y)                   #19
st([Y,Xpp])                     #20
ld([vTmp])                      #21 ih
st([Y,X])                       #22
ld([vPC])                       #23
adda(2)                         #24
st([vPC])                       #25
ld(hi('NEXTY'),Y)               #26
jmp(Y,'NEXTY')                  #27
ld(-30//2)                      #28

nop()

# Instruction BNE (35 72 xx) [26 cycles]
# * Branch if not zero (if(vACL!=0)vPCL=xx)
assert (pc() & 255) == (symbol('NE') & 255)
oplabel('BNE')
nop()                           #14
nop()                           #15
ld([vAC+1])                     #16
label('bne#17')
ora([vAC])                      #17
beq('bccn#20')                  #18
ld(1)                           #19
label('bccy#20')
ld([Y,X])                       #20
st([vPC])                       #21
ld(hi('NEXTY'),Y)               #22
jmp(Y,'NEXTY')                  #23
ld(-26//2)                      #24

nop()

# Instruction NEGW (35 7e)
# * Negate vAC := -vAC
oplabel('NEGW')
ld([vAC])                       #14
xora(0xff)                      #15
adda(1)                         #16
st([vAC])                       #17
beq(pc()+3)                     #18
bra(pc()+3)                     #19
ld(0)                           #20
ld(0xff)                        #20!
adda([vAC+1])                   #21
xora(0xff)                      #22
st([vAC+1])                     #23
ld(hi('NEXTY'),Y)               #24
jmp(Y,'NEXTY')                  #25
ld(-28//2)                      #26





# Instruction slots

fillers(until=0xff)


#-----------------------------------------------------------------------
#
#   $1800 ROM page 24: vCPU op implementation (from page 3)
#
#-----------------------------------------------------------------------

align(0x100, size=0x100)


# POKEA implementation
label('pokea#13')
ld(AC,X)                        #13
ld([X])                         #14
ld([vAC],X)                     #15
ld([vAC+1],Y)                   #16
st([Y,Xpp])                     #17
ld(hi('NEXTY'),Y)               #18
jmp(Y,'NEXTY')                  #19
ld(-22//2)                      #20

# DOKEA implementation (tentative)
label('dokea#13')
st([vTmp])                      #13
adda(1,X)                       #14
ld([X])                         #15 hi
ld([vTmp],X)                    #16
st([vTmp])                      #17 vTmp=hi
ld([X])                         #19 lo
ld([vAC],X)                     #19
ld([vAC+1],Y)                   #20
st([Y,Xpp])                     #21
ld([vTmp])                      #22
st([Y,X])                       #23
ld(hi('NEXTY'),Y)               #24
jmp(Y,'NEXTY')                  #25
ld(-28//2)                      #26

# DEEKA implementation
label('deeka#13')
st([vTmp])                      #13
ld([vAC+1],Y)                   #14
ld([vAC])                       #15
adda(1,X)                       #16
ld([Y,X])                       #17 hi
st([vTmp0])                     #18
ld([vAC],X)                     #19
ld([Y,X])                       #20 lo
ld([vTmp],X)                    #21
ld(0,Y)                         #22
st([Y,Xpp])                     #23
ld([vTmp0])                     #24
st([Y,Xpp])                     #25
ld(hi('NEXTY'),Y)               #26
jmp(Y,'NEXTY')                  #27
ld(-30//2)                      #28

# POKEQ implementation
label('pokeq#13')
ld([vAC],X)                     #13
ld([vAC+1],Y)                   #14
st([Y,X])                       #15
ld(hi('NEXTY'),Y)               #16
jmp(Y,'NEXTY')                  #17
ld(-20//2)                      #18

# DOKEQ implementation
label('dokeq#13')
ld([vAC],X)                     #13
ld([vAC+1],Y)                   #14
st([Y,Xpp])                     #15
ld(0)                           #16
st([Y,X]);                      #18
ld(hi('NEXTY'),Y)               #19
jmp(Y,'NEXTY')                  #20
ld(-22//2)                      #21

# PEEKV implementation
label('peekv#13')
st([vTmp])                      #13
adda(1,X)                       #14
ld([X])                         #15
ld(AC,Y)                        #16
ld([vTmp],X)                    #17
ld([X])                         #18
ld(AC,X)                        #19
ld([Y,X])                       #20
st([vAC])                       #21
ld(0)                           #22
st([vAC+1])                     #23
ld(hi('NEXTY'),Y)               #24
jmp(Y,'NEXTY')                  #25
ld(-28/2)                       #26

# DEEKV implementation
label('deekv#13')
adda(1,X)                       #13
ld([X])                         #14
ld(AC,Y)                        #15
ld([vTmp],X)                    #16
ld([X])                         #17
ld(AC,X)                        #18
ld([Y,X])                       #19
st([Y,Xpp])                     #20
st([vAC])                       #21
ld([Y,X])                       #22
st([vAC+1])                     #23
ld(hi('NEXTY'),Y)               #24
jmp(Y,'NEXTY')                  #25
ld(-28/2)                       #26

# MOVQB implementation
label('movqb#13')
ld([vPC+1],Y)                   #13
st([vTmp])                      #14
st([Y,Xpp])                     #15
ld([Y,X])                       #16
ld(AC,X)                        #17
ld(0,Y)                         #18
ld([vTmp])                      #19
st([Y,X])                       #20
ld([vPC])                       #21
adda(1)                         #22
st([vPC])                       #23
ld(hi('NEXTY'),Y)               #24
jmp(Y,'NEXTY')                  #25
ld(-28/2)                       #26

# MOVQW implementation
label('movqw#13')
ld([vPC+1],Y)                   #13
st([vTmp])                      #14
st([Y,Xpp])                     #15
ld([Y,X])                       #16
ld(AC,X)                        #17
ld(0,Y)                         #18
ld([vTmp])                      #19
st([Y,Xpp])                     #20
ld(0)                           #21
st([Y,X])                       #22
ld([vPC])                       #23
adda(1)                         #24
st([vPC])                       #25
ld(hi('NEXTY'),Y)               #26
jmp(Y,'NEXTY')                  #27
ld(-30/2)                       #28

# DOKEI implementation
label('dokei#13')
st([Y,Xpp])                     #13
st([vTmp])                      #14 ih
ld([Y,X])                       #15 il
ld([vAC],X)                     #16
ld([vAC+1],Y)                   #17
st([Y,Xpp])                     #18
ld([vTmp])                      #19 ih
st([Y,X])                       #20
ld([vPC])                       #21
adda(1)                         #22
st([vPC])                       #23
ld(hi('NEXTY'),Y)               #24
jmp(Y,'NEXTY')                  #25
ld(-28//2)                      #26

# CMPWU implementation
label('cmpwu#13')
adda(1,X)                       #13
ld([vAC+1])                     #14 compare high bytes
xora([X])                       #15
beq('cmp#18')                   #16 equal -> check low byte
bgt('cmp#19')                   #17 same high bit -> subtract
ld([vAC+1])                     #18 otherwise:
xora(0x80)                      #19 vACH>=0x80>[X] if vACH[7]==1
ora(1)                          #20 vACH<0x80<=[X] if vACH[7]==0
label('cmp#21')
st([vAC+1])                     #21 return
ld(hi('NEXTY'),Y)               #22
jmp(Y,'NEXTY')                  #23
ld(-26/2)                       #24

label('cmp#19')
bra('cmp#21')                   #19 high bytes are different
suba([X])                       #20 but with same high bit

label('cmp#18')
ld([vTmp],X)                    #18 high bytes are equal.
label('cmpi#19')
ld([vAC])                       #19 same things with low bytes
xora([X])                       #20
bpl('cmp#23')                   #21
ld([vAC])                       #22
xora(0x80)                      #23
ora(1)                          #24
st([vAC+1])                     #25
ld(hi('NEXTY'),Y)               #26
jmp(Y,'NEXTY')                  #27
ld(-30/2)                       #28
label('cmp#23')
suba([X])                       #23
st([vAC])                       #24
st([vAC+1])                     #25
ld(hi('NEXTY'),Y)               #26
jmp(Y,'NEXTY')                  #27
ld(-30/2)                       #28

# CMPWS implementation
label('cmpws#13')
adda(1,X)                       #13
ld([vAC+1])                     #14 compare high bytes
xora([X])                       #15
beq('cmp#18')                   #16 equal -> check low byte
bgt('cmp#19')                   #17 same high bit -> subtract
ld([vAC+1])                     #18 otherwise:
bra('cmp#21')                   #19 vACH>=0>[X] if vACH[7]==0
ora(1)                          #20 vACH<0<=[X] if vACH[7]==1

# CMPIU implementation
label('cmpiu#13')
st([vTmp])                      #13
ld([vAC+1])                     #14
bne('cmpiu#17')                 #15 
ld(vTmp,X)                      #16 
bra('cmpi#19')                  #17 vACH=0: reuse
label('cmpiu#17')
ld(1)                           #17 vACH!=0:
st([vAC+1])                     #18
ld(hi('REENTER'),Y)             #19
jmp(Y,'REENTER')                #20
ld(-24/2)                       #21

# CMPIS implementation
label('cmpis#13')
st([vTmp])                      #13
ld([vAC+1])                     #14
bne('cmpis#17')                 #15 
ld(vTmp,X)                      #16 
bra('cmpi#19')                  #17 vACH=0: reuse
label('cmpis#17')
ld(hi('REENTER'),Y)             #17 vACH!=0:
jmp(Y,'REENTER')                #18
ld(-22/2)                       #19


# ADDV immplementation
label('addv#13')
ld(0,Y)                         #13
ld(AC,X)                        #14
ld([Y,X])                       #15
adda([vAC])                     #16
st([Y,Xpp])                     #17
bmi('addv#20')                  #18
suba([vAC])                     #19
ora([vAC])                      #20
bmi('addv#23c')                 #21
ld([Y,X])                       #22
label('addv#23')
bra('addv#25')                  #23
adda([vAC+1])                   #24
label('addv#20')
anda([vAC])                     #20
bpl('addv#23')                  #21
ld([Y,X])                       #22
label('addv#23c')
adda([vAC+1])                   #23
adda(1)                         #24
label('addv#25')
st([Y,X])                       #25
ld(hi('NEXTY'),Y)               #26
jmp(Y,'NEXTY')                  #27
ld(-30/2)                       #28

# SUBV implementation
label('subv#13')
ld(0,Y)                         #13
ld(AC,X)                        #14
ld([Y,X])                       #15
bmi('subv#18')                  #16
suba([vAC])                     #17
st([Y,Xpp])                     #18
ora([vAC])                      #19
bmi('subv#22c')                 #20
ld([Y,X])                       #21
label('subv#22')
nop()                           #22
bra('addv#25')                  #23
suba([vAC+1])                   #24
label('subv#18')
st([Y,Xpp])                     #18
anda([vAC])                     #19
bpl('subv#22')                  #20
ld([Y,X])                       #21
label('subv#22c')
suba([vAC+1])                   #22
bra('addv#25')                  #23
suba(1)                         #24



#-----------------------------------------------------------------------
#
#   $1900 ROM page 25: more vCPU ops
#
#-----------------------------------------------------------------------

align(0x100, size=0x100)

# ALLOC implementation
label('alloc#13')
adda([vSP])                     #13
st([vSP])                       #14
ld(hi('REENTER'),Y)             #15
jmp(Y,'REENTER')                #16
ld(-20/2)                       #17

# STLW implementation
label('stlw')
adda([vSP])                     #13
st([vTmp])                      #14
adda(1,X)                       #15
ld([vAC+1])                     #16
st([X])                         #17
ld([vTmp],X)                    #18
ld([vAC])                       #19
st([X])                         #20
ld(hi('REENTER'),Y)             #21
jmp(Y,'REENTER')                #22
ld(-26/2)                       #23

# LDLW implementation
label('ldlw')
adda([vSP])                     #13
st([vTmp])                      #14
adda(1,X)                       #15
ld([X])                         #16
st([vAC+1])                     #17
ld([vTmp],X)                    #18
ld([X])                         #19
st([vAC])                       #20
ld(hi('REENTER'),Y)             #21
jmp(Y,'REENTER')                #22
ld(-26/2)                       #23

# PUSH implementation
label('push#13')
ld([vSP])                       #13
suba(2)                         #14
st([vSP],X)                     #15
ld([vLR])                       #16
st([Y,Xpp])                     #17
ld([vLR+1])                     #18
st([Y,Xpp])                     #19
ld([vPC])                       #20
suba(1)                         #21
st([vPC])                       #22
ld(hi('REENTER'),Y)             #23
jmp(Y,'REENTER')                #24
ld(-28//2)                      #25

# POP implementation 
label('pop#13')
ld([X])                         #13
st([vLR])                       #14
ld([vSP])                       #15
adda(1,X)                       #16
adda(2)                         #17
st([vSP])                       #18
ld([X])                         #19
st([vLR+1])                     #20
ld([vPC])                       #21
suba(1)                         #22
st([vPC])                       #23
ld(hi('NEXTY'),Y)               #24
jmp(Y,'NEXTY')                  #25
ld(-28//2)                      #26

#-----------------------------------------------------------------------
# implementation of long and fast conditional branches
# Original idea from at67

# JNE implementation (24/26)
label('jne#13')
ld([vAC+1])                     #13
ora([vAC])                      #14
beq('jccn#17')                  #15
label('jccy#16')                # branch in 26 cycles
ld([vPC+1],Y)                   #16
label('jccy#17')                # branch in 26 cycles (with Y=PCH)
ld([Y,X])                       #17
st([Y,Xpp])                     #18
st([vPC])                       #19
ld([Y,X])                       #20
st([vPC+1])                     #21
ld(hi('NEXTY'),Y)               #22
jmp(Y,'NEXTY')                  #23
ld(-26/2)                       #24

# JEQ implementation (24/26)
label('jeq#13')
ld([vAC+1])                     #13
ora([vAC])                      #14
beq('jccy#17')                  #15
ld([vPC+1],Y)                   #16
label('jccn#17')                # pass in 24 cycles
ld(1)                           #17
label('jccn#18')                # pass in 24 cycles (with AC=1)
adda([vPC])                     #18
st([vPC])                       #19
ld(hi('NEXTY'),Y)               #20
jmp(Y,'NEXTY')                  #21
ld(-24/2)                       #22

# Jcc returns
label('jccy#15')                # branch 26 cycles
bra('jccy#17')                  #15
ld([vPC+1],Y)                   #16
label('jccn#15')                # pass 22 cycles
ld(1)                           #15
label('jccn#16')                # pass 22 cycles (with AC=1)
adda([vPC])                     #16
st([vPC])                       #17
ld(hi('NEXTY'),Y)               #18
jmp(Y,'NEXTY')                  #19
ld(-22/2)                       #20
label('jccn#20')                # pass 26 cycles (with AC=1)
adda([vPC])                     #20
st([vPC])                       #21
ld(hi('NEXTY'),Y)               #22
jmp(Y,'NEXTY')                  #23
ld(-26/2)                       #24

# JLT implementation (22/26) [with vACH in AC]
label('jlt#13')
bmi('jccy#15')                  #14
bpl('jccn#16')                  #14
ld(1)                           #15

# JGE implementation (22/26) [with vACH in AC]
label('jge#13')
bpl('jccy#15')                  #13
bmi('jccn#16')                  #14
ld(1)                           #15

# JGT implementation (24-26/26) [with vACH in AC]
label('jgt#13')
bmi('jccn#15')                  #13
ora([vAC])                      #14
bne('jccy#17')                  #15
ld([vPC+1],Y)                   #16
ld(1)                           #17
bra('jccn#20')                  #18
nop()                           #19

# JLE implementation (24-26/26) [with vACH in AC]
label('jle#13')
bmi('jccy#15')                  #13
ora([vAC])                      #14
beq('jccy#17')                  #15
ld([vPC+1],Y)                   #16
ld(1)                           #17
bra('jccn#20')                  #18
nop()                           #19





#-----------------------------------------------------------------------
#
#  End of Core
#
#-----------------------------------------------------------------------

align(0x100)

disableListing()

#-----------------------------------------------------------------------
#
#  Start of storage area
#
#-----------------------------------------------------------------------

# Export some zero page variables to GCL
# These constants were already loaded from interface.json.
# We're redefining them here to get a consistency check.
define('memSize',    memSize)
for i in range(3):
  define('entropy%d' % i, entropy+i)
define('videoY',     videoY)
define('frameCount', frameCount)
define('serialRaw',  serialRaw)
define('buttonState',buttonState)
define('xoutMask',   xoutMask)
define('vPC',        vPC)
define('vAC',        vAC)
define('vACH',       vAC+1)
define('vLR',        vLR)
define('vSP',        vSP)
define('vTmp',       vTmp)      # Not in interface.json
define('romType',    romType)
define('sysFn',      sysFn)
for i in range(8):
  define('sysArgs%d' % i, sysArgs+i)
define('soundTimer', soundTimer)
define('ledState_v2',ledState_v2)
define('ledTempo',   ledTempo)
define('userVars',   userVars)
define('userVars_v4',userVars_v4)
define('userVars_v5',userVars_v5)
define('userVars_v6',userVars_v6)
define('userVars_v7',userVars_v7)
define('videoTable', videoTable)
define('ledTimer',   ledTimer)
define('vIRQ_v5',    vIRQ_v5)
define('ctrlBits_v5',ctrlBits)
define('videoTop_v5',videoTop_v5)
define('userCode',   userCode)
define('soundTable', soundTable)
define('screenMemory',screenMemory)
define('vReset',     vReset)
define('wavA',       wavA)
define('wavX',       wavX)
define('keyL',       keyL)
define('keyH',       keyH)
define('oscL',       oscL)
define('oscH',       oscH)
define('maxTicks',   maxTicks)
define('v6502_PC',   v6502_PC)
define('v6502_PCL',  v6502_PCL)
define('v6502_PCH',  v6502_PCH)
define('v6502_A',    v6502_A)
define('v6502_X',    v6502_X)
define('v6502_Y',    v6502_Y)
define('qqVgaWidth', qqVgaWidth)
define('qqVgaHeight',qqVgaHeight)
define('buttonRight',buttonRight)
define('buttonLeft', buttonLeft)
define('buttonDown', buttonDown)
define('buttonUp',   buttonUp)
define('buttonStart',buttonStart)
define('buttonSelect',buttonSelect)
define('buttonB',    buttonB)
define('buttonA',    buttonA)

# XXX This is a hack (trampoline() is probably in the wrong module):
define('vPC+1',      vPC+1)

#-----------------------------------------------------------------------
#       Embedded programs -- import and convert programs and data
#-----------------------------------------------------------------------

def basicLine(address, number, text):
  """Helper to encode lines for TinyBASIC"""
  head = [] if number is None else [number&255, number>>8]
  body = [] if text is None else [ord(c) for c in text] + [0]
  s = head + body
  assert len(s) > 0
  for i, byte in enumerate([address>>8, address&255, len(s)]+s):
    comment = repr(chr(byte)) if i >= 3+len(head) else None
    program.putInRomTable(byte, comment=comment)

#-----------------------------------------------------------------------

lastRomFile = ''

def insertRomDir(name):
  global lastRomFile
  if name[0] != '_':                    # Mechanism for hiding files
    if pc()&255 >= 251-14:              # Prevent page crossing
      trampoline()
    s = lastRomFile[0:8].ljust(8,'\0')  # Cropping and padding
    if len(lastRomFile) == 0:
      lastRomFile = 0
    for i in range(8):
      st(ord(s[i]), [Y,Xpp])            #25-32
      C(repr(s[i]))
    ld(lo(lastRomFile))                 #33
    st([vAC])                           #34
    ld(hi(lastRomFile))                 #35
    ld(hi('.sysDir#39'),Y)              #36
    jmp(Y,'.sysDir#39')                 #37
    st([vAC+1])                         #38
    lastRomFile = name

#-----------------------------------------------------------------------
#       Embedded programs must be given on the command line
#-----------------------------------------------------------------------

if pc()&255 >= 251:                     # Don't start in a trampoline region
  align(0x100)

for application in argv[1:]:
  print()

  # Determine label
  if '=' in application:
    # Explicit label given as 'label=filename'
    name, application = application.split('=', 1)
  else:
    # Label derived from filename itself
    name = application.rsplit('.', 1)[0] # Remove extension
    name = name.rsplit('/', 1)[-1]       # Remove path
  print('Processing file %s label %s' % (application, name))

  C('+-----------------------------------+')
  C('| %-33s |' % application)
  C('+-----------------------------------+')

  # Pre-compiled GT1 files
  if application.endswith(('.gt1', '.gt1x')):
    print('Load type .gt1 at $%04x' % pc())
    with open(application, 'rb') as f:
      raw = bytearray(f.read())
    insertRomDir(name)
    label(name)
    if raw[0] == 0 and raw[1] + raw[2] > 0xc0:
      highlight('Warning: zero-page conflict with ROM loader (SYS_Exec_88)')
    program = gcl.Program(None)
    for byte in raw:
      program.putInRomTable(byte)
    program.end()

  # GCL files
  #----------------------------------------------------------------
  #  !!! GCL programs using *labels* "_L=xx" must be cautious !!!
  # Those labels end up in the same symbol table as the ROM build,
  # and name clashes cause havoc. It's safer to precompile such
  # applications into .gt1/.gt1x files. (This warning doesn't apply
  # to ordinary GCL variable names "xx A=".)
  #----------------------------------------------------------------
  elif application.endswith('.gcl'):
    print('Compile type .gcl at $%04x' % pc())
    insertRomDir(name)
    label(name)
    program = gcl.Program(name, romName=DISPLAYNAME)
    program.org(userCode)
    zpReset(userVars)
    for line in open(application).readlines():
      program.line(line)
    # finish
    program.end()            # 00
    program.putInRomTable(2) # exech
    program.putInRomTable(0) # execl

  # Application-specific SYS extensions
  elif application.endswith('.py'):
    print('Include type .py at $%04x' % pc())
    label(name)
    importlib.import_module(name)

  # GTB files
  elif application.endswith('.gtb'):
    print('Link type .gtb at $%04x' % pc())
    zpReset(userVars)
    label(name)
    program = gcl.Program(name)
    # BasicProgram comes from TinyBASIC.gcl
    address = symbol('BasicProgram')
    if not has(address):
      highlight('Error: TinyBASIC must be compiled-in first')
    program.org(address)
    i = 0
    for line in open(application):
      i += 1
      line = line.rstrip()[0:25]
      number, text = '', ''
      for c in line:
        if c.isdigit() and len(text) == 0:
          number += c
        else:
          text += c
      basicLine(address, int(number), text)
      address += 32
      if address & 255 == 0:
        address += 160
    basicLine(address+2, None, 'RUN')           # Startup command
    # Buffer comes from TinyBASIC.gcl
    basicLine(symbol('Buffer'), address, None)  # End of program
    program.putInRomTable(0)
    program.end()
    print(' Lines', i)

  # Simple sequential RGB file (for Racer horizon image)
  elif application.endswith('-256x16.rgb'):
    width, height = 256, 16
    print('Convert type .rgb/sequential at $%04x' % pc())
    f = open(application, 'rb')
    raw = bytearray(f.read())
    f.close()
    insertRomDir(name)
    label(name)
    packed, quartet = [], []
    for i in range(0, len(raw), 3):
      R, G, B = raw[i+0], raw[i+1], raw[i+2]
      quartet.append((R//85) + 4*(G//85) + 16*(B//85))
      if len(quartet) == 4:
        # Pack 4 pixels in 3 bytes
        packed.append( ((quartet[0]&0b111111)>>0) + ((quartet[1]&0b000011)<<6) )
        packed.append( ((quartet[1]&0b111100)>>2) + ((quartet[2]&0b001111)<<4) )
        packed.append( ((quartet[2]&0b110000)>>4) + ((quartet[3]&0b111111)<<2) )
        quartet = []
    for i in range(len(packed)):
      ld(packed[i])
      if pc()&255 == 251:
        trampoline()
    print(' Pixels %dx%d' % (width, height))

  # Random access RGB files (for Pictures application)
  elif application.endswith('-160x120.rgb'):
    if pc()&255 > 0:
      trampoline()
    print('Convert type .rgb/parallel at $%04x' % pc())
    f = open(application, 'rb')
    raw = f.read()
    f.close()
    label(name)
    for y in range(0, qqVgaHeight, 2):
      for j in range(2):
        comment = 'Pixels for %s line %s' % (name, y+j)
        for x in range(0, qqVgaWidth, 4):
          bytes = []
          for i in range(4):
            R = raw[3 * ((y + j) * qqVgaWidth + x + i) + 0]
            G = raw[3 * ((y + j) * qqVgaWidth + x + i) + 1]
            B = raw[3 * ((y + j) * qqVgaWidth + x + i) + 2]
            bytes.append( (R//85) + 4*(G//85) + 16*(B//85) )
          # Pack 4 pixels in 3 bytes
          ld( ((bytes[0]&0b111111)>>0) + ((bytes[1]&0b000011)<<6) ); comment = C(comment)
          ld( ((bytes[1]&0b111100)>>2) + ((bytes[2]&0b001111)<<4) )
          ld( ((bytes[2]&0b110000)>>4) + ((bytes[3]&0b111111)<<2) )
        if j==0:
          trampoline3a()
        else:
          trampoline3b()
    print(' Pixels %dx%d' % (width, height))

  # XXX Provisionally bring ROMv1 egg back as placeholder for Pictures
  elif application.endswith(('/gigatron.rgb', '/packedPictures.rgb')):
    print(('Convert type gigatron.rgb at $%04x' % pc()))
    f = open(application, 'rb')
    raw = bytearray(f.read())
    f.close()
    label(name)
    for i in range(len(raw)):
      if i&255 < 251:
        ld(raw[i])
      elif pc()&255 == 251:
        trampoline()

  else:
    assert False

  C('End of %s, size %d' % (application, pc() - symbol(name)))
  print(' Size %s' % (pc() - symbol(name)))

#-----------------------------------------------------------------------
# ROM directory
#-----------------------------------------------------------------------

# SYS_ReadRomDir implementation

if pc()&255 > 251 - 28:         # Prevent page crossing
  trampoline()
label('sys_ReadRomDir')
beq('.sysDir#20')               #18
ld(lo(sysArgs),X)               #19
ld(AC,Y)                        #20 Follow chain to next entry
ld([vAC])                       #21
suba(14)                        #22
jmp(Y,AC)                       #23
#ld(hi(sysArgs),Y)              #24 Overlap
#
label('.sysDir#20')
ld(hi(sysArgs),Y)               #20,24 Dummy
ld(lo('.sysDir#25'))            #21 Go to first entry in chain
ld(hi('.sysDir#25'),Y)          #22
jmp(Y,AC)                       #23
ld(hi(sysArgs),Y)               #24
label('.sysDir#25')
insertRomDir(lastRomFile)       #25-38 Start of chain
label('.sysDir#39')
ld(hi('REENTER'),Y)             #39 Return
jmp(Y,'REENTER')                #40
ld(-44/2)                       #41

print()

#-----------------------------------------------------------------------
# End of embedded applications
#-----------------------------------------------------------------------

if pc()&255 > 0:
  trampoline()

#-----------------------------------------------------------------------
# Finish assembly
#-----------------------------------------------------------------------
end()
writeRomFiles(ROMNAME or argv[0])
