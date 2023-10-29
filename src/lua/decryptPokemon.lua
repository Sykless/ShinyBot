-- Decryption algorithm :
-- • https://projectpokemon.org/docs/gen-4/pkm-structure-r65/
-- • https://bulbapedia.bulbagarden.net/wiki/Pok%C3%A9mon_data_structure_(Generation_IV)

-- Analysed these to better understand the algorithm :
-- • https://github.com/dude22072/PokeStats/tree/master
-- • https://github.com/yling/yPokeStats/tree/main
-- • https://github.com/kwsch/PKHeX/tree/master
-- • https://tasvideos.org/UserFiles/Info/45747701013813013 by FractalFusion

local json = require "json"

-- Block order dependening on the shift value (0-23)
BLOCK_A = {1,1,1,1,1,1,2,2,3,4,3,4,2,2,3,4,3,4,2,2,3,4,3,4}
BLOCK_B = {2,2,3,4,3,4,1,1,1,1,1,1,3,4,2,2,4,3,3,4,2,2,4,3}
BLOCK_C = {3,4,2,2,4,3,3,4,2,2,4,3,1,1,1,1,1,1,4,3,4,3,2,2}
BLOCK_D = {4,3,4,3,2,2,4,3,4,3,2,2,4,3,4,3,2,2,1,1,1,1,1,1}

-- Address of the first memory address in the Pokemon parameters
START = 0x08

