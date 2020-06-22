std::vector<std::string> _defaultKeys =
{
    "                                                                                ",
    "; Keys are editable in 'input_config.ini'                                       ",
    "; If 'input_config.ini' is changed, then the emulator has to be restarted       ",
    "; Text cursor and editing is controlled via the mouse                           ",
    "; Left Mouse Button to compile/execute current file in Browser on Emulator      ",
    "; Right Mouse Button to compile/execute current file in Browser on Hardware     ",
    "                                                                                ",
    "[Emulator]               ; case sensitive                                       ",
    "MemoryMode   = CTRL+M    ; toggles between RAM, ROM0 and ROM1                   ",
    "MemorySize   = CTRL+Z    ; toggles between 32K RAM and 64K RAM                  ",
    "Browse       = CTRL+B    ; file browser                                         ",
    "RomType      = CTRL+R    ; ROM browser                                          ",
    "HexMonitor   = CTRL+X    ; hex monitor                                          ",
    "Disassembler = CTRL+D    ; disassembler, (vCPU or Native based on MemoryMode)   ",
    "Terminal     = CTRL+T    ; basic serial terminal for talking to hardware        ",
    "ImageEditor  = CTRL+I    ; basic image editor for editing graphic images        ",
    "AudioEditor  = CTRL+A    ; basic audio editor for editing sample waveforms      ",
    "ScanlineMode = CTRL+S    ; toggles scanline modes, Normal, VideoB and VideoBC   ",
    "Reset        = CTRL+F1   ; emulator reset                                       ",
    "Help         = CTRL+H    ; toggles help screen on and off                       ",
    "Quit         = CTRL+Q    ; instant quit                                         ",
    "                                                                                ",
    "[Keyboard]               ; case sensitive                                       ",
    "Mode         = CTRL+K    ; toggles between, Giga, PS2, HwGiga and HwPS2         ",
    "Left         = A         ; left input for emulator/hardware depending on Mode   ",
    "Right        = D         ; right input for emulator/hardware depending on Mode  ",
    "Up           = W         ; up input for emulator/hardware depending on Mode     ",
    "Down         = S         ; down input for emulator/hardware depending on Mode   ",
    "Start        = SPACE     ; start input for emulator/hardware depending on Mode  ",
    "Select       = Z         ; select input for emulator/hardware depending on Mode ",
    "A            = .         ; A input for emulator/hardware depending on Mode      ",
    "B            = /         ; B input for emulator/hardware depending on Mode      ",
    "                                                                                ",
    "[Hardware]               ; case sensitive                                       ",
    "Reset        = CTRL+F2   ; resets hardware                                      ",
    "                                                                                ",
    "[Debugger]               ; case sensitive                                       ",
    "Debug        = CTRL+F6   ; toggles debugging mode, can be used to pause         ",
    "RunToBrk     = CTRL+F7   ; run to breakpoint, does nada if no breakpoints exist ",
    "StepPC       = CTRL+F8   ; single steps debugger based on vPC or native PC      ",
    "StepWatch    = CTRL+F9   ; single steps debugger based on a watched variable    ",
    "                         ; by default is videoY which changes once per scanline ",
    "                                                                                "
};