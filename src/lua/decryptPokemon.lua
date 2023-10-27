-- Decryption algorithm :
-- • https://projectpokemon.org/docs/gen-4/pkm-structure-r65/
-- • https://bulbapedia.bulbagarden.net/wiki/Pok%C3%A9mon_data_structure_(Generation_IV)

-- Analysed these to better understand the algorithm :
-- • https://github.com/dude22072/PokeStats/tree/master
-- • https://github.com/yling/yPokeStats/tree/main
-- • https://github.com/kwsch/PKHeX/tree/master
-- • https://tasvideos.org/UserFiles/Info/45747701013813013 by FractalFusion

-- Block order dependening on the shift value (0-23)
BLOCK_A = {1,1,1,1,1,1,2,2,3,4,3,4,2,2,3,4,3,4,2,2,3,4,3,4}
BLOCK_B = {2,2,3,4,3,4,1,1,1,1,1,1,3,4,2,2,4,3,3,4,2,2,4,3}
BLOCK_C = {3,4,2,2,4,3,3,4,2,2,4,3,1,1,1,1,1,1,4,3,4,3,2,2}
BLOCK_D = {4,3,4,3,2,2,4,3,4,3,2,2,4,3,4,3,2,2,1,1,1,1,1,1}

-- Address of the first memory address in the Pokemon parameters
START = 0x08

function decryptPokemonData(selectedPidAddress)

    -- Pokemon object to store decrypted data
    local pokemonData = {}

    -- Retrieve PID and checksum from RAM
    local pid = memory.read_u32_le(selectedPidAddress)
    local checksum = memory.read_u16_le(selectedPidAddress + 0x06)

    -- Calculate Shift value used for block shuffling
    local shiftValue = ((pid & 0x3E000) >> 0xD) % 24

    -- Each parameter must be decrypted using PRNG (pseudorandom number generator)
    -- PRNG decryption covers two bytes at the time, so to get adjacent 1-byte values,
    -- We need to retrieve the 2-byte block, and then split the two values
    decryptBlockA(pokemonData, selectedPidAddress, shiftValue, checksum)
    decryptBlockB(pokemonData, selectedPidAddress, shiftValue, checksum)
    decryptBlockC(pokemonData, selectedPidAddress, shiftValue, checksum)
    decryptBlockD(pokemonData, selectedPidAddress, shiftValue, checksum)
    decryptStats(pokemonData, selectedPidAddress, shiftValue, pid)

    return pokemonData
end