function decryptPokemonData(selectedPidAddress)

    -- Retrieve PID and checksum from RAM
    local pid = memory.read_u32_le(selectedPidAddress)
    local checksum = memory.read_u16_le(selectedPidAddress + 0x06)

    -- Initialize Pokemon object to store decrypted data
    local pokemonData = {pid = pid, OT = {},
        EV = {}, IV = {}, stats = {}, 
        status = {}, moves = {}, met = {},
        contest = {}, ribbons = {}, egg = {}
    }

    -- Calculate Shift value used for block shuffling
    local shiftValue = ((pid & 0x3E000) >> 0xD) % 24

    -- Each parameter must be decrypted using PRNG (pseudorandom number generator)
    -- PRNG decryption covers two bytes at the time, so to get adjacent 1-byte values,
    -- We need to retrieve the 2-byte block, and then split the two values
    decryptBlockA(pokemonData, selectedPidAddress, shiftValue, checksum)
    decryptBlockB(pokemonData, selectedPidAddress, shiftValue, checksum)
    decryptBlockC(pokemonData, selectedPidAddress, shiftValue, checksum)
    decryptBlockD(pokemonData, selectedPidAddress, shiftValue, checksum)
    decryptStats(pokemonData, selectedPidAddress, shiftValue)

    -- Write Pokemon data in memory
    comm.mmfWrite("testfile", json.encode({["pokemonData"] = pokemonData}) .. "\x00")

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
    pokemonData["pokedexID"] = decryptData(pidAddress + BlockAoffset + START)
    pokemonData["name"] = POKEMON_NAMES[pokemonData["pokedexID"]]

    -- Held Item (0x0A-0x0B)
    pokemonData["item"] = decryptData(pidAddress + BlockAoffset + START + 2)

    -- OT ID (0x0C-0x0D)
    pokemonData["OT"]["ID"] = decryptData(pidAddress + BlockAoffset + START + 4)

    -- OT Secret ID (0x0E-0x0F)
    pokemonData["OT"]["secretID"] = decryptData(pidAddress + BlockAoffset + START + 6)

    -- Experience points (0x10-0x13)
    pokemonData["experience"] = decryptData(pidAddress + BlockAoffset + START + 8)

    -- Remaining two bytes from Experience points (0x12-0x13)
    -- Should I retrieve the last 2 bytes of Experience ?
    -- console.log("Missing experience : " .. (decryptData(pidAddress + BlockAoffset + START + 10)))
    nextRecursivePrng()  -- Still need to update PRNG if we miss data

    -- Friendship/Steps to Hatch - Ability (0x14-0x15)
    local friendship_ability = decryptData(pidAddress + BlockAoffset + START + 12)
    pokemonData["friendship"] = getBits(friendship_ability, 0, 8)
    pokemonData["ability"] = ABILITY_LIST[getBits(friendship_ability, 8, 8)]

    -- Markings - Original Language (0x16-0x17)
    local markings_originalLanguage = decryptData(pidAddress + BlockAoffset + START + 14)
    pokemonData["markings"] = getBits(markings_originalLanguage, 0, 8)
    pokemonData["originalLanguage"] = LANGUAGE_LIST[getBits(markings_originalLanguage, 8, 8)]

    -- HP Effort Value - Attack Effort Value (0x18-0x19)
    local HpEv_AtkEv = decryptData(pidAddress + BlockAoffset + START + 16)
    pokemonData["EV"]["HP"] = getBits(HpEv_AtkEv, 0, 8)
    pokemonData["EV"]["attack"] = getBits(HpEv_AtkEv, 8, 8)

    -- Defense Effort Value - Speed Effort Value (0x1A-0x1B)
    local DefEv_SpeEv = decryptData(pidAddress + BlockAoffset + START + 18)
    pokemonData["EV"]["defense"] = getBits(DefEv_SpeEv, 0, 8)
    pokemonData["EV"]["speed"] = getBits(DefEv_SpeEv, 8, 8)

    -- SP Attack Effort Value - SP Defense Effort Value (0x1C-0x1D)
    SpaEv_SpdEv = decryptData(pidAddress + BlockAoffset + START + 20)
    pokemonData["EV"]["specialAttack"] = getBits(SpaEv_SpdEv, 0, 8)
    pokemonData["EV"]["specialDefense"] = getBits(SpaEv_SpdEv, 8, 8)

    -- Cool/Beauty Contest Value (0x1E-0x1F)
    coolBeautyContest = decryptData(pidAddress + BlockAoffset + START + 22)
    pokemonData["contest"]["cool"] = getBits(coolBeautyContest, 0, 8)
    pokemonData["contest"]["beauty"] = getBits(coolBeautyContest, 8, 8)

    -- Cute/Smart Contest Value (0x20-0x21)
    local cuteSmartContest = decryptData(pidAddress + BlockAoffset + START + 24)
    pokemonData["contest"]["cute"] = getBits(cuteSmartContest, 0, 8)
    pokemonData["contest"]["smart"] = getBits(cuteSmartContest, 8, 8)

    -- Tough/Sheen Contest Value (0x22-0x23)
    local toughSheenContest = decryptData(pidAddress + BlockAoffset + START + 26)
    pokemonData["contest"]["tough"] = getBits(toughSheenContest, 0, 8)
    pokemonData["contest"]["sheen"] = getBits(toughSheenContest, 8, 8)

    -- Sinnoh Ribbon Set 1 (0x24-0x25)
    pokemonData["ribbons"]["sinnohRibbon1"] = decryptData(pidAddress + BlockAoffset + START + 28)

    -- Sinnoh Ribbon Set 2 (0x26-0x27)
    pokemonData["ribbons"]["sinnohRibbon2"] = decryptData(pidAddress + BlockAoffset + START + 30)
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
    local move1Name = MOVE_NAMES[decryptData(pidAddress + BlockBoffset + START)]
    if (move1Name) then pokemonData["moves"][1] = {name = move1Name} end

    -- Move 2 ID (0x2A-0x2B)
    local move2Name = MOVE_NAMES[decryptData(pidAddress + BlockBoffset + START + 2)]
    if (move2Name) then pokemonData["moves"][2] = {name = move2Name} end

    -- Move 3 ID (0x2C-0x2D)
    local move3Name = MOVE_NAMES[decryptData(pidAddress + BlockBoffset + START + 4)]
    if (move3Name) then pokemonData["moves"][3] = {name = move3Name} end

    -- Move 4 ID (0x2E-0x2F)
    local move4Name = MOVE_NAMES[decryptData(pidAddress + BlockBoffset + START + 6)]
    if (move4Name) then pokemonData["moves"][4] = {name = move4Name} end
    
    -- Move 1-2 Current PP (0x30-0x31)
    local move12pp = decryptData(pidAddress + BlockBoffset + START + 8)
    if (pokemonData["moves"][1]) then pokemonData["moves"][1]["PP"] = getBits(move12pp, 0, 8) end
    if (pokemonData["moves"][2]) then pokemonData["moves"][2]["PP"] = getBits(move12pp, 8, 8) end

    -- Move 3-4 Current PP (0x32-0x33)
    local move34pp = decryptData(pidAddress + BlockBoffset + START + 10)
    if (pokemonData["moves"][3]) then pokemonData["moves"][3]["PP"] = getBits(move34pp, 0, 8) end
    if (pokemonData["moves"][4]) then pokemonData["moves"][4]["PP"] = getBits(move34pp, 8, 8) end

    -- Move PP Ups (0x34-0x37)
    local movePPUpPart1 = decryptData(pidAddress + BlockBoffset + START + 12)
    local movePPUpPart2 = decryptData(pidAddress + BlockBoffset + START + 14)
    if (pokemonData["moves"][1]) then pokemonData["moves"][1]["PPUp"] = getBits(movePPUpPart1, 0, 8) end
    if (pokemonData["moves"][2]) then pokemonData["moves"][2]["PPUp"] = getBits(movePPUpPart1, 8, 8) end
    if (pokemonData["moves"][3]) then pokemonData["moves"][3]["PPUp"] = getBits(movePPUpPart2, 0, 8) end
    if (pokemonData["moves"][4]) then pokemonData["moves"][4]["PPUp"] = getBits(movePPUpPart2, 8, 8) end

    -- First two bytes of Individual Values (0x38-0x39)
    local IVpart1 = decryptData(pidAddress + BlockBoffset + START + 16)

    -- Last two bytes of Individual Values (0x3A-0x3B)
    local IVpart2 = decryptData(pidAddress + BlockBoffset + START + 18)
    
    local IV = IVpart1 + (IVpart2 << 16)
    pokemonData["IV"]["HP"] = getBits(IV,0,5)
    pokemonData["IV"]["attack"] = getBits(IV,5,5)
    pokemonData["IV"]["defense"] = getBits(IV,10,5)
    pokemonData["IV"]["speed"] = getBits(IV,15,5)
    pokemonData["IV"]["specialAttack"] = getBits(IV,20,5)
    pokemonData["IV"]["specialDefense"] = getBits(IV,25,5)
    pokemonData["isEgg"] = getBits(IV,30,1) == 1
    pokemonData["nicknamed"] = getBits(IV,31,1) == 1

    -- Hoenn Ribbon Set 1 (0x3C-0x3D)
    pokemonData["ribbons"]["hoennRibbon1"] = decryptData(pidAddress + BlockBoffset + START + 20)

    -- Hoenn Ribbon Set 2 (0x3E-0x3F)
    pokemonData["ribbons"]["hoennRibbon2"] = decryptData(pidAddress + BlockBoffset + START + 22)

    local genderForms = decryptData(pidAddress + BlockBoffset + START + 24)
    pokemonData["female"] = getBits(genderForms,1,1) == 1
    pokemonData["genderless"] = getBits(genderForms,2,1) == 1
    pokemonData["alternateForms"] = getBits(genderForms,3,5)

    -- Unused (0x42-0x43)
    local unused = decryptData(pidAddress + BlockBoffset + START + 26)

    -- Egg Location (0x44-0x45)
    pokemonData["met"]["locationEggReceived"] = decryptData(pidAddress + BlockBoffset + START + 28)

    -- Met at Location (0x46-0x47)
    pokemonData["met"]["location"] = decryptData(pidAddress + BlockBoffset + START + 30)
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
    pokemonData["nickname"] = ""
    
    -- Nickname (0x48-0x5D)
    for i = 0, 10 do
        -- Keep adding letters until we find 0xFFFF (end of nickname)
        if (searchNickname) then
            local nicknameLetter = decryptData(pidAddress + BlockCoffset + START + (i*2))

            if (nicknameLetter < 0xFFFF and CHARACTER_LIST[nicknameLetter - CHARACTER_LIST_OFFSET] ~= nil) then
                pokemonData["nickname"] = pokemonData["nickname"] .. CHARACTER_LIST[nicknameLetter - CHARACTER_LIST_OFFSET]
            else
                searchNickname = false
            end
        else
            nextRecursivePrng() -- Still need to update PRNG if we miss data
        end
    end

    -- Unused - Origin Game (0x5E-0x5F)
    pokemonData["originGame"] = getBits(decryptData(pidAddress + BlockCoffset + START + 22), 8, 8)

    -- Sinnoh Ribbon Set 3 (0x60-0x61)
    pokemonData["ribbons"]["sinnohRibbon3"] = decryptData(pidAddress + BlockCoffset + START + 24)

    -- Sinnoh Ribbon Set 4 (0x62-0x63)
    pokemonData["ribbons"]["sinnohRibbon4"] = decryptData(pidAddress + BlockCoffset + START + 26)

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
    pokemonData["OT"]["name"] = ""
    
    -- OT Name (0x68-0x77)
    for i = 0, 7 do
        -- Keep adding letters until we find 0xFFFF (end of name)
        if (searchOTName) then
            local nameLetter = decryptData(pidAddress + BlockDoffset + START + (i*2))

            if (nameLetter < 0xFFFF and CHARACTER_LIST[nameLetter - CHARACTER_LIST_OFFSET] ~= nil) then
                pokemonData["OT"]["name"] = pokemonData["OT"]["name"] .. CHARACTER_LIST[nameLetter - CHARACTER_LIST_OFFSET]
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
    pokemonData["met"]["dateEggReceived"] = 
        (dayEgg < 10 and "0" or "") .. dayEgg
        .. "/" .. (monthEgg < 10 and "0" or "") .. monthEgg
        .. "/20" .. (yearEgg < 10 and "0" or "") .. yearEgg

    -- Format Met Date
    pokemonData["met"]["date"] = 
        (dayMet < 10 and "0" or "") .. dayMet
        .. "/" .. (monthMet < 10 and "0" or "") .. monthMet
        .. "/20" .. (yearMet < 10 and "0" or "") .. yearMet

    -- Egg Location (Diamond/Pearl) (0x7E-0x7F)
    -- pokemonData["met"]["locationEggReceivedDP"] = decryptData(pidAddress + BlockDoffset + START + 22)
    nextRecursivePrng()

    -- Met Location (Diamond/Pearl) (0x80-0x81)
    -- pokemonData["met"]["locationDP"] = decryptData(pidAddress + BlockDoffset + START + 24)
    nextRecursivePrng()

    -- Pokérus - Poké Ball (0x82-0x83)
    local pokerusPokeball = decryptData(pidAddress + BlockDoffset + START + 26)
    pokemonData["pokerus"] = getBits(pokerusPokeball, 0, 8)
    pokemonData["pokeball"] = ITEM_NAMES[getBits(pokerusPokeball, 8, 8)]

    -- Met At Level - Female OT Gender (0x84-0x85)
    local metLevelFemaleOT = decryptData(pidAddress + BlockDoffset + START + 28)
    pokemonData["met"]["level"] = getBits(metLevelFemaleOT, 0, 7)
    pokemonData["OT"]["female"] = getBits(metLevelFemaleOT, 7, 1) == 1

    -- HGSS Poké Ball - Unused (0x86-0x87)
    -- pokemonData["PokeballHGSS"] = getBits(decryptData(pidAddress + BlockDoffset + START + 30), 0, 8)
