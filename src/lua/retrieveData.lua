

local BAG = {
    GENERAL_ITEMS = {ADDRESS = 0x630, NUMBER_OF_SLOTS = 165},
    KEY_ITEMS = {ADDRESS = 0x8C4, NUMBER_OF_SLOTS = 50},
    TMHM = {ADDRESS = 0x98C, NUMBER_OF_SLOTS = 100},
    MAIL = {ADDRESS = 0xB1C, NUMBER_OF_SLOTS = 12},
    MEDECINE = {ADDRESS = 0xB4C, NUMBER_OF_SLOTS = 40},
    BERRIES = {ADDRESS = 0xBEC, NUMBER_OF_SLOTS = 64},
    BALLS = {ADDRESS = 0xCEC, NUMBER_OF_SLOTS = 15},
    BATTLEITEMS = {ADDRESS = 0xD28, NUMBER_OF_SLOTS = 30}
}

-- Retrieve each bag section
function retrieveBag()
    local bagData = {
        generalItems = retrieveBagSection("GENERAL_ITEMS"),
        keyItems = retrieveBagSection("KEY_ITEMS"),
        TMHM = retrieveBagSection("TMHM"),
        mail = retrieveBagSection("MAIL"),
        medecine = retrieveBagSection("MEDECINE"),
        berries = retrieveBagSection("BERRIES"),
        balls = retrieveBagSection("BALLS"),
        battleItems = retrieveBagSection("BATTLEITEMS"),
    }

    return bagData
end

function retrieveBagSection(sectionId)
    local bagSection = {}

    for i = 0, BAG[sectionId].NUMBER_OF_SLOTS - 1 do
        local itemData = memory.read_u32_le(baseAddress + BAG[sectionId].ADDRESS + 4*i)

        if (itemData > 0) then
            local item = {}
            item["id"] = getBits(itemData,0,16)
            item["quantity"] = getBits(itemData,16,16)

            bagSection[i + 1] = item
        else
            break
        end
    end

    return bagSection
end

GAMEDATA_POINTER = 0x021C0974

ZONE_OFFSET = 0x1294
POSITIONX_OFFSET = 0x129C
POSITIONY_OFFSET = 0x12A0

BIKE_OFFSET = 0x1324
BIKESPEED_OFFSET = 0x1320
REPELSTEPS_OFFSET = 0x8087
ORIENTATION_OFFSET = 0x238A8
TIMEHOUR_ADDRESS = 0x021BF7C8

SELECTEDBAGSECTION_OFFSET = 0x285C8
SELECTEDBAGITEM_OFFSET = -0xCC80
MARSHPOKEMON_OFFSET = 0x7F24
SWARMPOKEMON_OFFSET = 0x7F28
GARDENPOKEMON_TODAY_OFFSET = 0x7F30
GARDENPOKEMON_YESTERDAY_OFFSET = 0x7F32
GBAGAME_ADDRESS = 0x021BF8C2

SKIP_ENCOUNTERTABLES = true
WALKENCOUNTERTABLE_OFFSET = 0x233D0
WATERENCOUNTERTABLE_OFFSET = WALKENCOUNTERTABLE_OFFSET + 0xCC

ORIENTATION = {"u","d","l","r"}

function retrievePlayerData()
    -- All memory addresses are stored in a single pointer, with different offsets for each
    local gameDataAddress = memory.read_u32_le(GAMEDATA_POINTER) 

    local orientationValue = memory.read_u16_le(gameDataAddress + ORIENTATION_OFFSET)
    local orientation = "d" -- Default orientation is down

    -- This is the only value we actually need to be sure of, since we're using it as an array id
    if (orientationValue >= 0 and orientationValue <= 3) then
        orientation = ORIENTATION[orientationValue + 1]
    end

    return {
        zone = memory.read_u16_le(gameDataAddress + ZONE_OFFSET),
        positionX = memory.read_u16_le(gameDataAddress + POSITIONX_OFFSET),
        positionY = memory.read_u16_le(gameDataAddress + POSITIONY_OFFSET),
        orientation = orientation,
        
        -- This memory address is actually used for multiple states, only state = 1 (isOnBike) is useful to us
        isOnBike = memory.read_u16_le(gameDataAddress + BIKE_OFFSET) == 1,

        -- Add 3 to convert 0 -> 1 values to speed 3 and 4 (bike speeds used in the game)
        bikeSpeed = memory.read_u8(gameDataAddress + BIKESPEED_OFFSET) + 3,
    }
