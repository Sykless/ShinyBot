function getHexValue(intValue)
    return string.format("%x", intValue)
end

function splitString(inputString, separator)
    local substringArray = {}

    -- Match every substring between separators
    for substring in string.gmatch(inputString, "([^" .. separator .. "]+)") do
        table.insert(substringArray, substring)
    end

    -- Return each substring in an array
    return substringArray
end