function decryptBlockA(pokemonData, pidAddress, shiftValue, checksum)
    -- Seed PRNG with checksum
    prng = checksum

    -- Each block is shifted by a certain offset, calculated with BLOCK_{A-B-C-D}
    local BlockAoffset = (BLOCK_A[shiftValue + 1] - 1) * 32

    -- Skip the 32 bytes of the unwanted blocks to start at Block A
    -- Each PRNG next recursive value skips 2 bytes
    for i = 1, BLOCK_A[shiftValue + 1] - 1 do
        for j = 1, 16 do nextRecursivePrng() end
    end

    -- National Pokédex ID (START-0x09)
    pokemonData["PokedexID"] = decryptData(pidAddress + BlockAoffset + START)
    pokemonData[" Name "] = POKEMON_NAMES[pokemonData["PokedexID"]]

    -- Held Item (0x0A-0x0B)
    pokemonData["HeldItem"] = decryptData(pidAddress + BlockAoffset + START + 2)

    -- OT ID (0x0C-0x0D)
    pokemonData["OT"] = decryptData(pidAddress + BlockAoffset + START + 4)

    -- OT Secret ID (0x0E-0x0F)
    pokemonData["OTSecretID"] = decryptData(pidAddress + BlockAoffset + START + 6)

    -- Experience points (0x10-0x13)
    pokemonData["Experience"] = decryptData(pidAddress + BlockAoffset + START + 8)

    -- Remaining two bytes from Experience points (0x12-0x13)
    -- Should I retrieve the last 2 bytes of Experience ?
    -- console.log("Missing experience : " .. (decryptData(pidAddress + BlockAoffset + START + 10)))
    nextRecursivePrng()  -- Still need to update PRNG if we miss data

    -- Friendship/Steps to Hatch - Ability (0x14-0x15)
    local friendship_ability = decryptData(pidAddress + BlockAoffset + START + 12)
    pokemonData["Friendship"] = getBits(friendship_ability, 0, 8)
    pokemonData["Ability"] = ABILITY_LIST[getBits(friendship_ability, 8, 8)]

    -- Markings - Original Language (0x16-0x17)
    local markings_originalLanguage = decryptData(pidAddress + BlockAoffset + START + 14)
    pokemonData["Markings"] = getBits(markings_originalLanguage, 0, 8)
    pokemonData["OriginalLanguage"] = LANGUAGE_LIST[getBits(markings_originalLanguage, 8, 8)]

    -- HP Effort Value - Attack Effort Value (0x18-0x19)
    local HpEv_AtkEv = decryptData(pidAddress + BlockAoffset + START + 16)
    pokemonData["EV-HP"] = getBits(HpEv_AtkEv, 0, 8)
    pokemonData["EV-ATQ"] = getBits(HpEv_AtkEv, 8, 8)

    -- Defense Effort Value - Speed Effort Value (0x1A-0x1B)
    local DefEv_SpeEv = decryptData(pidAddress + BlockAoffset + START + 18)
    pokemonData["EV-DEF"] = getBits(DefEv_SpeEv, 0, 8)
    pokemonData["EV-SPE"] = getBits(DefEv_SpeEv, 8, 8)

    -- SP Attack Effort Value - SP Defense Effort Value (0x1C-0x1D)
    SpaEv_SpdEv = decryptData(pidAddress + BlockAoffset + START + 20)
    pokemonData["EV-SPA"] = getBits(SpaEv_SpdEv, 0, 8)
    pokemonData["EV-SPD"] = getBits(SpaEv_SpdEv, 8, 8)

    -- Cool/Beauty Contest Value (0x1E-0x1F)
    coolBeautyContest = decryptData(pidAddress + BlockAoffset + START + 22)
    pokemonData["ContestCool"] = getBits(coolBeautyContest, 0, 8)
    pokemonData["ContestBeauty"] = getBits(coolBeautyContest, 8, 8)

    -- Cute/Smart Contest Value (0x20-0x21)
    local cuteSmartContest = decryptData(pidAddress + BlockAoffset + START + 24)
    pokemonData["ContestCute"] = getBits(cuteSmartContest, 0, 8)
    pokemonData["ContestSmart"] = getBits(cuteSmartContest, 8, 8)

    -- Tough/Sheen Contest Value (0x22-0x23)
    local toughSheenContest = decryptData(pidAddress + BlockAoffset + START + 26)
    pokemonData["ContestTouch"] = getBits(toughSheenContest, 0, 8)
    pokemonData["ContestSheen"] = getBits(toughSheenContest, 8, 8)

    -- Sinnoh Ribbon Set 1 (0x24-0x25)
    pokemonData["SinnohRibbon3"] = decryptData(pidAddress + BlockAoffset + START + 28)

    -- Sinnoh Ribbon Set 2 (0x26-0x27)
    pokemonData["SinnohRibbon4"] = decryptData(pidAddress + BlockAoffset + START + 30)
end

