def formatNumber(number):
    stringNumber = str(number)

    if (len(stringNumber) == 1):
        return " " + stringNumber + " "
    elif (len(stringNumber) == 2):
        return " " + stringNumber
    else:
        return stringNumber