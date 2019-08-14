# Core Language Imports

from PIL import Image

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
        "main": ac.execute(ab_query, (loadout["head"]["main"],)).fetchone() if loadout["head"]["main"] != 0 else unknown,
        "subs": get_subs(loadout["head"]["subs"])
    }
    clothes = {
        "gear": ac.execute("""
        SELECT row_to_json(clothing) FROM clothing WHERE id = %s;
        """, (loadout["clothes"]["gear_id"],)).fetchone(),
        "main": ac.execute(ab_query, (loadout["clothes"]["main"],)).fetchone() if loadout["clothes"]["main"] != 0 else unknown,
        "subs": get_subs(loadout["clothes"]["subs"])
    }
    shoes = {
        "gear": ac.execute("""
        SELECT row_to_json(shoes) FROM shoes WHERE id = %s;
        """, (loadout["shoes"]["gear_id"],)).fetchone(),
        "main": ac.execute(ab_query, (loadout["shoes"]["main"],)).fetchone() if loadout["shoes"]["main"] != 0 else unknown,
        "subs": get_subs(loadout["shoes"]["subs"])
    }
    return {
        "main": weapon_set[0],
        "sub": weapon_set[1],
        "special": weapon_set[2],
        "head": head,
        "clothes": clothes,
        "shoes": shoes
    }

