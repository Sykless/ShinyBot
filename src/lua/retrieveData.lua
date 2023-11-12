

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
            item["name"] = ITEM_NAMES[getBits(itemData,0,16)]
            item["quantity"] = getBits(itemData,16,16)

            bagSection[i + 1] = item
        else
            break
        end
    end

    return bagSection
end

function retrieveBag()
    -- Retrieve each bag section
    local bagData = {
        generalItems = retrieveBagSection("GENERAL_ITEMS"),
        keyItems = retrieveBagSection("KEY_ITEMS"),
        TMHM = retrieveBagSection("TMHM"),
        mail = retrieveBagSection("MAIL"),
        medecine = retrieveBagSection("MEDECINE"),
        berries = retrieveBagSection("BERRIES"),
        balls = retrieveBagSection("BALLS"),
        battleItems = retrieveBagSection("BATTLEITEMS")
    }

    return bagData
end

MAP_POINTER = 0x021C0974

function retrievePosition()

    local mapAddress = memory.read_u32_le(MAP_POINTER) + 0x1294
    local positionXAddress = mapAddress + 8
    local positionYAddress = mapAddress + 12

    return {
        zone = memory.read_u16_le(mapAddress),
        positionX = memory.read_u16_le(positionXAddress),
        positionY = memory.read_u16_le(positionYAddress)
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