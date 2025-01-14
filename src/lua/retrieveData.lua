

MEMORYADDRESSES = {
    D = {
        BASE_ADDRESS = 0x021CCEBC,
        BASE_OFFSET = 0xD26C,
        TITLESCREEN_ADDRESS = 0x02125000,
        PARTYPOKEMON_OFFSET = 0x98,
        WILDPOKEMONADDRESS_OFFSET = 0x2ABCC,
        WILDPOKEMON_OFFSET = -0x11A8,
        ZONE_OFFSET = 0x1238,
        POSITIONX_OFFSET = 0x1240,
        POSITIONY_OFFSET = 0x1244,
        FOGTYPE_OFFSET = 0x129E,
        HONEYTREES_OFFSET = 0x72DC,
        CYCLINGROAD_OFFSET = 0xFDC,
        REPELSTEPS_OFFSET = 0x73E0,
        BIKE_OFFSET = 0x12C8,
        BIKESPEED_OFFSET = 0x12C4,
        ORIENTATION_OFFSET = 0x2484C,
        REGISTEREDKEYITEM_OFFSET = 0xD94,
        FEEBASSEED_OFFSET = 0x539C,
        WALKENCOUNTERTABLE_OFFSET = 0x243AC,
        TIMEHOUR_ADDRESS = 0x021C49A8,
        SELECTEDBAGSECTION_OFFSET = 0x29568,
        SELECTEDBAGITEM_OFFSET = -0xCEB4
    },
    PL = {
        BASE_ADDRESS = 0x02101F0C,
        BASE_OFFSET = 0xCFF4,
        TITLESCREEN_ADDRESS = 0x0211F000,
        PARTYPOKEMON_OFFSET = 0xA0,
        WILDPOKEMONADDRESS_OFFSET = 0x28300,
        WILDPOKEMON_OFFSET = 0x7A0,
        ZONE_OFFSET = 0x1280,
        POSITIONX_OFFSET = 0x1288,
        POSITIONY_OFFSET = 0x128C,
        FOGTYPE_OFFSET = 0x12E6,
        HONEYTREES_OFFSET = 0x7F30,
        CYCLINGROAD_OFFSET = 0xFEC,
        REPELSTEPS_OFFSET = 0x8073,
        BIKE_OFFSET = 0x1310,
        BIKESPEED_OFFSET = 0x130C,
        ORIENTATION_OFFSET = 0x23894,
        REGISTEREDKEYITEM_OFFSET = 0xDA0,
        FEEBASSEED_OFFSET = 0x5664,
        WALKENCOUNTERTABLE_OFFSET = 0x233D0,
        TIMEHOUR_ADDRESS = 0x021BF7C8,
        SELECTEDBAGSECTION_OFFSET = 0x285B4,
        SELECTEDBAGITEM_OFFSET = -0xCC94
    }
}

-- Same memory addresses for Pokémon Diamond and Pearl
MEMORYADDRESSES["P"] = MEMORYADDRESSES["D"]

GAMECODE_ADDRESS = 0x023FFE08
GBAGAME_ADDRESS = 0x021BF8C2

MARSHPOKEMON_OFFSET = 0x7F24
SWARMPOKEMON_OFFSET = 0x7F28
GARDENPOKEMON_TODAY_OFFSET = 0x7F30
GARDENPOKEMON_YESTERDAY_OFFSET = 0x7F32

SKIP_ENCOUNTERTABLES = true

CYCLINGROAD_ZONEID = 350
ORIENTATION = {"u","d","l","r"}

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

function retriveGameCode()
    local firstLetter = memory.read_u8(GAMECODE_ADDRESS)
    local secondLetter = memory.read_u8(GAMECODE_ADDRESS + 1)

    if secondLetter == 0 then
        return string.char(firstLetter)
    else
        return string.char(firstLetter) .. string.char(secondLetter)
    end
end

function refreshPID()
    -- Pointer : Reference address
    baseAddress = memory.read_u32_le(MEMORYADDRESSES[GAMECODE]["BASE_ADDRESS"]) + MEMORYADDRESSES[GAMECODE]["BASE_OFFSET"]

    -- PID : Pokemon unique ID
    allyPidAddress = baseAddress + MEMORYADDRESSES[GAMECODE]["PARTYPOKEMON_OFFSET"]
    wildPidAddress = memory.read_u32_le(baseAddress + MEMORYADDRESSES[GAMECODE]["WILDPOKEMONADDRESS_OFFSET"])

    -- Only set wildPidAddress if the retrieved value is an actual address
    if (wildPidAddress > 0x02000000 and wildPidAddress < 0x03000000) then
        wildPidAddress = wildPidAddress + MEMORYADDRESSES[GAMECODE]["WILDPOKEMON_OFFSET"]
    else
        wildPidAddress = 0
    end
end

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
    --0x64793839
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

