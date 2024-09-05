dofile "data.lua"
dofile "utils.lua"
dofile "memory.lua"
dofile "retrieveData.lua"
dofile "decryptPokemon.lua"

console.clear()
console.log("\nShinybot started\n")

SKIP_ENCOUNTERS = true

local json = require "json"

-- Pokemon object
local position = {}
local pokemonTeam = {}
local wildPokemon = {}
local bag = {}

-- Diamond = D, Pearl = P, Platinum = PL
GAMECODE = retriveGameCode()

-- Calculate PID memory addresses needed for data processing
refreshPID()

-- Get wild Pokemon encrypted data from PID address to display PID
wildPokemon = decryptPokemonData(wildPidAddress)
console.log("Game : " .. GAMECODE)
console.log("baseAddress : 0x" .. getHexValue(baseAddress))
console.log("Ally PID address : 0x" .. getHexValue(allyPidAddress))
console.log("Ally PID : 0x" .. getHexValue(memory.read_u32_le(allyPidAddress)))
console.log("Wild PID address : 0x" .. getHexValue(wildPidAddress))
console.log("Wild PID : 0x" .. getHexValue(memory.read_u32_le(wildPidAddress)))

-- Clear previously used data, fill every byte with null values
comm.mmfWrite("joypad", string.rep("\x00", 20480))
comm.mmfWrite("pokemonTeamData", string.rep("\x00", 20480))
comm.mmfWrite("wildPokemonData", string.rep("\x00", 20480))
comm.mmfWrite("bagData", string.rep("\x00", 20480))
comm.mmfWrite("gameData", string.rep("\x00", 20480))
comm.mmfWrite("playerData", string.rep("\x00", 20480))
comm.mmfWrite("runSections", string.rep("\x00", 20480))
comm.mmfWrite("specialPokemon", string.rep("\x00", 20480))

-- Set screenshot memory file name
comm.mmfWrite("screenshot", string.rep("\x00", 64000))
comm.mmfSetFilename("screenshot")

while true do
    -- Save a screenshot in memory file every frame
    comm.mmfScreenshot()

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
        if (wildPidAddress > 0) then
            wildPokemon = decryptPokemonData(wildPidAddress) -- Get Pokemon encrypted data from PID address
        else
            wildPokemon = {pid = 0}
        end

        comm.mmfWrite("wildPokemonData", json.encode({["wildPokemonData"] = wildPokemon}) .. "\x00")

        -- Write Bag data in memory
        bag = retrieveBag()
        comm.mmfWrite("bagData", json.encode({["bagData"] = bag}) .. "\x00")
    end

    -- Set Repel steps to a fixed number to prevent it from decreasing
    if (SKIP_ENCOUNTERS) then
        memory.write_u8(baseAddress - 0x02000000 + MEMORYADDRESSES[GAMECODE]["REPELSTEPS_OFFSET"], 5, "Main RAM")
    end

    -- Save game data (current selection, repel steps remaining, etc) at every frame
    gameData = retrieveGameData()
    comm.mmfWrite("gameData", json.encode({["gameData"] = gameData}) .. "\x00")

    -- Save player data (position, orientation, bike speed, etc) at every frame
    playerData = retrievePlayerData()
    comm.mmfWrite("playerData", json.encode({["playerData"] = playerData}) .. "\x00")

    -- Check in memory if we need to override Swarm/Marsh/Garden Pokemon
    readSpecialPokemonFromMemory()

    -- Debug : display position on screen
    gui.text(0,0, string.format("(%d,%d) - (%d,%d), Zone : %d, Framecount : %d, PID : %x\nRepel steps : %d, Bike : %s (speed = %d)", playerData.positionX, playerData.positionY, playerData.positionY + 1, playerData.positionX + 1, playerData.zone, emu.framecount(), wildPokemon.pid, gameData.repelSteps, tostring(playerData.isOnBike), playerData.bikeSpeed))
    
    -- Input button retrieved from memory
    inputFromMemory()

    -- Next frame
    emu.frameadvance()
end