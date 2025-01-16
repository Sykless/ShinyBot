dofile "utils.lua"

BUTTON_MAPPING = {
    ["A"] = "A",
    ["B"] = "B",
    ["X"] = "X",
    ["Y"] = "Y",
    ["L"] = "L",
    ["R"] = "R",
    ["d"] = "Down",
    ["l"] = "Left",
    ["u"] = "Up",
    ["r"] = "Right",
    ["s"] = "Select",
    ["S"] = "Start",
    ["T"] = "Touch",
    ["@"] = "Nothing"
}

local runSections = {}
local runSectionId = -1
local processedInputs = 0

-- Check if baseAddress is valid and zone > 0
function isGameRunning()
    return (baseAddress > 0x02000000
            and baseAddress < 0x03000000
            and memory.read_u16_le(baseAddress + MEMORYADDRESSES[GAMECODE]["ZONE_OFFSET"]) > 0)
end

-- Check if we're in-game or before the title screen
function isOnTitleScreen()
    return (memory.read_u32_le(MEMORYADDRESSES[GAMECODE]["TITLESCREEN_ADDRESS"]) == 0
        and memory.read_u32_le(MEMORYADDRESSES[GAMECODE]["TITLESCREEN_ADDRESS"] + 4) == 0
        and memory.read_u32_le(MEMORYADDRESSES[GAMECODE]["TITLESCREEN_ADDRESS"] + 8) == 0
        and memory.read_u32_le(MEMORYADDRESSES[GAMECODE]["TITLESCREEN_ADDRESS"] + 12) == 0)
end

function readRunSectionsFromMemory()
    -- Read data from memory file sent by Python script
    local mmfRunSections = comm.mmfRead("runSections", 256)
    local runSectionsString = string.match(mmfRunSections, "[^\x00]+") -- Get everything before the first null \x00 character
    local runSectionsInt = {}

    if (runSectionsString) then
        local runSectionsSplit = splitString(runSectionsString, "/")

        -- Convert string sections to int arrays
        for id, substring in ipairs(runSectionsSplit) do
            local stringSection = splitString(substring, "-")
            table.insert(runSectionsInt, {["start"] = tonumber(stringSection[1]), ["end"] = tonumber(stringSection[2])})
        end

        -- Erase old memory values
        comm.mmfWrite("runSections", string.rep("\x00", 256))
    end

    return runSectionsInt
end

