-- Decryption algorithm :
-- • https://projectpokemon.org/docs/gen-4/pkm-structure-r65/
-- • https://bulbapedia.bulbagarden.net/wiki/Pok%C3%A9mon_data_structure_(Generation_IV)

-- Analysed these to better understand the algorithm :
-- • https://github.com/dude22072/PokeStats/tree/master
-- • https://github.com/yling/yPokeStats/tree/main
-- • https://github.com/kwsch/PKHeX/tree/master
-- • https://tasvideos.org/UserFiles/Info/45747701013813013 by FractalFusion

-- Block order dependening on the shift value (0-23)
BlockA = {1,1,1,1,1,1,2,2,3,4,3,4,2,2,3,4,3,4,2,2,3,4,3,4}
BlockB = {2,2,3,4,3,4,1,1,1,1,1,1,3,4,2,2,4,3,3,4,2,2,4,3}
BlockC = {3,4,2,2,4,3,3,4,2,2,4,3,1,1,1,1,1,1,4,3,4,3,2,2}
BlockD = {4,3,4,3,2,2,4,3,4,3,2,2,4,3,4,3,2,2,1,1,1,1,1,1}

-- Address of the first memory address in the Pokemon parameters
START = 0x08

function decryptPokemonData(pidAddr)
    -- Retrieve PID and checksum from RAM
    pid = memory.read_u32_le(pidAddr)
    checksum = memory.read_u16_le(pidAddr + 6)

    -- Calculate Shift value used for block shuffling - see decryptPokemon.lua
    shiftValue = ((pid & 0x3E000) >> 0xD) % 24
    console.log("shiftValue : " .. shiftValue .. " -> " 
        .. BlockA[shiftValue + 1]
        .. BlockB[shiftValue + 1]
        .. BlockC[shiftValue + 1]
        .. BlockD[shiftValue + 1]
        .. "\n"
    )

    -- Each block is shift by a certain offset, calculated with Block{A-B-C-D}
    BlockAoffset = (BlockA[shiftValue + 1] - 1) * 32
    BlockBoffset = (BlockB[shiftValue + 1] - 1) * 32
    BlockCoffset = (BlockC[shiftValue + 1] - 1) * 32
    BlockDoffset = (BlockD[shiftValue + 1] - 1) * 32

    -- Each parameter must be decrypted using PRNG (pseudorandom number generator)
    -- PRNG decryption covers two bytes at the time, so to get adjacent 1-byte values,
    -- We need to retrieve the 2-byte block, and then split the two values
    decryptBlockA()
    decryptBlockB()
    decryptBlockC()
    decryptBlockD()
    decryptStats()
end

