console.log("Shinyboy started.")

upInput = {}
leftInput = {}
rightInput = {}
downInput = {}

upInput["Up"] = true
leftInput["Left"] = true
rightInput["Right"] = true
downInput["Down"] = true

NUM_OF_FRAMES_PER_PRESS = 5
RELEASE_TIME = 2 * NUM_OF_FRAMES_PER_PRESS
NUM_OF_POSITIONS = 4

MODULO = NUM_OF_POSITIONS * RELEASE_TIME

while true do
    if emu.framecount() % MODULO == 0 then
        joypad.set(upInput)
    elseif emu.framecount() % MODULO == MODULO * 0.75 then
        joypad.set(leftInput)
    elseif emu.framecount() % MODULO == MODULO * 0.5 then
        joypad.set(downInput)
    elseif emu.framecount() % MODULO == MODULO * 0.25 then
        joypad.set(rightInput)
    end

    emu.frameadvance()
end