-- Not actually used, but can be useful to find a memory address

function lineToHexAddress(line,column)
    local hexValue = getHexValue(line-1)
    local columnId = {"0", "4", "8", "C"}

    while string.len(hexValue) < 5 do
        hexValue = "0" .. hexValue
    end

    return "02" .. hexValue .. columnId[column] 
end

function lineToNumberAddress(line,column)
    return tonumber(lineToHexAddress(line,column),16)
end

function lineToIntMemoryValue(line, column)
    local address = lineToNumberAddress(line,column)
    return memory.read_u32_le(address)
end

function lineToHexMemoryValue(line, column)
    local intMemoryValue = lineToIntMemoryValue(line,column)
    return getHexValue(intMemoryValue)
end

function displayMemoryValue(line,column)
    local address = lineToNumberAddress(line,column)
    local intMemoryValue = memory.read_u32_le(address)
    local hexaMemoryValue = getHexValue(intMemoryValue)

    console.log("Line " .. line .. ", column " .. column .. " : " .. hexaMemoryValue)
end

function readbyterange(address, bytes)
    -- bytes must be a multiple of 4
    if bytes % 4 ~= 0 then
        return 0
    end

    local text = ""
    local iterations = bytes / 4

    for i = 0, iterations - 1 do 
        data = memory.read_u32_le(address + 4*i)
        hexData = getHexValue(data)

        for j = 1, 7, 2 do 
            intAsciiValue = tonumber(string.sub(hexData, j, j+1),16)

            if intAsciiValue ~= 0 then
                text = text .. string.char(intAsciiValue)
            else
                text = text .. " "
            end
        end
    end

    return text
end

-- Ouisticram combat - PID = C04E266C -> 6C 26 4E C0
-- -> 163411, 4ème colonne
-- -> 173723, 4ème colonne
-- -> 180472, 2ème colonne
-- -> 181674, 3ème colonne
-- -> 182739, 2ème colonne
-- -> 232622, 1ère colonne

-- Ouisticram combat 2nd - PID = C04E266C -> 6C 26 4E C0
-- -> 163426, 3ème colonne
-- -> 173738, 3ème colonne
-- -> 182754, 1ère colonne
-- -> 232622, 1ère colonne

-- Ouisticram overworld - PID = C04E266C -> 6C 26 4E C0
-- -> 163426, 4ème colonne
-- -> 232622, 1ère colonne

-- Ouisticram overworld 2nd - PID = C04E266C -> 6C 26 4E C0
-- -> 163411, 4ème colonne
-- -> 232622, 1ère colonne

-- Keunotor ennemi combat - PID = 04217957 -> 57 79 21 04
-- -> 173814, 4ème colonne
-- -> 174542, 2ème colonne
-- -> 180459, 2ème colonne -- nope
-- -> 181686, 3ème colonne -- nope
-- -> 182830, 2ème colonne

-- Keunotor combat - PID = 04217957 -> 57 79 21 04
-- -> 163411, 4ème colonne
-- -> 173723, 4ème colonne
-- -> 180472, 2ème colonne -- nope
-- -> 181674, 3ème colonne -- nope
-- -> 182739, 2ème colonne
-- -> 232636, 4ème colonne -- nope

-- Keunotor overworld - PID = 04217957 -> 57 79 21 04
-- -> 163411, 3ème colonne
-- -> 232636, 4ème colonne

-- Keunotor overworld 2nd - PID = 04217957 -> 57 79 21 04
-- -> 163426, 3ème colonne

-- displayMemoryValue(173814,4)
-- displayMemoryValue(174542,2)
-- displayMemoryValue(180459,2)  -- nope
-- displayMemoryValue(181686,3)  -- nope
-- displayMemoryValue(182830,2)

-- gameNameAddress = 0x023FF000
-- gameLanguage = 0x023FFE0F

-- games["POKEMON PL"]["F"]={
--     "Pokemon Platinum (PAL)",
--     memory.readdword(0x02101D2C) + 0xD094,
--     memory.readdword(memory.readdword(0x02101D2C) + 0x352F4) + 0x7A0,
--     0xEC
-- }

-- start = status==1 and games[version][lan][2] + games[version][lan][4] * (substatus[1]-1) 
-- or games[version][lan][3] + games[version][lan][4] * (substatus[2]-1) -- Set the pokemon start adress

-- console.log("Hexa start : 0x" .. getHexValue(start))
-- console.log("Hexa PID : 0x" .. getHexValue(memory.read_u32_le(start)))
-- console.log("Hexa PID : 0x" .. getHexValue(memory.read_u32_le(0x022a6f5C)))
-- console.log("Hexa PID : 0x" .. getHexValue(memory.read_u32_le(0x022a9cd4))) -- nope
-- console.log("Hexa PID : 0x" .. getHexValue(memory.read_u32_le(0x022c0ea4))) -- nope
-- console.log("Hexa PID : 0x" .. getHexValue(memory.read_u32_le(0x022c5b58))) -- nope
-- console.log("Hexa PID : 0x" .. getHexValue(memory.read_u32_le(0x022ca2d4))) -- nope