function decryptBlockA()
    -- Seed PRNG with checksum
    prng = checksum

    -- Skip the 32 bytes of the unwanted blocks to start at Block A
    -- Each PRNG next recursive value skips 2 bytes
    for i = 1, BlockA[shiftValue + 1] - 1 do
        for j = 1, 16 do prng = nextRecursivePrng(prng) end
    end

    -- National Pokédex ID (START-0x09)
    pokemon["PokedexID"] = decryptData(pidAddr + BlockAoffset + START)
    pokemon[" Name "] = POKEMON_NAMES[pokemon["PokedexID"]]

    -- Held Item (0x0A-0x0B)
    pokemon["HeldItem"] = decryptData(pidAddr + BlockAoffset + START + 2)

    -- OT ID (0x0C-0x0D)
    pokemon["OT"] = decryptData(pidAddr + BlockAoffset + START + 4)

    -- OT Secret ID (0x0E-0x0F)
    pokemon["OTSecretID"] = decryptData(pidAddr + BlockAoffset + START + 6)

    -- Experience points (0x10-0x13)
    pokemon["Experience"] = decryptData(pidAddr + BlockAoffset + START + 8)

    -- Remaining two bytes from Experience points (0x12-0x13)
    -- Should I retrieve the last 2 bytes of Experience ?
    -- console.log("Missing experience : " .. (decryptData(pidAddr + BlockAoffset + START + 10)))
    prng = nextRecursivePrng(prng)  -- Still need to update PRNG if we miss data

    -- Friendship/Steps to Hatch - Ability (0x14-0x15)
    friendship_ability = decryptData(pidAddr + BlockAoffset + START + 12)
    pokemon["Friendship"] = getBits(friendship_ability, 0, 8)
    pokemon["Ability"] = ABILITY_LIST[getBits(friendship_ability, 8, 8)]

    -- Markings - Original Language (0x16-0x17)
    markings_originalLanguage = decryptData(pidAddr + BlockAoffset + START + 14)
    pokemon["Markings"] = getBits(markings_originalLanguage, 0, 8)
    pokemon["OriginalLanguage"] = LANGUAGE_LIST[getBits(markings_originalLanguage, 8, 8)]

    -- HP Effort Value - Attack Effort Value (0x18-0x19)
    HpEv_AtkEv = decryptData(pidAddr + BlockAoffset + START + 16)
    pokemon["EV-HP"] = getBits(HpEv_AtkEv, 0, 8)
    pokemon["EV-ATQ"] = getBits(HpEv_AtkEv, 8, 8)

    -- Defense Effort Value - Speed Effort Value (0x1A-0x1B)
    DefEv_SpeEv = decryptData(pidAddr + BlockAoffset + START + 18)
    pokemon["EV-DEF"] = getBits(DefEv_SpeEv, 0, 8)
    pokemon["EV-SPE"] = getBits(DefEv_SpeEv, 8, 8)

    -- SP Attack Effort Value - SP Defense Effort Value (0x1C-0x1D)
    SpaEv_SpdEv = decryptData(pidAddr + BlockAoffset + START + 20)
    pokemon["EV-SPA"] = getBits(SpaEv_SpdEv, 0, 8)
    pokemon["EV-SPD"] = getBits(SpaEv_SpdEv, 8, 8)

    -- Cool/Beauty Contest Value (0x1E-0x1F)
    coolBeautyContest = decryptData(pidAddr + BlockAoffset + START + 22)
    pokemon["ContestCool"] = getBits(coolBeautyContest, 0, 8)
    pokemon["ContestBeauty"] = getBits(coolBeautyContest, 8, 8)

    -- Cute/Smart Contest Value (0x20-0x21)
    cuteSmartContest = decryptData(pidAddr + BlockAoffset + START + 24)
    pokemon["ContestCute"] = getBits(cuteSmartContest, 0, 8)
    pokemon["ContestSmart"] = getBits(cuteSmartContest, 8, 8)

    -- Tough/Sheen Contest Value (0x22-0x23)
    toughSheenContest = decryptData(pidAddr + BlockAoffset + START + 26)
    pokemon["ContestTouch"] = getBits(toughSheenContest, 0, 8)
    pokemon["ContestSheen"] = getBits(toughSheenContest, 8, 8)

    -- Sinnoh Ribbon Set 1 (0x24-0x25)
    pokemon["SinnohRibbon3"] = decryptData(pidAddr + BlockAoffset + START + 28)

    -- Sinnoh Ribbon Set 2 (0x26-0x27)
    pokemon["SinnohRibbon4"] = decryptData(pidAddr + BlockAoffset + START + 30)
end

function decryptBlockB()
    -- Seed PRNG with checksum
    prng = checksum

    -- Skip the 32 bytes of the unwanted blocks to start at Block B
    -- Each PRNG next recursive value skips 2 bytes
    for i = 1, BlockB[shiftValue + 1] - 1 do
        for j = 1, 16 do prng = nextRecursivePrng(prng) end
    end

    -- Move 1 ID (0x28-0x29)
    pokemon["Move1"] = MOVE_NAMES[decryptData(pidAddr + BlockBoffset + START)]

    -- Move 2 ID (0x2A-0x2B)
    pokemon["Move2"] = MOVE_NAMES[decryptData(pidAddr + BlockBoffset + START + 2)]

    -- Move 3 ID (0x2C-0x2D)
    pokemon["Move3"] = MOVE_NAMES[decryptData(pidAddr + BlockBoffset + START + 4)]

    -- Move 4 ID (0x2E-0x2F)
    pokemon["Move4"] = MOVE_NAMES[decryptData(pidAddr + BlockBoffset + START + 6)]

    -- Move 1-2 Current PP (0x30-0x31)
    move12pp = decryptData(pidAddr + BlockBoffset + START + 8)
    pokemon["Move1PP"] = getBits(move12pp, 0, 8)
    pokemon["Move2PP"] = getBits(move12pp, 8, 8)

    -- Move 3-4 Current PP (0x32-0x33)
    move34pp = decryptData(pidAddr + BlockBoffset + START + 10)
    pokemon["Move3PP"] = getBits(move34pp, 0, 8)
    pokemon["Move4PP"] = getBits(move34pp, 8, 8)

    -- Move PP Ups (0x34-0x37)
    pokemon["MovePPUps"] = decryptData(pidAddr + BlockBoffset + START + 12)

    -- Remaining two bytes from Move PP Ups (0x36-0x37)
    prng = nextRecursivePrng(prng) -- Still need to update PRNG if we miss data

    -- First two bytes of Individual Values (0x38-0x39)
    IVpart1 = decryptData(pidAddr + BlockBoffset + START + 16)

    -- Last two bytes of Individual Values (0x3A-0x3B)
    IVpart2 = decryptData(pidAddr + BlockBoffset + START + 18)
    
    IV = IVpart1 + (IVpart2 << 16)
    pokemon["IV-HP"] = getBits(IV,0,5)
    pokemon["IV-ATQ"] = getBits(IV,5,5)
    pokemon["IV-DEF"] = getBits(IV,10,5)
    pokemon["IV-SPE"] = getBits(IV,15,5)
    pokemon["IV-SPA"] = getBits(IV,20,5)
    pokemon["IV-SPD"] = getBits(IV,25,5)
    pokemon["IsEgg"] = getBits(IV,30,1)
    pokemon["IsNicknamed"] = getBits(IV,31,1)

    -- Hoenn Ribbon Set 1 (0x3C-0x3D)
    pokemon["HoennRibbon1"] = decryptData(pidAddr + BlockBoffset + START + 20)

    -- Hoenn Ribbon Set 2 (0x3E-0x3F)
    pokemon["HoennRibbon2"] = decryptData(pidAddr + BlockBoffset + START + 22)

    -- Gender - Alternate Forms (0x40-0x41)
    data = decryptData(pidAddr + BlockBoffset + START + 24)
    pokemon["Female"] = getBits(data,1,1)
    pokemon["Genderless"] = getBits(data,2,1)
    pokemon["AlternateForms"] = getBits(data,3,5)

    -- Unused (0x42-0x43)
    prng = nextRecursivePrng(prng) -- Still need to update PRNG if we miss data

    -- Egg Location (0x44-0x45)
    pokemon["EggLocation"] = decryptData(pidAddr + BlockBoffset + START + 28)

    -- Met at Location (0x46-0x47)
    pokemon["MetLocation"] = decryptData(pidAddr + BlockBoffset + START + 30)