end

function retrieveGameData()

    -- All memory addresses are stored in a single pointer, with different offsets for each
    local gameDataAddress = memory.read_u32_le(GAMEDATA_POINTER)

    local marshPokemonIds = memory.read_u32_le(baseAddress + MARSHPOKEMON_OFFSET)
    local marshPokemonList = {
        MARSHPOKEMON_LIST[getBits(marshPokemonIds,0,5)],  -- Zone 1
        MARSHPOKEMON_LIST[getBits(marshPokemonIds,5,5)],  -- Zone 2
        MARSHPOKEMON_LIST[getBits(marshPokemonIds,10,5)], -- Zone 3
        MARSHPOKEMON_LIST[getBits(marshPokemonIds,15,5)], -- Zone 4
        MARSHPOKEMON_LIST[getBits(marshPokemonIds,20,5)], -- Zone 5
        MARSHPOKEMON_LIST[getBits(marshPokemonIds,25,5)], -- Zone 6
    }

    local gardenPokemonYesterday = 0
    local gardenPokemonYesterdayId = memory.read_u16_le(baseAddress + GARDENPOKEMON_YESTERDAY_OFFSET)

    if (gardenPokemonYesterdayId ~= 0xFFFF) then
        gardenPokemonYesterday = GARDENPOKEMON_LIST[gardenPokemonYesterdayId]
    end

    return {
        hourOfDay = memory.read_u32_le(TIMEHOUR_ADDRESS),
        repelSteps = memory.readbyte(gameDataAddress + REPELSTEPS_OFFSET),
        selectedBagSection = memory.readbyte(gameDataAddress + SELECTEDBAGSECTION_OFFSET),
        selectedBagItemId = memory.readbyte(gameDataAddress + SELECTEDBAGITEM_OFFSET),
        swarmPokemon = SWARMPOKEMON_LIST[memory.read_u32_le(baseAddress + SWARMPOKEMON_OFFSET) % 22],
        marshPokemonList = marshPokemonList,
        gardenPokemonToday = GARDENPOKEMON_LIST[memory.read_u16_le(baseAddress + GARDENPOKEMON_TODAY_OFFSET)],
        gardenPokemonYesterday = gardenPokemonYesterday,
        gbaGame = memory.readbyte(GBAGAME_ADDRESS),
        encounterTables = SKIP_ENCOUNTERTABLES and {} or { -- Only retrieve encounter tables if needed
            walkEncounterTable = retrieveWalkEncounterTable(),
            waterEncounterTable = retrieveWaterEncounterTable()
        }
    }
end