function retrievePlayerData()
    local orientationValue = memory.read_u16_le(baseAddress + MEMORYADDRESSES[GAMECODE]["ORIENTATION_OFFSET"])
    local orientation = "d" -- Default orientation is down

    -- This is the only value we actually need to be sure of, since we're using it as an array id
    if (orientationValue >= 0 and orientationValue <= 3) then
        orientation = ORIENTATION[orientationValue + 1]
    end

    zoneId = memory.read_u16_le(baseAddress + MEMORYADDRESSES[GAMECODE]["ZONE_OFFSET"])

    -- Particular case on Cycling Road sharing the same ZoneId as Route 206
    if (zoneId == CYCLINGROAD_ZONEID) then

        -- I am not exactly sure what this value actually refers to, I only noticed that it was equal to 8 on Cycling Road and 0 anywhere else
        cyclingRoad = memory.read_u16_le(baseAddress + MEMORYADDRESSES[GAMECODE]["CYCLINGROAD_OFFSET"])

        if (cyclingRoad > 0) then
            zoneId = zoneId + 1000
        end
    end

    return {
        zone = zoneId,
        positionX = memory.read_u16_le(baseAddress + MEMORYADDRESSES[GAMECODE]["POSITIONX_OFFSET"]),
        positionY = memory.read_u16_le(baseAddress + MEMORYADDRESSES[GAMECODE]["POSITIONY_OFFSET"]),
        orientation = orientation,

        -- This memory address is actually used for multiple states, only state = 1 (isOnBike) is useful to us
        isOnBike = memory.read_u16_le(baseAddress + MEMORYADDRESSES[GAMECODE]["BIKE_OFFSET"]) == 1,

        -- Add 3 to convert 0 -> 1 values to speed 3 and 4 (bike speeds used in the game)
        bikeSpeed = memory.read_u8(baseAddress + MEMORYADDRESSES[GAMECODE]["BIKESPEED_OFFSET"]) + 3,
    }
end

function retrieveGameData()

    local marshPokemonIds = memory.read_u32_le(baseAddress + MARSHPOKEMON_OFFSET)
    local marshPokemonList = {
        getBits(marshPokemonIds,0,5),  -- Zone 1
        getBits(marshPokemonIds,5,5),  -- Zone 2
        getBits(marshPokemonIds,10,5), -- Zone 3
        getBits(marshPokemonIds,15,5), -- Zone 4
        getBits(marshPokemonIds,20,5), -- Zone 5
        getBits(marshPokemonIds,25,5), -- Zone 6
    }

    local honeyTreesCountdown = {}
    local honeyAddress = baseAddress + MEMORYADDRESSES[GAMECODE]["HONEYTREES_OFFSET"]

    for i = 1, 21 do
        honeyTreesCountdown[i] = memory.read_u32_le(honeyAddress + 8 * i)
    end

    return {
        hourOfDay = memory.read_u32_le(MEMORYADDRESSES[GAMECODE]["TIMEHOUR_ADDRESS"]),
        repelSteps = memory.readbyte(baseAddress + MEMORYADDRESSES[GAMECODE]["REPELSTEPS_OFFSET"]),

        selectedBagSection = memory.readbyte(baseAddress + MEMORYADDRESSES[GAMECODE]["SELECTEDBAGSECTION_OFFSET"]),
        selectedBagItemId = memory.readbyte(baseAddress + MEMORYADDRESSES[GAMECODE]["SELECTEDBAGITEM_OFFSET"]),
        registeredKeyItem = memory.read_u32_le(baseAddress + MEMORYADDRESSES[GAMECODE]["REGISTEREDKEYITEM_OFFSET"]),

        isFoggy = memory.readbyte(baseAddress + MEMORYADDRESSES[GAMECODE]["FOGTYPE_OFFSET"]) == 14,
        feebasSeed = memory.read_u32_le(baseAddress + MEMORYADDRESSES[GAMECODE]["FEEBASSEED_OFFSET"]),
        honeyTreesCountdown = honeyTreesCountdown,
        swarmPokemon = memory.read_u32_le(baseAddress + SWARMPOKEMON_OFFSET) % 22,
        marshPokemonList = marshPokemonList,
        gardenPokemonToday = memory.read_u16_le(baseAddress + GARDENPOKEMON_TODAY_OFFSET),
        gardenPokemonYesterday = memory.read_u16_le(baseAddress + GARDENPOKEMON_YESTERDAY_OFFSET),
        gbaGame = memory.readbyte(GBAGAME_ADDRESS),
        encounterTables = SKIP_ENCOUNTERTABLES and {} or { -- Only retrieve encounter tables if needed
            walkEncounterTable = retrieveWalkEncounterTable(),
            waterEncounterTable = retrieveWaterEncounterTable()
        }
    }
end

-- Only needed once to generate encounter tables for each zone in Python code
function retrieveWalkEncounterTable()
    local encounterTableAddress = baseAddress + MEMORYADDRESSES[GAMECODE]["WALKENCOUNTERTABLE_OFFSET"]

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
    local encounterTableAddress = baseAddress + MEMORYADDRESSES[GAMECODE]["WALKENCOUNTERTABLE_OFFSET"] + 0xCC

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