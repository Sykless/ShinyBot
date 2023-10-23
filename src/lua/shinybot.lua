console.log("Shinyboy started.")

-- Addresses taken from https://github.com/yling/yPokeStats/tree/main

function readbyterange(address, bytes)
    -- bytes must be a multiple of 4
    if bytes % 4 ~= 0 then
        return 0
    end

    local text = ""
    local iterations = bytes / 4

    for i = 0, iterations - 1 do 
        data = memory.read_u32_be(address + 4*i)
        hexData = string.format("%x", data)

        for j = 1, 7, 2 do 
            intAsciiValue = tonumber(string.sub(hexData, j, j+1),16)

            if intAsciiValue ~= 0 then
                text = text .. string.char(intAsciiValue)
            else
                text = text .. " "
            end
        end
    end

    return text
end

gameNameAddress = 0x023FF000
gameLanguage = 0x023FFE0F

console.log(readbyterange(gameNameAddress,12))
console.log(readbyterange(gameLanguage,4))

runInCircles = false

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

while runInCircles do
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