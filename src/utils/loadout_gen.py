# Core Language Imports

from PIL import Image
from pprint import pprint

# Third-Party Imports

import pg8000 as pg

asset_db = pg.connect(user='prismarine-core', database='assets')
ac = asset_db.cursor()
ab_query = "SELECT row_to_json(abilities) FROM abilities WHERE id = %s;"
unknown = {
    "image": "../assets/img/skills/Unknown.png",
    "name": "Unknown"
}

def get_subs(ab_list):
    return [ ac.execute(ab_query, (i,)).fetchone() if i != 0 else unknown for i in ab_list ]

def compile_loadout_dict(loadout: dict):
    weapon_set = ac.execute("""
    SELECT row_to_json(main_weapons), row_to_json(sub_weapons), row_to_json(special_weapons) FROM main_weapons
        JOIN special_weapons ON main_weapons.special=special_weapons.name
        JOIN sub_weapons ON main_weapons.sub=sub_weapons.name
        WHERE site_id = %s AND class = %s;
    """, (loadout["id"], loadout["set"])).fetchone()
    head = {
        "gear": ac.execute("""
        SELECT row_to_json(headgear) FROM headgear WHERE id = %s;
        """, (loadout["head"]["gear_id"],)).fetchone(),
        "main": ac.execute(ab_query, (loadout["head"]["main"],)).fetchone()[0] if loadout["head"]["main"] != 0 else unknown,
        "subs": [ val for sublist in get_subs(loadout["head"]["subs"]) for val in sublist ]
    }
    clothes = {
        "gear": ac.execute("""
        SELECT row_to_json(clothing) FROM clothing WHERE id = %s;
        """, (loadout["clothes"]["gear_id"],)).fetchone(),
        "main": ac.execute(ab_query, (loadout["clothes"]["main"],)).fetchone()[0] if loadout["clothes"]["main"] != 0 else unknown,
        "subs": [ val for sublist in get_subs(loadout["clothes"]["subs"]) for val in sublist ]
    }
    shoes = {
        "gear": ac.execute("""
        SELECT row_to_json(shoes) FROM shoes WHERE id = %s;
        """, (loadout["shoes"]["gear_id"],)).fetchone(),
        "main": ac.execute(ab_query, (loadout["shoes"]["main"],)).fetchone()[0] if loadout["shoes"]["main"] != 0 else unknown,
        "subs": [ val for sublist in get_subs(loadout["shoes"]["subs"]) for val in sublist ]
    }
    return {
        "main": weapon_set[0],
        "sub": weapon_set[1],
        "special": weapon_set[2],
        "head": head,
        "clothes": clothes,
        "shoes": shoes
    }

def generate_image(loadout: dict):
    head_coords = {
        "main": (153, 118),
        "subs": [
            (189, 127),
            (217, 127),
            (246, 127)
        ]
    }
    clothes_coords = {
        "main": (298, 118),
        "subs": [
            (334, 127),
            (363, 127),
            (391, 127)
        ]
    }
    shoe_coords = {
        "main": (443, 118),
        "subs": [
            (479, 127),
            (508, 127),
            (536, 127)
        ]
    }
    coord_map = {
        "head": head_coords,
        "clothes": clothes_coords,
        "shoes": shoe_coords
    }
    base = Image.open("../assets/img/loadout_base.png")

    sub_wep = Image.open(loadout["sub"]["image"]).resize((32,32), Image.ANTIALIAS)
    base.paste(sub_wep, (27, 116), sub_wep)
    special_wep = Image.open(loadout["special"]["image"]).resize((32,32), Image.ANTIALIAS)
    base.paste(special_wep, (78, 116), special_wep)

    for gear in ["head", "clothes", "shoes"]:
        main = Image.open(loadout[gear]["main"]["image"]).resize((32,32), Image.ANTIALIAS)
        base.paste(main, coord_map[gear]["main"], main)
        for index, sub in enumerate(loadout[gear]["subs"]):
            sub = Image.open(sub["image"]).resize((24,24), Image.ANTIALIAS)
            base.paste(sub, coord_map[gear]["subs"][index], sub)

    return base