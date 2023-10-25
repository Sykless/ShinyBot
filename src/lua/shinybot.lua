dofile "data.lua"
dofile "memory.lua"
dofile "decryptPokemon.lua"

console.clear()
console.log("\nShinybot started\n")

-- Pokemon object
pokemon = {}

-- Block order dependening on the shift value (0-23)
BlockA = {1,1,1,1,1,1,2,2,3,4,3,4,2,2,3,4,3,4,2,2,3,4,3,4}
BlockB = {2,2,3,4,3,4,1,1,1,1,1,1,3,4,2,2,4,3,3,4,2,2,4,3}
BlockC = {3,4,2,2,4,3,3,4,2,2,4,3,1,1,1,1,1,1,4,3,4,3,2,2}
BlockD = {4,3,4,3,2,2,4,3,4,3,2,2,4,3,4,3,2,2,1,1,1,1,1,1}

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
pidAddr = allyPidAddress

-- Retrieve PID and checksum from RAM
pid = memory.read_u32_le(pidAddr)
checksum = memory.read_u16_le(pidAddr + 6)

-- Calculate Shift value used for block shuffling - see decryptPokemon.lua
shiftValue = ((pid & 0x3E000) >> 0xD) % 24
console.log("shiftValue : " .. shiftValue .. " -> " 
    .. BlockA[shiftValue + 1]
    .. BlockB[shiftValue + 1]
    .. BlockC[shiftValue + 1]
    .. BlockD[shiftValue + 1]
    .. "\n"
)

-- Each block is shift by a certain offset, calculated with Block{A-B-C-D}
BlockAoffset = (BlockA[shiftValue + 1] - 1) * 32
BlockBoffset = (BlockB[shiftValue + 1] - 1) * 32
BlockCoffset = (BlockC[shiftValue + 1] - 1) * 32
BlockDoffset = (BlockD[shiftValue + 1] - 1) * 32

-- Each parameter must be decrypted using PRNG (pseudorandom number generator)
-- PRNG decryption covers two bytes at the time, so to get adjacent 1-byte values,
-- We need to retrieve the 2-byte block, and then split the two values
decryptBlockA()
decryptBlockB()
decryptBlockC()
decryptBlockD()

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