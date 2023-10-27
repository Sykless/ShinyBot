function displayPokemonInfo(pokemon, pidAddressUsed)
    if pokemon["Move1"] ~= nil then
        console.log(
            pokemon[" Name "] .. " " .. (pokemon["Female"] == 0 and "♂" or "♀")
            .. " level " .. pokemon["Level"] .. " (" .. pokemon["Ability"] .. ")\n"
            .. " - " .. pokemon["Move1"] .. " (" .. pokemon["Move1PP"] .."/".. pokemon["Move1PP"] .. ")\n"
            .. (pokemon["Move2"] and (" - " .. pokemon["Move2"] .. " (" .. pokemon["Move2PP"] .."/".. pokemon["Move2PP"] .. ")\n") or "")
            .. (pokemon["Move3"] and (" - " .. pokemon["Move3"] .. " (" .. pokemon["Move3PP"] .."/".. pokemon["Move3PP"] .. ")\n") or "")
            .. (pokemon["Move4"] and (" - " .. pokemon["Move4"] .. " (" .. pokemon["Move4PP"] .."/".. pokemon["Move4PP"] .. ")\n") or "")
        )

        console.log(
            " =============================================\n"
            .. " =       =  HP = ATQ = DEF = SPA = SPD = SPE =\n"
            .. " =============================================\n"
            .. " = STATS = ".. formatNumber(pokemon["HPMax"]) .." = ".. formatNumber(pokemon["Attack"]) .." = ".. formatNumber(pokemon["Defense"]) .." = ".. formatNumber(pokemon["SpecialAttack"]) .." = ".. formatNumber(pokemon["SpecialDefense"]) .." = ".. formatNumber(pokemon["Speed"]) .." =\n"
            .. " =============================================\n"
            .. " = IV    = ".. formatNumber(pokemon["IV-HP"]) .." = ".. formatNumber(pokemon["IV-ATQ"]) .." = ".. formatNumber(pokemon["IV-DEF"]) .." = ".. formatNumber(pokemon["IV-SPA"]) .." = ".. formatNumber(pokemon["IV-SPD"]) .." = ".. formatNumber(pokemon["IV-SPE"]) .." =\n"
            .. " =============================================\n"
            .. " = EV    = ".. formatNumber(pokemon["EV-HP"]) .." = ".. formatNumber(pokemon["EV-ATQ"]) .." = ".. formatNumber(pokemon["EV-DEF"]) .." = ".. formatNumber(pokemon["EV-SPA"]) .." = ".. formatNumber(pokemon["EV-SPD"]) .." = ".. formatNumber(pokemon["EV-SPE"]) .." =\n"
            .. " =============================================\n"
        )
    else
        console.log("Frère j'ai cherché là j'ai pas trouvé : 0x" .. getHexValue(pidAddressUsed))
        console.log(pokemon)
    end
end

function formatNumber(number)
    if (string.len(number) == 1) then
        return " "..number.." "
    elseif (string.len(number) == 2) then
        return " "..number
    else
        return number
    end
end

function getHexValue(intValue)
    return string.format("%x", intValue)
end