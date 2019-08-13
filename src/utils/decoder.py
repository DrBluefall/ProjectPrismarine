class DecodeError(Exception):
    pass

def decode_gear(code):
    gear_id = int(code[:2], base=16)
    raw_abilities= code[2:8]
    bin_abilities = hex_to_bin(raw_abilities)
    main = int(bin_abilities[:5], 2)
    subs = [ int(bin_abilities[i:i+5], 2) for i in range(5, len(bin_abilities), 5) ]
    return {
    "gear_id": gear_id,
    "main": main,
    "subs": subs
    }

def decode(code):
    if code[0] != '0':
        raise ValueError("Invalid Code.")
    try:
        weapon_set = int(code[1])
        weapon_id = int(code[2:4], 16)
        head = decode_gear(code[4:11])
        clothes = decode_gear(code[11:18])
        shoes = decode_gear(code[18:25])
    except Exception as err:
        raise DecodeError(str(err)) from err
    return {
    "set": weapon_set,
    "id": weapon_id,
    "head": head,
    "clothes": clothes,
    "shoes": shoes
    }

def hex_to_bin(s):
    ret = ''
    lookup_table = {
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
    for index, value in enumerate(s):
        if value in lookup_table.keys():
            ret += lookup_table[value]
        else:
            raise ValueError("Invalid value specified in hex to binary conversion.")
    return ret