end

function decryptBlockC()
    -- Seed PRNG with checksum
    prng = checksum

    -- Skip the 32 bytes of the unwanted blocks to start at Block C
    -- Each PRNG next recursive value skips 2 bytes
    for i = 1, BlockC[shiftValue + 1] - 1 do
        for j = 1, 16 do prng = nextRecursivePrng(prng) end
    end

    searchNickname = true
    pokemon["Nickname"] = ""
    
    -- Nickname (0x48-0x5D)
    for i = 0, 10 do
        -- Keep adding letters until we find 0xFFFF (end of nickname)
        if (searchNickname) then
            nicknameLetter = decryptData(pidAddr + BlockCoffset + START + (i*2))

            if (nicknameLetter < 0xFFFF) then
                pokemon["Nickname"] = pokemon["Nickname"] .. CHARACTER_LIST[nicknameLetter - CHARACTER_LIST_OFFSET]
            else
                searchNickname = false
            end
        else
            prng = nextRecursivePrng(prng) -- Still need to update PRNG if we miss data
        end
    end

    -- Unused - Origin Game (0x5E-0x5F)
    pokemon["OriginGame"] = getBits(decryptData(pidAddr + BlockCoffset + START + 22), 8, 8)

    -- Sinnoh Ribbon Set 3 (0x60-0x61)
    pokemon["SinnohRibbon3"] = decryptData(pidAddr + BlockCoffset + START + 24)

    -- Sinnoh Ribbon Set 4 (0x62-0x63)
    pokemon["SinnohRibbon4"] = decryptData(pidAddr + BlockCoffset + START + 26)

    -- Unused (0x64-0x67)
    -- data = decryptData(pidAddr + BlockCoffset + START + 28)
end

