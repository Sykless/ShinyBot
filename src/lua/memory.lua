dofile "utils.lua"

BUTTON_MAPPING = {
    ["A"] = "A",
    ["B"] = "B",
    ["X"] = "X",
    ["Y"] = "Y",
    ["L"] = "L",
    ["R"] = "R",
    ["d"] = "Down",
    ["l"] = "Left",
    ["u"] = "Up",
    ["r"] = "Right",
    ["s"] = "Select",
    ["S"] = "Start",
    ["@"] = "Nothing"
}

local runSections = {}
local runSectionId = -1
local processedInputs = 0

function readRunSectionsFromMemory()
    -- Read data from memory file sent by Python script
    local mmfRunSections = comm.mmfRead("runSections", 20480)
    local runSectionsString = string.match(mmfRunSections, "[^\x00]+") -- Get everything before the first null \x00 character
    local runSectionsInt = {}

    if (runSectionsString) then
        local runSectionsSplit = splitString(runSectionsString, "/")

        -- Convert string sections to int arrays
        for id, substring in ipairs(runSectionsSplit) do
            local stringSection = splitString(substring, "-")
            table.insert(runSectionsInt, {["start"] = tonumber(stringSection[1]), ["end"] = tonumber(stringSection[2])})
        end

        -- Erase old memory values
        comm.mmfWrite("runSections", string.rep("\x00", 20480))
    end

    return runSectionsInt
end

function inputFromMemory(runFlag)
    -- Read data from memory file sent by Python script
    local mmfJoypad = comm.mmfRead("joypad", 20480)
    local joypadInput = string.match(mmfJoypad, "[^\x00]+") -- Get everything before the first null \x00 character

    if (joypadInput) then

        -- We just received new inputs, check if we also need to run
        if (runSectionId == -1) then
            runSections = readRunSectionsFromMemory()

            -- Set runSectionsId to 0 if we don't have to run at all
            if (next(runSections) == nil) then
                runSectionId = 0
            else
                runSectionId = 1
            end
        -- Increase the number of processed inputs
        else
            processedInputs = processedInputs + 1
        end
        
        -- Retrieve the first button of the sequence (only 1 input per frame)
        local joypadMap = {}
        local buttonPress = string.sub(joypadInput,1,1)
        local remainingInputs = string.sub(joypadInput, 2, string.len(joypadInput))

        -- Copnvert value retreived from memory to actual button pressed
        joypadMap[BUTTON_MAPPING[buttonPress]] = "True"

        -- If run sections are present, check if we need to run
        if (runSectionId > 0 and runSectionId <= #runSections) then

            -- Go to next section when we go above it
            if (processedInputs > runSections[runSectionId]["end"]) then
                runSectionId = runSectionId + 1
            end

            -- Between start and end, press B to run
            if (runSectionId <= #runSections and processedInputs >= runSections[runSectionId]["start"] and processedInputs < runSections[runSectionId]["end"]) then
                joypadMap["B"] = "True"
            end
        end

        -- Apply generated joypad to emulator
        joypad.set(joypadMap)
    
        -- Erase first input with \x00 null character and shift the rest to the left
        comm.mmfWrite("joypad", remainingInputs .. "\x00")

    -- No more input to process, prepare to read runSections
    else
        runSectionId = -1
        processedInputs = 0
    end
end

function readFlagsFromMemory()
    local mmfFlags = comm.mmfRead("flagsData", 20480)
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

