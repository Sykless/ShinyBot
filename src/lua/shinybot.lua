dofile "data.lua"
dofile "utils.lua"
dofile "battle.lua"
dofile "memory.lua"
dofile "decryptPokemon.lua"

console.clear()
console.log("\nShinybot started\n")

PLATINUM_ADDRESS = 0x02101F0C
BUTTON_MAPPING = {
    ["A"] = {["A"] = "True"},
    ["B"] = {["B"] = "True"},
    ["X"] = {["X"] = "True"},
    ["Y"] = {["Y"] = "True"},
    ["L"] = {["L"] = "True"},
    ["R"] = {["R"] = "True"},
    ["d"] = {["Down"] = "True"},
    ["l"] = {["Left"] = "True"},
    ["u"] = {["Up"] = "True"},
    ["r"] = {["Right"] = "True"},
    ["s"] = {["Select"] = "True"},
    ["S"] = {["Start"] = "True"},
    ["@"] = {}
}

-- Pokemon object
local pokemon = {}

-- Calculate PID memory addresses needed for data processing
refreshPID()

console.log("pointer : 0x" .. getHexValue(pointer))
console.log("Ally PID address : 0x" .. getHexValue(allyPidAddress))
console.log("Ally PID : 0x" .. getHexValue(memory.read_u32_le(allyPidAddress)))
console.log("Opposing PID address : 0x" .. getHexValue(opposingPidAddress))
console.log("Opposing PID : 0x" .. getHexValue(memory.read_u32_le(opposingPidAddress)))

-- Fill memory files with null values to only retrieve our data when needed
comm.mmfWrite("joypad", string.rep("\x00", 4096))

-- Set screenshot memory file name
comm.mmfWrite("screenshot", string.rep("\x00", 30486))
comm.mmfSetFilename("screenshot")

while true do
    -- Save a screenshot in memory file every frame
    comm.mmfScreenshot()

    -- Check every second if a new wild Pokemon has been found
    if emu.framecount() % 60 == 0 then
        refreshPID()
        pokemon = decryptPokemonData(opposingPidAddress) -- Get Pokemon encrypted data from PID address
    end

    local mmfJoypad = comm.mmfRead("joypad", 4096)
    local joypadInput = string.match(mmfJoypad, "[^\x00]+") -- Get everything before the first null \x00 character

    if (joypadInput) then
        local buttonPress = string.sub(joypadInput,1,1)
        local remainingInputs = string.sub(joypadInput, 2, string.len(joypadInput))

        joypad.set(BUTTON_MAPPING[buttonPress])
    
        -- Erase first input with \x00 null character and shift the rest to the left
        comm.mmfWrite("joypad", remainingInputs .. "\x00")
    end

    -- Next frame
    emu.frameadvance()
end