function decryptBlockB(pokemonData, pidAddress, shiftValue, checksum)
    -- Seed PRNG with checksum
    prng = checksum

    -- Each block is shifted by a certain offset, calculated with BLOCK_{A-B-C-D}
    local BlockBoffset = (BLOCK_B[shiftValue + 1] - 1) * 32

    -- Skip the 32 bytes of the unwanted blocks to start at Block B
    -- Each PRNG next recursive value skips 2 bytes
    for i = 1, BLOCK_B[shiftValue + 1] - 1 do
        for j = 1, 16 do nextRecursivePrng() end
    end

    -- Move 1 ID (0x28-0x29)
    pokemonData["Move1"] = MOVE_NAMES[decryptData(pidAddress + BlockBoffset + START)]

    -- Move 2 ID (0x2A-0x2B)
    pokemonData["Move2"] = MOVE_NAMES[decryptData(pidAddress + BlockBoffset + START + 2)]

    -- Move 3 ID (0x2C-0x2D)
    pokemonData["Move3"] = MOVE_NAMES[decryptData(pidAddress + BlockBoffset + START + 4)]

    -- Move 4 ID (0x2E-0x2F)
    pokemonData["Move4"] = MOVE_NAMES[decryptData(pidAddress + BlockBoffset + START + 6)]

    -- Move 1-2 Current PP (0x30-0x31)
    local move12pp = decryptData(pidAddress + BlockBoffset + START + 8)
    pokemonData["Move1PP"] = getBits(move12pp, 0, 8)
    pokemonData["Move2PP"] = getBits(move12pp, 8, 8)

    -- Move 3-4 Current PP (0x32-0x33)
    local move34pp = decryptData(pidAddress + BlockBoffset + START + 10)
    pokemonData["Move3PP"] = getBits(move34pp, 0, 8)
    pokemonData["Move4PP"] = getBits(move34pp, 8, 8)

    -- Move PP Ups (0x34-0x37)
    pokemonData["MovePPUps"] = decryptData(pidAddress + BlockBoffset + START + 12)

    -- Remaining two bytes from Move PP Ups (0x36-0x37)
    nextRecursivePrng() -- Still need to update PRNG if we miss data

    -- First two bytes of Individual Values (0x38-0x39)
    local IVpart1 = decryptData(pidAddress + BlockBoffset + START + 16)

    -- Last two bytes of Individual Values (0x3A-0x3B)
    local IVpart2 = decryptData(pidAddress + BlockBoffset + START + 18)
    
    local IV = IVpart1 + (IVpart2 << 16)
    pokemonData["IV-HP"] = getBits(IV,0,5)
    pokemonData["IV-ATQ"] = getBits(IV,5,5)
    pokemonData["IV-DEF"] = getBits(IV,10,5)
    pokemonData["IV-SPE"] = getBits(IV,15,5)
    pokemonData["IV-SPA"] = getBits(IV,20,5)
    pokemonData["IV-SPD"] = getBits(IV,25,5)
    pokemonData["IsEgg"] = getBits(IV,30,1)
    pokemonData["IsNicknamed"] = getBits(IV,31,1)

    -- Hoenn Ribbon Set 1 (0x3C-0x3D)
    pokemonData["HoennRibbon1"] = decryptData(pidAddress + BlockBoffset + START + 20)

    -- Hoenn Ribbon Set 2 (0x3E-0x3F)
    pokemonData["HoennRibbon2"] = decryptData(pidAddress + BlockBoffset + START + 22)

    local genderForms = decryptData(pidAddress + BlockBoffset + START + 24)
    pokemonData["Female"] = getBits(genderForms,1,1)
    pokemonData["Genderless"] = getBits(genderForms,2,1)
    pokemonData["AlternateForms"] = getBits(genderForms,3,5)

    -- Unused (0x42-0x43)
    local unused = decryptData(pidAddress + BlockBoffset + START + 26)

    -- Egg Location (0x44-0x45)
    pokemonData["EggLocation"] = decryptData(pidAddress + BlockBoffset + START + 28)

    -- Met at Location (0x46-0x47)
    pokemonData["MetLocation"] = decryptData(pidAddress + BlockBoffset + START + 30)
end

