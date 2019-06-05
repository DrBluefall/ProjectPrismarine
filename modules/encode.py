
def hexToBinary(s):
    i, k, part, ret = ''
    # lookup table for easier conversion. '0' characters are padded for '1' to '7'
    lookupTable = {
        '0': '0000',
        '1': '0001',
        '2': '0010',
        '3': '0011',
        '4': '0100',
        '5': '0101',
        '6': '0110',
        '7': '0111',
        '8': '1000',
        '9': '1001',
        'a': '1010',
        'b': '1011',
        'c': '1100',
        'd': '1101',
        'e': '1110',
        'f': '1111',
        'A': '1010',
        'B': '1011',
        'C': '1100',
        'D': '1101',
        'E': '1110',
        'F': '1111'
    }
    for i in len(s):
        if lookupTable.hasOwnProperty(s[i]):
            ret += lookupTable[s[i]]
        else:
            valid = False
            return valid
    valid = True
    result = ret
    return valid, result


def decodeGear(code):
    gearid = int(code.substring(0, 2), 16)
    rawAbilities = code.substring(2, 8)
    binAbilities = hexToBinary(rawAbilities).result
    main = int(binAbilities.substring(0, 5), 2)
    subs = []
    i = 5
    for i in len(binAbilities):
        subs.append(int(binAbilities.substring(i, i+5), 2))

    decoded_gear = {
        'gear': gearid,
        'main': main,
        'subs': subs
    }
    return decoded_gear


def decode(code):
    if code[0] != 0:
        print("invalid code")
        return False
    try:
        weaponset = int(code[1])
        weaponid = int(code.substring(2, 4), 16)
        head = decodeGear(code.substring(4, 11))
        clothes = decodeGear(code.substring(11, 18))
        shoes = decodeGear(code.substring(18, 25))
    except Exception as err:
        print("Invalid code: " + err)
        return False

    decoded_loadout = {
        'set': weaponset,
        'weapon': weaponid,
        'head': head,
        'clothes': clothes,
        'shoes': shoes
    }
    return decoded_loadout