-- Only needed once to generate encounter tables for each zone in Python code
function retrieveWalkEncounterTable()
    local encounterTableAddress = baseAddress + WALKENCOUNTERTABLE_OFFSET

    local walkEncountersTables = {}
    local walkEncountersIdentifier = memory.read_u32_le(encounterTableAddress)

    -- Retrieve every possible grass/cave encounters in the zone
    if (walkEncountersIdentifier > 0) then
        walkEncountersTables = {
            walkEncountersIdentifier = walkEncountersIdentifier,
            morningEncounters = {},
            dayEncounters = {},
            nightEncounters = {},
            swarmEncounters = {},
            pokeradarEncounters = {},
            gbaEncounters = {}
        }

        -- Retrieve all 12 possible default encounters in grass/cave
        for i = 0, 11 do
            table.insert(walkEncountersTables["morningEncounters"], {pokedexId = memory.read_u32_le(encounterTableAddress + 8*i + 8),
                                                                     level = memory.read_u32_le(encounterTableAddress + 8*i + 4)})
        end

        -- Replace encounters 3 and 4 (10% encounters) during the day
        table.insert(walkEncountersTables["dayEncounters"], memory.read_u32_le(encounterTableAddress + 108))
        table.insert(walkEncountersTables["dayEncounters"], memory.read_u32_le(encounterTableAddress + 112))

        -- Replace encounters 3 and 4 (10% encounters) during the night
        table.insert(walkEncountersTables["nightEncounters"], memory.read_u32_le(encounterTableAddress + 116))
        table.insert(walkEncountersTables["nightEncounters"], memory.read_u32_le(encounterTableAddress + 120))

        -- Replace encounters 1 and 2 (20% encounters) during a swarm
        table.insert(walkEncountersTables["swarmEncounters"], memory.read_u32_le(encounterTableAddress + 100))
        table.insert(walkEncountersTables["swarmEncounters"], memory.read_u32_le(encounterTableAddress + 104))

        -- Replace encounters 5, 6 (10% encounters), 11 and 12 (1% encounters) on a pokeradar rare grass patch
        table.insert(walkEncountersTables["pokeradarEncounters"], memory.read_u32_le(encounterTableAddress + 124))
        table.insert(walkEncountersTables["pokeradarEncounters"], memory.read_u32_le(encounterTableAddress + 128))
        table.insert(walkEncountersTables["pokeradarEncounters"], memory.read_u32_le(encounterTableAddress + 132))
        table.insert(walkEncountersTables["pokeradarEncounters"], memory.read_u32_le(encounterTableAddress + 136))

        -- Replace encounters 9 and 10 (4% encounters) if Sapphire is inserted in the GBA slot
        table.insert(walkEncountersTables["gbaEncounters"], {memory.read_u32_le(encounterTableAddress + 172),
                                                             memory.read_u32_le(encounterTableAddress + 176)})

        -- Replace encounters 9 and 10 (4% encounters) if Ruby is inserted in the GBA slot
        table.insert(walkEncountersTables["gbaEncounters"], {memory.read_u32_le(encounterTableAddress + 164),
                                                             memory.read_u32_le(encounterTableAddress + 168)})

        -- Replace encounters 9 and 10 (4% encounters) if Emerald is inserted in the GBA slot
        table.insert(walkEncountersTables["gbaEncounters"], {memory.read_u32_le(encounterTableAddress + 180),
                                                             memory.read_u32_le(encounterTableAddress + 184)})

        -- Replace encounters 9 and 10 (4% encounters) if Fire Red is inserted in the GBA slot
        table.insert(walkEncountersTables["gbaEncounters"], {memory.read_u32_le(encounterTableAddress + 188),
                                                             memory.read_u32_le(encounterTableAddress + 192)})

        -- Replace encounters 9 and 10 (4% encounters) if Leaf Green is inserted in the GBA slot
        table.insert(walkEncountersTables["gbaEncounters"], {memory.read_u32_le(encounterTableAddress + 196),
                                                             memory.read_u32_le(encounterTableAddress + 200)})
    end

    return walkEncountersTables
end

-- Only needed once to generate encounter tables for each zone in Python code
function retrieveWaterEncounterTable()
    local encounterTableAddress = baseAddress + WATERENCOUNTERTABLE_OFFSET

    local waterEncountersTables = {}
    local waterEncountersIdentifier = memory.read_u32_le(encounterTableAddress)

    -- Retrieve every possible surf/rod encounters in the zone
    if (waterEncountersIdentifier > 0) then
        waterEncountersTables = {
            surfEncounters = {},
            oldRodEncounters = {},
            goodRodEncounters = {},
            superRodEncounters = {}
        }

        -- Retrieve all 5 surf encounters
        for i = 0, 4 do
            table.insert(waterEncountersTables["surfEncounters"], {pokedexId = memory.read_u32_le(encounterTableAddress + 8*i + 8),
                                                                   minLevel = memory.read_u8(encounterTableAddress + 8*i + 5),
                                                                   maxLevel = memory.read_u8(encounterTableAddress + 8*i + 4)})
        end

        -- Retrieve all 5 old/good/super rod encounters
        for rodId, rodEncounters in ipairs({"oldRodEncounters", "goodRodEncounters", "superRodEncounters"}) do
            for i = 0, 4 do
                table.insert(waterEncountersTables[rodEncounters], {pokedexId = memory.read_u32_le(encounterTableAddress + 44 + 44*rodId + 8*i + 8),
                                                                    minLevel = memory.read_u8(encounterTableAddress + 44 + 44*rodId + 8*i + 5),
                                                                    maxLevel = memory.read_u8(encounterTableAddress + 44 + 44*rodId + 8*i + 4)})
            end
        end
    end

    return waterEncountersTables
end

-- opposingPidAddress may vary so we must refresh its value from time to time
function refreshPID()
    -- Pointer : Reference address
    pointer = memory.read_u32_le(PLATINUM_ADDRESS)
    baseAddress = pointer + 0xCFF4
    saveAddress = pointer + 0x11B598

    -- PID : Pokemon unique ID
    allyPidAddress = baseAddress + 0xA0
    opposingPidAddress = memory.read_u32_le(pointer + 0x352F4) + 0x7A0
end