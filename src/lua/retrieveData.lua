

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

SELECTEDBAGSECTION_ADDRESS = 0X022A69E4
SELECTEDBAGITEM_ADDRESS = 0x0227179C

function retrieveGameData()
    return {
        repelSteps = memory.readbyte(REPELSTEPS_ADDRESS),
        selectedBagSection = memory.readbyte(SELECTEDBAGSECTION_ADDRESS),
        selectedBagItemId = memory.readbyte(SELECTEDBAGITEM_ADDRESS)
    }
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

    return bagData
end

MAP_POINTER = 0x021C0974
BIKE_ADDRESS = 0x0227F740
BIKESPEED_ADDRESS = 0x0227F73C
REPELSTEPS_ADDRESS = 0x022864A3
ORIENTATION_ADDRESS = 0x022A1CC8
ORIENTATION = {"u","d","l","r"}

function retrievePlayerData()
    local zoneAddress = memory.read_u32_le(MAP_POINTER) + 0x1294
    local positionXAddress = zoneAddress + 8
    local positionYAddress = zoneAddress + 12

    local orientation = "d" -- Default orientation is down
    local orientationValue = memory.read_u16_le(ORIENTATION_ADDRESS)

    -- This is the only value we actually need to be sure of, since we're using it as an array id
    if (orientationValue >= 0 and orientationValue <= 3) then
        orientation = ORIENTATION[orientationValue + 1]
    end

    return {
        zone = memory.read_u16_le(zoneAddress),
        positionX = memory.read_u16_le(positionXAddress),
        positionY = memory.read_u16_le(positionYAddress),
        orientation = orientation,
        
        -- This memory address is actually used for multiple states, only state = 1 (isOnBike) is useful to us
        isOnBike = memory.read_u16_le(BIKE_ADDRESS) == 1,

        -- Add 3 to convert 0 -> 1 values to speed 3 and 4 (bike speeds used in the game)
        bikeSpeed = memory.read_u8(BIKESPEED_ADDRESS) + 3,
    }
end

-- opposingPidAddress may vary so we must refresh its value from time to time
function refreshPID()
    -- Pointer : Reference address
    pointer = memory.read_u32_le(PLATINUM_ADDRESS)
    baseAddress = pointer + 0xCFF4

    -- PID : Pokemon unique ID
    allyPidAddress = baseAddress + 0xA0
    opposingPidAddress = memory.read_u32_le(pointer + 0x352F4) + 0x7A0
end