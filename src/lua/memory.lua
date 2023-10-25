function getHexValue(intValue)
    return string.format("%x", intValue)
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

    local result = multiplyUpperUpper + multiplyUpperLower + multiplyLowerUpper + multiplyLowerLower

    return result
end

-- PRNG is calculated using this formula : X[n+1] = (0x41C64E6D * X[n] + 0x6073)
function nextRecursivePrng(prngValue)
    -- Make sure to restrain result within 32 bits at each step of the process
    -- Since lua does not do this automatically
    local mul = (0x41C64E6D * prngValue) & 0xFFFFFFFF
    local sum = (mul + 0x6073) & 0xFFFFFFFF

    return sum
end

function getUpper16Bits(a)
    return a >> 16
end

function getBits(a,b,d)
	return (a >> b) % (1 << d)
end