end

function decryptStats(pokemonData, pidAddress, shiftValue)
    -- Seed PRNG with PID
    prng = pokemonData["pid"]

    -- Status (0x88)
    local status = getBits(decryptData(pidAddress + 0x88),0,8)
    pokemonData["status"]["asleep"] = getBits(status,3,0) -- 3 bits to keep track of sleep rounds (0-7)
    pokemonData["status"]["poisoned"] = getBits(status,1,3) == 1
    pokemonData["status"]["burned"] = getBits(status,1,4) == 1
    pokemonData["status"]["frozen"] = getBits(status,1,5) == 1
    pokemonData["status"]["paralyzed"] = getBits(status,1,6) == 1
    pokemonData["status"]["toxic"] = getBits(status,1,7) == 1

    -- Unknown (0x8A-0x8B)
    nextRecursivePrng() -- Still need to update PRNG if we miss data

    -- Level - Capsule Index (Seals) (0x8C-0x8D)
    local levelCapsule = decryptData(pidAddress + 0x8C)
    pokemonData["level"] = getBits(levelCapsule, 0, 8)
    pokemonData["capsule"] = getBits(levelCapsule, 8, 8)

    -- Current HP (0x8E-0x8F)
    pokemonData["currentHP"] = decryptData(pidAddress + 0x8E)

    -- Max HP (0x90-0x91)
    pokemonData["stats"]["HP"] = decryptData(pidAddress + 0x90)

    -- Attack (0x92-0x93)
    pokemonData["stats"]["attack"] = decryptData(pidAddress + 0x92)

    -- Defense (0x94-0x95)
    pokemonData["stats"]["defense"] = decryptData(pidAddress + 0x94)

    -- Speed (0x96-0x97)
    pokemonData["stats"]["speed"] = decryptData(pidAddress + 0x96)

    -- Special Attack (0x98-0x99)
    pokemonData["stats"]["specialAttack"] = decryptData(pidAddress + 0x98)

    -- Special Defense (0x9A-0x9B)
    pokemonData["stats"]["specialDefense"] = decryptData(pidAddress + 0x9A)

    -- Unknown - Contains Trash Data (0x9C-0xD3)
    for i = 1, 28 do nextRecursivePrng() end -- Still need to update PRNG if we miss data

    -- Seal Coordinates (0xD4-0xEB)
    pokemonData["sealCoordinates"] = decryptData(pidAddress + 0xD4)
end

-- PRNG is calculated using this formula : X[n+1] = (0x41C64E6D * X[n] + 0x6073)
function nextRecursivePrng()
    -- Make sure to restrain result within 32 bits at each step of the process
    -- Since lua does not do this automatically
    local product = (0x41C64E6D * prng) & 0xFFFFFFFF
    local sum = (product + 0x6073) & 0xFFFFFFFF

    prng = sum
end