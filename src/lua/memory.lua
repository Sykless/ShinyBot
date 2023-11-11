BUTTON_MAPPING = {
    ["A"] = {["A"] = "True"},
    ["B"] = {["B"] = "True"},
    ["X"] = {["X"] = "True"},
    ["Y"] = {["Y"] = "True"},
    ["L"] = {["L"] = "True"},
    ["R"] = {["R"] = "True"},
    ["d"] = {["Down"] = "True"},
    ["l"] = {["Left"] = "True"},
    ["u"] = {["Up"] = "True"},
    ["r"] = {["Right"] = "True"},
    ["s"] = {["Select"] = "True"},
    ["S"] = {["Start"] = "True"},
    ["@"] = {}
}

function inputFromMemory(runFlag)
    -- Read data from memory file sent by Python script
    local mmfJoypad = comm.mmfRead("joypad", 4096)
    local joypadInput = string.match(mmfJoypad, "[^\x00]+") -- Get everything before the first null \x00 character

    if (joypadInput) then
        -- Retrieve the first button of the sequence (only 1 input per frame)
        local buttonPress = string.sub(joypadInput,1,1)
        local remainingInputs = string.sub(joypadInput, 2, string.len(joypadInput))

        local joypadMap = BUTTON_MAPPING[buttonPress]

        if (runFlag) then
            joypadMap["B"] = "True"
        end
    
        joypad.set(joypadMap)
    
        -- Erase first input with \x00 null character and shift the rest to the left
        comm.mmfWrite("joypad", remainingInputs .. "\x00")
    end
end

function readFlagsFromMemory()
    local mmfFlags = comm.mmfRead("flagsData", 4096)
    return {
        runInput = string.sub(mmfFlags,1,1) == "1"
    }
end

-- 32 bits multiplication, see http://www.sunshine2k.de/coding/c/mul32x32.html
function multiply32(a,b) -- 
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

