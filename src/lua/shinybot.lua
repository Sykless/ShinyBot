dofile "data.lua"
dofile "utils.lua"
dofile "memory.lua"
dofile "retrieveData.lua"
dofile "decryptPokemon.lua"

console.clear()
console.log("\nShinybot started\n")

PLATINUM_ADDRESS = 0x02101F0C

local json = require "json"

-- Pokemon object
local pokemon = {}
local bag = {}
local positionData = {}

-- Calculate PID memory addresses needed for data processing
refreshPID()

console.log("pointer : 0x" .. getHexValue(pointer))
console.log("Ally PID address : 0x" .. getHexValue(allyPidAddress))
console.log("Ally PID : 0x" .. getHexValue(memory.read_u32_le(allyPidAddress)))
console.log("Opposing PID address : 0x" .. getHexValue(opposingPidAddress))
console.log("Opposing PID : 0x" .. getHexValue(memory.read_u32_le(opposingPidAddress)))

-- Clear previously used data
comm.mmfWrite("joypad", string.rep("\x00", 4096))
comm.mmfWrite("pokemonData", string.rep("\x00", 4096))
comm.mmfWrite("bagData", string.rep("\x00", 4096))
comm.mmfWrite("positionData", string.rep("\x00", 4096))

-- Set screenshot memory file name
comm.mmfWrite("screenshot", string.rep("\x00", 30486))
comm.mmfSetFilename("screenshot")

while true do
    -- Save a screenshot in memory file every frame
    comm.mmfScreenshot()

    -- Save pokemon and bag data every second
    if emu.framecount() % 60 == 0 then
        refreshPID()
        
        -- Write Pokemon data in memory
        pokemon = decryptPokemonData(opposingPidAddress) -- Get Pokemon encrypted data from PID address
        comm.mmfWrite("pokemonData", json.encode({["pokemonData"] = pokemon}) .. "\x00")

        -- Write Bag data in memory
        bag = retrieveBag()
        comm.mmfWrite("bagData", json.encode({["bagData"] = bag}) .. "\x00")
    end

    -- Save player position every 5 frames
    if emu.framecount() % 5 == 0 then
        position = retrievePosition()
        comm.mmfWrite("positionData", json.encode({["positionData"] = position}) .. "\x00")
    end

    gui.text(0,0, string.format("X: %d, Y: %d", position.positionX, position.positionY))
    
    -- Input button retrieved from memory
    inputFromMemory()

    -- Next frame
    emu.frameadvance()
end