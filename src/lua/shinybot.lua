dofile "data.lua"
dofile "memory.lua"
dofile "decryptPokemon.lua"

console.clear()
console.log("\nShinybot started\n")

-- Pokemon object
pokemon = {}

platinumWrongAddress = 0x02101D2C
platinumAddress = 0x02101F0C

-- Pointer : Reference address
pointer = memory.read_u32_le(platinumAddress)
console.log("pointer : 0x" .. getHexValue(pointer))

-- PID : Pokemon unique ID
allyPidAddress = pointer + 0xD094 -- Ally
opposingPidAddress = memory.read_u32_le(pointer + 0x352F4) + 0x7A0 -- Opposing
console.log("Ally PID : 0x" .. getHexValue(memory.read_u32_le(allyPidAddress)))
console.log("Opposing PID : 0x" .. getHexValue(memory.read_u32_le(opposingPidAddress)))

-- Select the PID address to use
pidAddressToUse = allyPidAddress

-- Get Pokemon encrypted data from PID address
decryptPokemonData(pidAddressToUse)

-- Display Pokemon stats
console.log(pokemon)

-- runInCircles = true

-- upInput = {}
-- leftInput = {}
-- rightInput = {}
-- downInput = {}

-- upInput["Up"] = true
-- leftInput["Left"] = true
-- rightInput["Right"] = true
-- downInput["Down"] = true

-- NUM_OF_FRAMES_PER_PRESS = 5
-- RELEASE_TIME = 2 * NUM_OF_FRAMES_PER_PRESS
-- NUM_OF_POSITIONS = 4

-- MODULO = NUM_OF_POSITIONS * RELEASE_TIME

-- while runInCircles do
--     if emu.framecount() % MODULO == 0 then
--         -- console.log(memory.read_u8(pointer + 0xDE34))
--     elseif emu.framecount() % MODULO == MODULO * 0.75 then
--         --joypad.set(leftInput)
--     elseif emu.framecount() % MODULO == MODULO * 0.5 then
--         --joypad.set(downInput)
--     elseif emu.framecount() % MODULO == MODULO * 0.25 then
--         --joypad.set(rightInput)
--     end

--     emu.frameadvance()
-- end