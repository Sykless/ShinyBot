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
local position = {}
local pokemonTeam = {}
local wildPokemon = {}
local bag = {}

local flags = {
    runInput = false
}

-- Calculate PID memory addresses needed for data processing
refreshPID()

-- Get wild Pokemon encrypted data from PID address to display PID
wildPokemon = decryptPokemonData(opposingPidAddress)

console.log("pointer : 0x" .. getHexValue(pointer))
console.log("Ally PID address : 0x" .. getHexValue(allyPidAddress))
console.log("Ally PID : 0x" .. getHexValue(memory.read_u32_le(allyPidAddress)))
console.log("Opposing PID address : 0x" .. getHexValue(opposingPidAddress))
console.log("Opposing PID : 0x" .. getHexValue(memory.read_u32_le(opposingPidAddress)))

-- Clear previously used data, fill every byte with null values
comm.mmfWrite("joypad", string.rep("\x00", 20480))
comm.mmfWrite("pokemonTeamData", string.rep("\x00", 20480))
comm.mmfWrite("wildPokemonData", string.rep("\x00", 20480))
comm.mmfWrite("bagData", string.rep("\x00", 20480))
comm.mmfWrite("positionData", string.rep("\x00", 20480))
comm.mmfWrite("flagsData", "0" .. string.rep("\x00", 20480))

-- Set screenshot memory file name
comm.mmfWrite("screenshot", string.rep("\x00", 64000))
comm.mmfSetFilename("screenshot")

while true do
    -- Save a screenshot in memory file every frame
    comm.mmfScreenshot()

    flags = readFlagsFromMemory()

    -- Save pokemon and bag data every second
    if emu.framecount() % 60 == 0 then
        refreshPID()
        
        -- Write Pokemon team data in memory
        pokemonTeam = {}

        -- Decrypt each pokemon in team
        for i = 0, 5 do
            allyPokemon = decryptPokemonData(allyPidAddress + i*0xEC) -- Get Pokemon encrypted data from PID address
            table.insert(pokemonTeam, allyPokemon)
        end

        comm.mmfWrite("pokemonTeamData", json.encode({["pokemonTeamData"] = pokemonTeam}) .. "\x00")

        -- Write wild Pokemon data in memory
        wildPokemon = decryptPokemonData(opposingPidAddress) -- Get Pokemon encrypted data from PID address
        comm.mmfWrite("wildPokemonData", json.encode({["wildPokemonData"] = wildPokemon}) .. "\x00")

        -- Write Bag data in memory
        bag = retrieveBag()
        comm.mmfWrite("bagData", json.encode({["bagData"] = bag}) .. "\x00")
    end

    -- Save player position every frames
    position = retrievePosition()
    comm.mmfWrite("positionData", json.encode({["positionData"] = position}) .. "\x00")

    -- Debug : display position on screen
    gui.text(0,0, string.format("X: %d, Y: %d, Zone : %d, PID : %d", position.positionX, position.positionY, position.zone, wildPokemon.pid))
    
    -- Input button retrieved from memory
    inputFromMemory(flags.runInput)

    -- Next frame
    emu.frameadvance()
end