function decryptBlockC(pokemonData, pidAddress, shiftValue, checksum)
    -- Seed PRNG with checksum
    prng = checksum

    -- Each block is shifted by a certain offset, calculated with BLOCK_{A-B-C-D}
    local BlockCoffset = (BLOCK_C[shiftValue + 1] - 1) * 32

    -- Skip the 32 bytes of the unwanted blocks to start at Block C
    -- Each PRNG next recursive value skips 2 bytes
    for i = 1, BLOCK_C[shiftValue + 1] - 1 do
        for j = 1, 16 do nextRecursivePrng() end
    end

    local searchNickname = true
    pokemonData["Nickname"] = ""
    
    -- Nickname (0x48-0x5D)
    for i = 0, 10 do
        -- Keep adding letters until we find 0xFFFF (end of nickname)
        if (searchNickname) then
            local nicknameLetter = decryptData(pidAddress + BlockCoffset + START + (i*2))

            if (nicknameLetter < 0xFFFF and CHARACTER_LIST[nicknameLetter - CHARACTER_LIST_OFFSET] ~= nil) then
                pokemonData["Nickname"] = pokemonData["Nickname"] .. CHARACTER_LIST[nicknameLetter - CHARACTER_LIST_OFFSET]
            else
                searchNickname = false
            end
        else
            nextRecursivePrng() -- Still need to update PRNG if we miss data
        end
    end

    -- Unused - Origin Game (0x5E-0x5F)
    pokemonData["OriginGame"] = getBits(decryptData(pidAddress + BlockCoffset + START + 22), 8, 8)

    -- Sinnoh Ribbon Set 3 (0x60-0x61)
    pokemonData["SinnohRibbon3"] = decryptData(pidAddress + BlockCoffset + START + 24)

    -- Sinnoh Ribbon Set 4 (0x62-0x63)
    pokemonData["SinnohRibbon4"] = decryptData(pidAddress + BlockCoffset + START + 26)

    -- Unused (0x64-0x67)
    -- data = decryptData(pidAddress + BlockCoffset + START + 28)
end

function decryptBlockD(pokemonData, pidAddress, shiftValue, checksum)
    -- Seed PRNG with checksum
    prng = checksum

    -- Each block is shifted by a certain offset, calculated with BLOCK_{A-B-C-D}
    local BlockDoffset = (BLOCK_D[shiftValue + 1] - 1) * 32

    -- Skip the 32 bytes of the unwanted blocks to start at Block D
    -- Each PRNG next recursive value skips 2 bytes
    for i = 1, BLOCK_D[shiftValue + 1] - 1 do
        for j = 1, 16 do nextRecursivePrng() end
    end

    local searchOTName = true
    pokemonData["OTName"] = ""
    
    -- OT Name (0x68-0x77)
    for i = 0, 7 do
        -- Keep adding letters until we find 0xFFFF (end of name)
        if (searchOTName) then
            local nameLetter = decryptData(pidAddress + BlockDoffset + START + (i*2))

            if (nameLetter < 0xFFFF and CHARACTER_LIST[nameLetter - CHARACTER_LIST_OFFSET] ~= nil) then
                pokemonData["OTName"] = pokemonData["OTName"] .. CHARACTER_LIST[nameLetter - CHARACTER_LIST_OFFSET]
            else
                searchOTName = false
            end
        else
            nextRecursivePrng() -- Still need to update PRNG if we miss data
        end 
    end

    -- Date Egg Received (0x78-0x7A)
    local yearMonth_Egg = decryptData(pidAddress + BlockDoffset + START + 16)

    -- Remaining byte of Date Egg Received and first byte of Date Met (0x7A-0x7B)
    local dayEgg_yearMet = decryptData(pidAddress + BlockDoffset + START + 18)

    -- Date Met (0x7B-0x7D)
    local monthDay_Met = decryptData(pidAddress + BlockDoffset + START + 20)

    local yearEgg = getBits(yearMonth_Egg,0,8)
    local monthEgg = getBits(yearMonth_Egg,8,8)
    local dayEgg = getBits(dayEgg_yearMet,0,8)

    local yearMet = getBits(dayEgg_yearMet,8,8)
    local monthMet = getBits(monthDay_Met,0,8)
    local dayMet = getBits(monthDay_Met,8,8)

    -- Format Egg Date
    pokemonData["DateEggReceived"] = 
        (dayEgg < 10 and "0" or "") .. dayEgg
        .. "/" .. (monthEgg < 10 and "0" or "") .. monthEgg
        .. "/20" .. (yearEgg < 10 and "0" or "") .. yearEgg

    -- Format Met Date
    pokemonData["DateMet"] = 
        (dayMet < 10 and "0" or "") .. dayMet
        .. "/" .. (monthMet < 10 and "0" or "") .. monthMet
        .. "/20" .. (yearMet < 10 and "0" or "") .. yearMet

    -- Egg Location (Diamond/Pearl) (0x7E-0x7F)
    pokemonData["EggLocationDP"] = decryptData(pidAddress + BlockDoffset + START + 22)

    -- Met Location (Diamond/Pearl) (0x80-0x81)
    pokemonData["MetLocationDP"] = decryptData(pidAddress + BlockDoffset + START + 24)

    -- Pokérus - Poké Ball (0x82-0x83)
    local pokerusPokeball = decryptData(pidAddress + BlockDoffset + START + 26)
    pokemonData["Pokerus"] = getBits(pokerusPokeball, 0, 8)
    pokemonData["Pokeball"] = ITEM_NAMES[getBits(pokerusPokeball, 8, 8)]

    -- Met At Level - Female OT Gender (0x84-0x85)
    local metLevelFemaleOT = decryptData(pidAddress + BlockDoffset + START + 28)
    pokemonData["MetLevel"] = getBits(metLevelFemaleOT, 0, 7)
    pokemonData["OTFemale"] = getBits(metLevelFemaleOT, 7, 1)

    -- HGSS Poké Ball - Unused (0x86-0x87)
    -- pokemonData["PokeballHGSS"] = getBits(decryptData(pidAddress + BlockDoffset + START + 30), 0, 8)
