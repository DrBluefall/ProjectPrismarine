"""Module storing all weapons from Splatoon 2."""
import json

with open("./weapons.json", "r") as infile:
    json_weapons = json.load(infile)

for key, value in json_weapons.items():
    pass