function decryptBlockD()
    -- Seed PRNG with checksum
    prng = checksum

    -- Skip the 32 bytes of the unwanted blocks to start at Block D
    -- Each PRNG next recursive value skips 2 bytes
    for i = 1, BlockD[shiftValue + 1] - 1 do
        for j = 1, 16 do prng = nextRecursivePrng(prng) end
    end

    searchOTName = true
    pokemon["OTName"] = ""
    
    -- OT Name (0x68-0x77)
    for i = 0, 7 do
        -- Keep adding letters until we find 0xFFFF (end of name)
        if (searchOTName) then
            nameLetter = decryptData(pidAddr + BlockDoffset + START + (i*2))

            if (nameLetter < 0xFFFF) then
                pokemon["OTName"] = pokemon["OTName"] .. CHARACTER_LIST[nameLetter - CHARACTER_LIST_OFFSET]
            else
                searchOTName = false
            end
        else
            prng = nextRecursivePrng(prng) -- Still need to update PRNG if we miss data
        end 
    end

    -- Date Egg Received (0x78-0x7A)
    yearMonth_Egg = decryptData(pidAddr + BlockDoffset + START + 16)

    -- Remaining byte of Date Egg Received and first byte of Date Met (0x7A-0x7B)
    dayEgg_yearMet = decryptData(pidAddr + BlockDoffset + START + 18)

    -- Date Met (0x7B-0x7D)
    monthDay_Met = decryptData(pidAddr + BlockDoffset + START + 20)

    yearEgg = getBits(yearMonth_Egg,0,8)
    monthEgg = getBits(yearMonth_Egg,8,8)
    dayEgg = getBits(dayEgg_yearMet,0,8)

    yearMet = getBits(dayEgg_yearMet,8,8)
    monthMet = getBits(monthDay_Met,0,8)
    dayMet = getBits(monthDay_Met,8,8)

    -- Format Egg Date
    pokemon["DateEggReceived"] = 
        (dayEgg < 10 and "0" or "") .. dayEgg
        .. "/" .. (monthEgg < 10 and "0" or "") .. monthEgg
        .. "/20" .. (yearEgg < 10 and "0" or "") .. yearEgg

    -- Format Met Date
    pokemon["DateMet"] = 
        (dayMet < 10 and "0" or "") .. dayMet
        .. "/" .. (monthMet < 10 and "0" or "") .. monthMet
        .. "/20" .. (yearMet < 10 and "0" or "") .. yearMet

    -- Egg Location (Diamond/Pearl) (0x7E-0x7F)
    pokemon["EggLocationDP"] = decryptData(pidAddr + BlockDoffset + START + 22)

    -- Met Location (Diamond/Pearl) (0x80-0x81)
    pokemon["MetLocationDP"] = decryptData(pidAddr + BlockDoffset + START + 24)

    -- Pokérus - Poké Ball (0x82-0x83)
    pokerusPokeball = decryptData(pidAddr + BlockDoffset + START + 26)
    pokemon["Pokerus"] = getBits(pokerusPokeball, 0, 8)
    pokemon["Pokeball"] = ITEM_NAMES[getBits(pokerusPokeball, 8, 8)]

    -- Met At Level - Female OT Gender (0x84-0x85)
    metLevelFemaleOT = decryptData(pidAddr + BlockDoffset + START + 28)
    pokemon["MetLevel"] = getBits(metLevelFemaleOT, 0, 7)
    pokemon["OTFemale"] = getBits(metLevelFemaleOT, 7, 1)

    -- HGSS Poké Ball - Unused (0x86-0x87)
    -- pokemon["PokeballHGSS"] = getBits(decryptData(pidAddr + BlockDoffset + START + 30), 0, 8)
end

function decryptStats()
    -- Seed PRNG with PID
    prng = pid

    -- Status (0x88)
    status = getBits(decryptData(pidAddr + 0x88),0,8)

    pokemon["Asleep"] = getBits(status,3,0) -- 3 bits to keep track of sleep rounds (0-7)
    pokemon["Poisoned"] = getBits(status,1,3)
    pokemon["Burned"] = getBits(status,1,4)
    pokemon["Frozen"] = getBits(status,1,5)
    pokemon["Paralyzed"] = getBits(status,1,6)
    pokemon["Toxic"] = getBits(status,1,7)

    -- Unknown (0x8A-0x8B)
    prng = nextRecursivePrng(prng) -- Still need to update PRNG if we miss data

    -- Level - Capsule Index (Seals) (0x8C-0x8D)
    levelCapsule = decryptData(pidAddr + 0x8C)
    pokemon["Level"] = getBits(levelCapsule, 0, 8)
    pokemon["Capsule"] = getBits(levelCapsule, 8, 8)

    -- Current HP (0x8E-0x8F)
    pokemon["HPCurrent"] = decryptData(pidAddr + 0x8E)

    -- Max HP (0x90-0x91)
    pokemon["HPMax"] = decryptData(pidAddr + 0x90)

    -- Attack (0x92-0x93)
    pokemon["Attack"] = decryptData(pidAddr + 0x92)

    -- Defense (0x94-0x95)
    pokemon["Defense"] = decryptData(pidAddr + 0x94)

    -- Speed (0x96-0x97)
    pokemon["Speed"] = decryptData(pidAddr + 0x96)

    -- Special Attack (0x98-0x99)
    pokemon["SpecialAttack"] = decryptData(pidAddr + 0x98)

    -- Special Defense (0x9A-0x9B)
    pokemon["SpecialDefense"] = decryptData(pidAddr + 0x9A)

    -- Unknown - Contains Trash Data (0x9C-0xD3)
    for i = 1, 28 do prng = nextRecursivePrng(prng) end -- Still need to update PRNG if we miss data

    -- Seal Coordinates (0xD4-0xEB)
    pokemon["SealCoordinates"] = decryptData(pidAddr + 0xD4)
end