end

function decryptStats(pokemonData, pidAddress, shiftValue, pid)
    -- Seed PRNG with PID
    prng = pid

    -- Status (0x88)
    local status = getBits(decryptData(pidAddress + 0x88),0,8)
    pokemonData["Asleep"] = getBits(status,3,0) -- 3 bits to keep track of sleep rounds (0-7)
    pokemonData["Poisoned"] = getBits(status,1,3)
    pokemonData["Burned"] = getBits(status,1,4)
    pokemonData["Frozen"] = getBits(status,1,5)
    pokemonData["Paralyzed"] = getBits(status,1,6)
    pokemonData["Toxic"] = getBits(status,1,7)

    -- Unknown (0x8A-0x8B)
    nextRecursivePrng() -- Still need to update PRNG if we miss data

    -- Level - Capsule Index (Seals) (0x8C-0x8D)
    local levelCapsule = decryptData(pidAddress + 0x8C)
    pokemonData["Level"] = getBits(levelCapsule, 0, 8)
    pokemonData["Capsule"] = getBits(levelCapsule, 8, 8)

    -- Current HP (0x8E-0x8F)
    pokemonData["HPCurrent"] = decryptData(pidAddress + 0x8E)

    -- Max HP (0x90-0x91)
    pokemonData["HPMax"] = decryptData(pidAddress + 0x90)

    -- Attack (0x92-0x93)
    pokemonData["Attack"] = decryptData(pidAddress + 0x92)

    -- Defense (0x94-0x95)
    pokemonData["Defense"] = decryptData(pidAddress + 0x94)

    -- Speed (0x96-0x97)
    pokemonData["Speed"] = decryptData(pidAddress + 0x96)

    -- Special Attack (0x98-0x99)
    pokemonData["SpecialAttack"] = decryptData(pidAddress + 0x98)

    -- Special Defense (0x9A-0x9B)
    pokemonData["SpecialDefense"] = decryptData(pidAddress + 0x9A)

    -- Unknown - Contains Trash Data (0x9C-0xD3)
    for i = 1, 28 do nextRecursivePrng() end -- Still need to update PRNG if we miss data

    -- Seal Coordinates (0xD4-0xEB)
    pokemonData["SealCoordinates"] = decryptData(pidAddress + 0xD4)
end

-- PRNG is calculated using this formula : X[n+1] = (0x41C64E6D * X[n] + 0x6073)
function nextRecursivePrng()
    -- Make sure to restrain result within 32 bits at each step of the process
    -- Since lua does not do this automatically
    local product = (0x41C64E6D * prng) & 0xFFFFFFFF
    local sum = (product + 0x6073) & 0xFFFFFFFF

    prng = sum
end