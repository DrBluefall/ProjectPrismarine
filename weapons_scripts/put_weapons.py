"""Module that stores all weapons from Splatoon 2."""
import json


def main():
    """."""
    with open("./all_weapons.json", "r") as infile:
        json_weapons = json.load(infile)

    for key, value in json_weapons.items():
        print(key, value)


if __name__ == "__main__":
    main()