function inputFromMemory()
    -- Read data from memory file sent by Python script
    local mmfJoypad = comm.mmfRead("joypad", 8192)
    local joypadInput = string.match(mmfJoypad, "[^\x00]+") -- Get everything before the first null \x00 character

    if (joypadInput) then

        -- We just received new inputs, check if we also need to run
        if (runSectionId == -1) then
            runSections = readRunSectionsFromMemory()

            -- Set runSectionsId to 0 if we don't have to run at all
            if (next(runSections) == nil) then
                runSectionId = 0
            else
                runSectionId = 1
            end
        -- Increase the number of processed inputs
        else
            processedInputs = processedInputs + 1
        end

        -- Retrieve the first button of the sequence (only 1 input per frame)
        local joypadMap = {}
        local joypadAnalogMap = {}
        local inputLenght = 1
        local buttonPress = string.sub(joypadInput,1,1)

        -- If touchscreen is needed, retrieve 7 characters instead of 1 to get X,Y Touch coordinates
        if (buttonPress == "T") then
            inputLenght = 7
            joypadAnalogMap["Touch X"] = string.sub(joypadInput, 2, 4)
            joypadAnalogMap["Touch Y"] = string.sub(joypadInput, 5, 7)
        else
            client.clearautohold() -- Clear programmatically set Touch X/Y
        end
              
        local remainingInputs = string.sub(joypadInput, inputLenght + 1, string.len(joypadInput))

        -- Convert value retrieved from memory to actual button pressed
        joypadMap[BUTTON_MAPPING[buttonPress]] = "True"

        -- If run sections are present, check if we need to run
        if (runSectionId > 0 and runSectionId <= #runSections) then

            -- Go to next section when we go above it
            if (processedInputs > runSections[runSectionId]["end"]) then
                runSectionId = runSectionId + 1
            end

            -- Between start and end, press B to run
            if (runSectionId <= #runSections and processedInputs >= runSections[runSectionId]["start"] and processedInputs < runSections[runSectionId]["end"]) then
                joypadMap["B"] = "True"
            end
        end

        -- Apply generated joypad to emulator
        joypad.set(joypadMap)
        joypad.setanalog(joypadAnalogMap)

        -- Erase first input with \x00 null character and shift the rest to the left
        comm.mmfWrite("joypad", remainingInputs ..  string.rep("\x00", inputLenght))

    -- No more input to process, prepare to read runSections
    else
        runSectionId = -1
        processedInputs = 0
    end
end

function readSpecialPokemonFromMemory()
    -- Read data from memory file sent by Python script
    local mmfSpecialPokemon = comm.mmfRead("specialPokemon", 256)
    local specialPokemonString = string.match(mmfSpecialPokemon, "[^\x00]+") -- Get everything before the first null \x00 character
    local specialPokemonInt = {}

    if (specialPokemonString) then
        local specialPokemonSplit = splitString(specialPokemonString, "/")
        local gardenPokemonToday = -1
        local gardenPokemonYesterday = -1

        -- Convert string sections to Pokemon IDs
        for id, substring in ipairs(specialPokemonSplit) do
            local stringSection = splitString(substring, "-")

            -- Update Marsh/Swarm Pokemon and GBA game with provided IDs
            if (stringSection[1] == "MARSH") then
                updateMarshPokemon(tonumber(stringSection[2]))
            elseif (stringSection[1] == "SWARM") then
                updateSwarmPokemon(tonumber(stringSection[2]))
            elseif (stringSection[1] == "GBAGAME") then
                updateGBAGame(tonumber(stringSection[2]))
            elseif (stringSection[1] == "GARDENTODAY") then
                gardenPokemonToday = tonumber(stringSection[2])
            elseif (stringSection[1] == "GARDENYESTERDAY") then
                gardenPokemonYesterday = tonumber(stringSection[2])
            end
        end

        -- Update Garden Pokemon with provided IDs
        updateGardenPokemon(gardenPokemonToday, gardenPokemonYesterday)

        -- Erase old memory values
        comm.mmfWrite("specialPokemon", string.rep("\x00", 256))
    end
end

-- Simulate GBA game in GBA slot, makes certain Pokemon appear
function updateGBAGame(gameId)
    memory.write_u8(GBAGAME_ADDRESS - 0x02000000, gameId, "Main RAM")
end

function updateMarshPokemon(marshSectionId)

    -- Each marsh zone is coded on 5 bits, apply the same Pokémon ID for each
    zone1 = marshSectionId
    zone2 = (zone1 << 5) + marshSectionId
    zone3 = (zone2 << 5) + marshSectionId
    zone4 = (zone3 << 5) + marshSectionId
    zone5 = (zone4 << 5) + marshSectionId
    zone6 = (zone5 << 5) + marshSectionId

    -- Write new Pokémon marsh values in memory
    memory.write_u32_le(baseAddress - 0x02000000 + MARSHPOKEMON_OFFSET, zone6, "Main RAM")
end

function updateSwarmPokemon(swarmSectionId)
    memory.write_u32_le(baseAddress - 0x02000000 + SWARMPOKEMON_OFFSET, swarmSectionId, "Main RAM")
end

function updateGardenPokemon(gardenSectionIdToday, gardenSectionIdYesterday)

    -- If no garden Pokemon for today is provided, retrieve it in memory
    if (gardenSectionIdToday == -1) then
        gardenSectionIdToday = memory.read_u16_le(baseAddress + GARDENPOKEMON_TODAY_OFFSET)
    end

    -- Can"t have the same Pokémon today and yesterday
    if (gardenSectionIdToday == gardenSectionIdYesterday or gardenSectionIdYesterday == -1) then
        gardenSectionIdYesterday = 0xFFFF
    end

    -- Write new Pokémon swarm value in memory
    memory.write_u16_le(baseAddress - 0x02000000 + GARDENPOKEMON_TODAY_OFFSET, gardenSectionIdToday, "Main RAM")
    memory.write_u16_le(baseAddress - 0x02000000 + GARDENPOKEMON_YESTERDAY_OFFSET, gardenSectionIdYesterday, "Main RAM")
end

-- 32 bits multiplication, see http://www.sunshine2k.de/coding/c/mul32x32.html
function multiply32(a,b)
    local upper16BitsA = (a >> 16) & 0xFFFF
    local lower16BitsA = a % 0x10000

    local upper16BitsB = (b >> 16) & 0xFFFF
    local lower16BitsB = b % 0x10000

    local multiplyUpperUpper = (upper16BitsA * upper16BitsB) << 32
    local multiplyUpperLower = (upper16BitsA << 16) * lower16BitsB
    local multiplyLowerUpper = (upper16BitsB << 16) * lower16BitsA
    local multiplyLowerLower = lower16BitsA * lower16BitsB

    return multiplyUpperUpper + multiplyUpperLower + multiplyLowerUpper + multiplyLowerLower
end

-- Decryption is performed using this formula : data = encrypted xor (PNRG >> 16)
function decryptData(address)
    nextRecursivePrng() -- Update PRNG before each decryption
    encryptedData = memory.read_u16_le(address) -- Retrieve encrypted data from RAM
    decryptedData = encryptedData ~ (prng >> 16) -- Decrypt data using above formula

    return decryptedData
end

function getBits(a,b,d)
	return (a >> b) % (1 << d)
end

