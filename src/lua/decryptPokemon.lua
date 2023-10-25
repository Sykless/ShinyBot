-- Decryption algorithm :
-- • https://projectpokemon.org/docs/gen-4/pkm-structure-r65/
-- • https://bulbapedia.bulbagarden.net/wiki/Pok%C3%A9mon_data_structure_(Generation_IV)

-- Analysed these to better understand the algorithm :
-- • https://github.com/dude22072/PokeStats/tree/master
-- • https://github.com/yling/yPokeStats/tree/main
-- • https://github.com/kwsch/PKHeX/tree/master
-- • https://tasvideos.org/UserFiles/Info/45747701013813013 by FractalFusion

function decryptBlockA()
    -- Seed PRNG with checksum
    prng = checksum

    -- Skip the 32 bytes of the unwanted blocks to start at Block A
    -- Each PRNG next recursive value skips 2 bytes
    for i = 1, BlockA[shiftValue + 1] - 1 do
        for j = 1, 16 do prng = nextRecursivePrng(prng) end
    end

    -- National Pokédex ID (0x08-0x09)
    prng = nextRecursivePrng(prng)
    pokemon["PokedexID"] = memory.read_u16_le(pidAddr + BlockAoffset + 8) ~ getUpper16Bits(prng)
    pokemon[" Name "] = POKEMON_NAMES[pokemon["PokedexID"]]

    -- Held Item (0x0A-0x0B)
    prng = nextRecursivePrng(prng)
    pokemon["HeldItem"] = memory.read_u16_le(pidAddr + BlockAoffset + 8 + 2) ~ getUpper16Bits(prng)

    -- OT ID (0x0C-0x0D)
    prng = nextRecursivePrng(prng)
    pokemon["OT"] = memory.read_u16_le(pidAddr + BlockAoffset + 8 + 4) ~ getUpper16Bits(prng)

    -- OT Secret ID (0x0E-0x0F)
    prng = nextRecursivePrng(prng)
    pokemon["OTSecretID"] = memory.read_u16_le(pidAddr + BlockAoffset + 8 + 6) ~ getUpper16Bits(prng)

    -- Experience points (0x10-0x13)
    prng = nextRecursivePrng(prng)
    pokemon["Experience"] = memory.read_u16_le(pidAddr + BlockAoffset + 8 + 8) ~ getUpper16Bits(prng)

    -- Remaining two bytes from Experience points (0x12-0x13)
    -- Should I retrieve the last 2 bytes of Experience ?
    -- console.log("Missing experience : " .. (memory.read_u16_le(pidAddr + BlockAoffset + 8 + 10) ~ getUpper16Bits(prng)))
    prng = nextRecursivePrng(prng)

    -- Friendship/Steps to Hatch - Ability (0x14-0x15)
    prng = nextRecursivePrng(prng)
    friendship_ability = memory.read_u16_le(pidAddr + BlockAoffset + 8 + 12) ~ getUpper16Bits(prng)

    pokemon["Friendship"] = getBits(friendship_ability, 0, 8)
    pokemon["Ability"] = ABILITY_LIST[getBits(friendship_ability, 8, 8)]

    -- Markings - Original Language (0x16-0x17)
    prng = nextRecursivePrng(prng)
    markings_originalLanguage = memory.read_u16_le(pidAddr + BlockAoffset + 8 + 14) ~ getUpper16Bits(prng)

    pokemon["Markings"] = getBits(markings_originalLanguage, 0, 8)
    pokemon["OriginalLanguage"] = LANGUAGE_LIST[getBits(markings_originalLanguage, 8, 8)]

    -- HP Effort Value - Attack Effort Value (0x18-0x19)
    prng = nextRecursivePrng(prng)
    HpEv_AtkEv = memory.read_u16_le(pidAddr + BlockAoffset + 8 + 16) ~ getUpper16Bits(prng)

    pokemon["EV-HP"] = getBits(HpEv_AtkEv, 0, 8)
    pokemon["EV-ATQ"] = getBits(HpEv_AtkEv, 8, 8)

    -- Defense Effort Value - Speed Effort Value (0x1A-0x1B)
    prng = nextRecursivePrng(prng)
    DefEv_SpeEv = memory.read_u16_le(pidAddr + BlockAoffset + 8 + 18) ~ getUpper16Bits(prng)

    pokemon["EV-DEF"] = getBits(DefEv_SpeEv, 0, 8)
    pokemon["EV-SPE"] = getBits(DefEv_SpeEv, 8, 8)

    -- SP Attack Effort Value - SP Defense Effort Value (0x1C-0x1D)
    prng = nextRecursivePrng(prng)
    SpaEv_SpdEv = memory.read_u16_le(pidAddr + BlockAoffset + 8 + 20) ~ getUpper16Bits(prng)

    pokemon["EV-SPA"] = getBits(SpaEv_SpdEv, 0, 8)
    pokemon["EV-SPD"] = getBits(SpaEv_SpdEv, 8, 8)

    -- Cool/Beauty Contest Value (0x1E-0x1F)
    prng = nextRecursivePrng(prng)
    coolBeautyContest = memory.read_u16_le(pidAddr + BlockAoffset + 8 + 22) ~ getUpper16Bits(prng)

    pokemon["ContestCool"] = getBits(coolBeautyContest, 0, 8)
    pokemon["ContestBeauty"] = getBits(coolBeautyContest, 8, 8)

    -- Cute/Smart Contest Value (0x20-0x21)
    prng = nextRecursivePrng(prng)
    cuteSmartContest = memory.read_u16_le(pidAddr + BlockAoffset + 8 + 24) ~ getUpper16Bits(prng)
    
    pokemon["ContestCute"] = getBits(cuteSmartContest, 0, 8)
    pokemon["ContestSmart"] = getBits(cuteSmartContest, 8, 8)

    -- Tough/Sheen Contest Value (0x22-0x23)
    prng = nextRecursivePrng(prng)
    toughSheenContest = memory.read_u16_le(pidAddr + BlockAoffset + 8 + 26) ~ getUpper16Bits(prng)

    pokemon["ContestTouch"] = getBits(toughSheenContest, 0, 8)
    pokemon["ContestSheen"] = getBits(toughSheenContest, 8, 8)

    -- Sinnoh Ribbon Set 1 (0x24-0x25)
    prng = nextRecursivePrng(prng)
    pokemon["SinnohRibbon3"] = memory.read_u16_le(pidAddr + BlockAoffset + 8 + 28) ~ getUpper16Bits(prng)

    -- Sinnoh Ribbon Set 2 (0x26-0x27)
    prng = nextRecursivePrng(prng)
    pokemon["SinnohRibbon4"] = memory.read_u16_le(pidAddr + BlockAoffset + 8 + 30) ~ getUpper16Bits(prng)
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
    prng = nextRecursivePrng(prng)
    pokemon["Move1"] = MOVE_NAMES[memory.read_u16_le(pidAddr + BlockBoffset + 8) ~ getUpper16Bits(prng)]

    -- Move 2 ID (0x2A-0x2B)
    prng = nextRecursivePrng(prng)
    pokemon["Move2"] = MOVE_NAMES[memory.read_u16_le(pidAddr + BlockBoffset + 8 + 2) ~ getUpper16Bits(prng)]

    -- Move 3 ID (0x2C-0x2D)
    prng = nextRecursivePrng(prng)
    pokemon["Move3"] = MOVE_NAMES[memory.read_u16_le(pidAddr + BlockBoffset + 8 + 4) ~ getUpper16Bits(prng)]

    -- Move 4 ID (0x2E-0x2F)
    prng = nextRecursivePrng(prng)
    pokemon["Move4"] = MOVE_NAMES[memory.read_u16_le(pidAddr + BlockBoffset + 8 + 6) ~ getUpper16Bits(prng)]

    -- Move 1-2 Current PP (0x30-0x31)
    prng = nextRecursivePrng(prng)
    move12pp = memory.read_u16_le(pidAddr + BlockBoffset + 8 + 8) ~ getUpper16Bits(prng)

    pokemon["Move1PP"] = getBits(move12pp, 0, 8)
    pokemon["Move2PP"] = getBits(move12pp, 8, 8)

    -- Move 3-4 Current PP (0x32-0x33)
    prng = nextRecursivePrng(prng)
    move34pp = memory.read_u16_le(pidAddr + BlockBoffset + 8 + 10) ~ getUpper16Bits(prng)

    pokemon["Move3PP"] = getBits(move34pp, 0, 8)
    pokemon["Move4PP"] = getBits(move34pp, 8, 8)

    -- Move PP Ups (0x34-0x37)
    prng = nextRecursivePrng(prng)
    ppUp = memory.read_u16_le(pidAddr + BlockBoffset + 8 + 12) ~ getUpper16Bits(prng)
    pokemon["MovePPUps"] = getBits(ppUp, 0, 4)

    -- Remaining two bytes from Move PP Ups (0x36-0x37)
    prng = nextRecursivePrng(prng)

    -- First two bytes of Individual Values (0x38-0x39)
    prng = nextRecursivePrng(prng)
    IVpart1 = memory.read_u16_le(pidAddr + BlockBoffset + 8 + 16) ~ getUpper16Bits(prng)

    -- Last two bytes of Individual Values (0x3A-0x3B)
    prng = nextRecursivePrng(prng)
    IVpart2 = memory.read_u16_le(pidAddr + BlockBoffset + 8 + 18) ~ getUpper16Bits(prng)
    
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
    prng = nextRecursivePrng(prng)
    pokemon["HoennRibbon1"] = memory.read_u16_le(pidAddr + BlockBoffset + 8 + 20) ~ getUpper16Bits(prng)

    -- Hoenn Ribbon Set 2 (0x3E-0x3F)
    prng = nextRecursivePrng(prng)
    pokemon["HoennRibbon2"] = memory.read_u16_le(pidAddr + BlockBoffset + 8 + 22) ~ getUpper16Bits(prng)

    -- Gender - Alternate Forms (0x40-0x41)
    prng = nextRecursivePrng(prng)
    data = memory.read_u16_le(pidAddr + BlockBoffset + 8 + 24) ~ getUpper16Bits(prng)

    pokemon["Female"] = getBits(data,1,1)
    pokemon["Genderless"] = getBits(data,2,1)
    pokemon["AlternateForms"] = getBits(data,3,5)

    -- Unused (0x42-0x43)
    prng = nextRecursivePrng(prng)

    -- Egg Location (0x44-0x45)
    prng = nextRecursivePrng(prng)
    pokemon["EggLocation"] = memory.read_u16_le(pidAddr + BlockBoffset + 8 + 28) ~ getUpper16Bits(prng)

    -- Met at Location (0x46-0x47)
    prng = nextRecursivePrng(prng)
    pokemon["MetLocation"] = memory.read_u16_le(pidAddr + BlockBoffset + 8 + 30) ~ getUpper16Bits(prng)
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
        prng = nextRecursivePrng(prng)

        -- Keep adding letters until we find 0xFFFF (end of nickname)
        if (searchNickname) then
            nicknameLetter = memory.read_u16_le(pidAddr + BlockCoffset + 8 + (i*2)) ~ getUpper16Bits(prng)

            if (nicknameLetter < 0xFFFF) then
                pokemon["Nickname"] = pokemon["Nickname"] .. CHARACTER_LIST[nicknameLetter - CHARACTER_LIST_OFFSET]
            else
                searchNickname = false
            end
        end
    end

    -- Unused - OriginGame (0x5E-0x5F)
    prng = nextRecursivePrng(prng)
    pokemon["OriginGame"] = getBits(memory.read_u16_le(pidAddr + BlockCoffset + 8 + 22) ~ getUpper16Bits(prng), 8, 8)

    -- Sinnoh Ribbon Set 3 (0x60-0x61)
    prng = nextRecursivePrng(prng)
    pokemon["SinnohRibbon3"] = memory.read_u16_le(pidAddr + BlockCoffset + 8 + 24) ~ getUpper16Bits(prng)

    -- Sinnoh Ribbon Set 4 (0x62-0x63)
    prng = nextRecursivePrng(prng)
    pokemon["SinnohRibbon4"] = memory.read_u16_le(pidAddr + BlockCoffset + 8 + 26) ~ getUpper16Bits(prng)

    -- Unused (0x62-0x63)
    -- prng = nextRecursivePrng(prng)
    -- console.log(memory.read_u16_le(pidAddr + BlockCoffset + 8 + 28) ~ getUpper16Bits(prng))
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
        prng = nextRecursivePrng(prng)

        -- Keep adding letters until we find 0xFFFF (end of name)
        if (searchOTName) then
            nameLetter = memory.read_u16_le(pidAddr + BlockDoffset + 8 + (i*2)) ~ getUpper16Bits(prng)

            if (nameLetter < 0xFFFF) then
                pokemon["OTName"] = pokemon["OTName"] .. CHARACTER_LIST[nameLetter - CHARACTER_LIST_OFFSET]
            else
                searchOTName = false
            end
        end
    end

    -- Date Egg Received (0x78-0x7A)
    prng = nextRecursivePrng(prng)
    yearMonth_Egg = memory.read_u16_le(pidAddr + BlockDoffset + 8 + 16) ~ getUpper16Bits(prng)

    -- Remaining byte of Date Egg Received and first byte of Date Met (0x7A-0x7B)
    prng = nextRecursivePrng(prng)
    dayEgg_yearMet = memory.read_u16_le(pidAddr + BlockDoffset + 8 + 18) ~ getUpper16Bits(prng)

    -- Date Met (0x7B-0x7D)
    prng = nextRecursivePrng(prng)
    monthDay_Met = memory.read_u16_le(pidAddr + BlockDoffset + 8 + 20) ~ getUpper16Bits(prng)

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
    prng = nextRecursivePrng(prng)
    -- pokemon["EggLocation"] = memory.read_u16_le(pidAddr + BlockDoffset + 8 + 22) ~ getUpper16Bits(prng)

    -- Met Location (Diamond/Pearl) (0x80-0x81)
    prng = nextRecursivePrng(prng)
    -- pokemon["MetLocation"] = memory.read_u16_le(pidAddr + BlockDoffset + 8 + 24) ~ getUpper16Bits(prng)

    -- Pokérus - Poké Ball (0x82-0x83)
    prng = nextRecursivePrng(prng)
    pokerusPokeball = memory.read_u16_le(pidAddr + BlockDoffset + 8 + 26) ~ getUpper16Bits(prng)

    pokemon["Pokerus"] = getBits(pokerusPokeball, 0, 8)
    pokemon["Pokeball"] = ITEM_NAMES[getBits(pokerusPokeball, 8, 8)]

    -- Met At Level - Female OT Gender (0x84-0x85)
    prng = nextRecursivePrng(prng)
    metLevelFemaleOT = memory.read_u16_le(pidAddr + BlockDoffset + 8 + 28) ~ getUpper16Bits(prng)

    pokemon["MetLevel"] = getBits(metLevelFemaleOT, 0, 7)
    pokemon["OTFemale"] = getBits(metLevelFemaleOT, 7, 1)

    -- HGSS Poké Ball - Unused (0x86-0x87)
    -- prng = nextRecursivePrng(prng)
    -- pokemon["Pokeball"] = getBits(memory.read_u16_le(pidAddr + BlockDoffset + 8 + 30) ~ getUpper16Bits(prng), 0, 8)
end

-- function decryptStats()
--     -- -- Current stats
--     -- prng = pid
--     -- prng = nextRecursivePrng(prng)
--     -- statusConditions = getBits(memory.read_u8(pidAddr + 0x88) ~ getUpper16Bits(prng), 0, 8)
--     -- prng = nextRecursivePrng(prng)
--     -- prng = nextRecursivePrng(prng)
--     -- level = getBits((memory.read_u16_le(pidAddr + 0x8C) ~ getUpper16Bits(prng)),0,8)
--     -- prng = nextRecursivePrng(prng)
--     -- hpstat = (memory.read_u16_le(pidAddr + 0x8E) ~ getUpper16Bits(prng))
--     -- prng = nextRecursivePrng(prng)
--     -- maxhpstat = (memory.read_u16_le(pidAddr + 0x90) ~ getUpper16Bits(prng))

--     -- console.log("level : " .. level)
--     -- console.log("maxhpstat : " .. maxhpstat) 
-- end