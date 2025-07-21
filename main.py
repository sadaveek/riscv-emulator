from emulator import emulator

emu = emulator()
emu.assemble("test.s")
print('Assembled')
emu.load_program("test.bin")
print('Loaded')
emu.run()
emu.debug()