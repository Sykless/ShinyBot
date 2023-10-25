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

-- PRNG is calculated using this formula : X[n+1] = (0x41C64E6D * X[n] + 0x6073)
function nextRecursivePrng(prngValue)
    -- Make sure to restrain result within 32 bits at each step of the process
    -- Since lua does not do this automatically
    local product = (0x41C64E6D * prngValue) & 0xFFFFFFFF
    local sum = (product + 0x6073) & 0xFFFFFFFF

    return sum
end

-- Decryption is performed using this formula : data = encrypted xor (PNRG >> 16)
function decryptData(address)
    prng = nextRecursivePrng(prng) -- Update PRNG before each decryption
    encryptedData = memory.read_u16_le(address) -- Retrieve encrypted data from RAM
    decryptedData = encryptedData ~ (prng >> 16) -- Decrypt data using above formula

    return decryptedData
end

function getHexValue(intValue)
    return string.format("%x", intValue)
end

function getBits(a,b,d)
	return (a >> b) % (1 << d)
end

