"""Loadout.ink's encoding and decoding module, translated into Python."""
"""
Encoding allows to encode a set of gears and abilities into a single string and vice-versa.
The encoded string is composed of 25 hexadecimal characters (from 0 to 9 and from A to F).
The first digit is the version number of the encoding mechanism and is 0 at the moment.
This will allow to change the encoding method in the future while ensuring backward compatibility.
Format:
0 0 XX XXXXXXX XXXXXXX XXXXXXX
^ ^ ^  ^       ^       ^
| | |  |       |       |
Version number |       |
  | |  |       |       |
  Weapon set   |       |
    |  |       |       |
    Weapon ID  |       |
       |       |       |
       Encoded Hat     |
               |       |
               Encoded Clothes
                       |
                       Encoded Shoes
Example:
0 0 00 241084e 0000000 07c8000
Gears (hats, clothes, shoes) are all encoded the same way.
The value is made of 7 hexadecimal characters.
Format:
XX XXXXX
^  ^
|  |
Gear id
   |
   Abilities
Example:
07c8000
Abilities format:
XXXXX hex to binary
XXXXX XXXXX XXXXX XXXXX (there is a trick here: hexa to binaries are then groupped by 5 digits)
^    ^    ^    ^
|    |    |    |
Main |    |    |
Sub 1|    |    |
     Sub 2|    |
          Sub 3|
Example:
c8000 => 11001 00000 00000 00000
"""


def decode_gear(code):
    """Convert a gear code into a dictionary."""
    gearid = int(code[0:2], 16)
    raw_abilities = code[2:8]
    bin_abilities = hex_to_binary(raw_abilities)["result"]
    main = int(bin_abilities[0:5], 2)
    subs = []
    i = 5
    while i < len(bin_abilities):
        subs.append(int(bin_abilities[i : i + 5], 2))
        i += 5

    return {"gear": gearid, "main": main, "subs": subs}


def decode(code):
    """Convert a loadout.ink code into a dictionary."""
    if code[0] != "0":
        raise KeyError("invalid code")
    weaponset = int(code[1])
    weaponid = int(code[2:4], 16)
    head = decode_gear(code[4:11])
    clothes = decode_gear(code[11:18])
    shoes = decode_gear(code[18:25])

    return {"set": weaponset, "weapon": weaponid, "head": head, "clothes": clothes, "shoes": shoes}


def hex_to_binary(s):
    """Convert a hexadecimal string to a binary string."""
    ret = ""
    # lookup table for easier conversion. '0' characters are padded for '1' to '7'
    lookup_table = {
        "0": "0000",
        "1": "0001",
        "2": "0010",
        "3": "0011",
        "4": "0100",
        "5": "0101",
        "6": "0110",
        "7": "0111",
        "8": "1000",
        "9": "1001",
        "a": "1010",
        "b": "1011",
        "c": "1100",
        "d": "1101",
        "e": "1110",
        "f": "1111",
        "A": "1010",
        "B": "1011",
        "C": "1100",
        "D": "1101",
        "E": "1110",
        "F": "1111",
    }
    i = 0
    while i != len(s):
        if s[i] in lookup_table:
            ret = ret + lookup_table[s[i]]
        else:
            return {"valid": False}
        i += 1
    return {"valid": True, "result": ret}
