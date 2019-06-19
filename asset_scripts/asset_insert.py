"""Module that stores all weapons from Splatoon 2."""
import all_weapons, subs, specials, clothing, shoes, headgear, gear_abilities
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, select


class asset_database:
    """Class containing all tables with assets for the bot."""

    engine = create_engine("sqlite:///assets.db")
    metadata = MetaData(engine)
    weapons_table = Table(
        "weapons",
        metadata,
        Column("weapon_id", Integer, primary_key=True),
        Column("loadout_ink_id", Integer),
        Column("wep_class", String),
        Column("class_id", Integer),
        Column("main_name", String),
        Column("sub", String),
        Column("special", String),
        Column("special_cost", String),
        Column("price", String),
        Column("level", Integer),
        Column("image", String)
    )

    headgear_table = Table(
        "headgear",
        metadata,
        Column("name", String),
        Column("main_ablilty", String),
        Column("brand", String),
        Column("id", Integer, primary_key=True)
    )

    clothing_table = Table(
        "clothing",
        metadata,
        Column("name", String),
        Column("main_ablilty", String),
        Column("brand", String),
        Column("id", Integer, primary_key=True)
    )

    shoes_table = Table(
        "shoes",
        metadata,
        Column("name", String),
        Column("main_ablilty", String),
        Column("brand", String),
        Column("id", Integer, primary_key=True)
    )

    sub_table = Table(
        "sub_table",
        metadata,
        Column("name", String),
        Column("image", String),
        Column("cost", Integer),
        Column("id", Integer, primary_key=True)
    )

    special_table = Table(
        "special_table",
        metadata,
        Column("name", String),
        Column("image", String),
        Column("id", Integer, primary_key=True)
    )

    ability_table = Table(
        "ability_table",
        metadata,
        Column("name", String),
        Column("image", String),
        Column("id", Integer, primary_key=True)
    )

    metadata.create_all()
    c = engine.connect()


def asset_inserter():
    """Insert weapons, subs, specials, and abilities into the asset database."""
    for weapon_class in all_weapons.weapons:
        for key in weapon_class:
            if key == "weapons":
                for weapon in weapon_class["weapons"]:
                    image = weapon["image"][29:]
                    ins = asset_database.weapons_table.insert(None).values(
                        loadout_ink_id=weapon["id"],
                        wep_class=weapon["class"],
                        class_id=weapon_class["id"],
                        main_name=weapon["name"],
                        sub=weapon["sub"],
                        special=weapon["special"],
                        special_cost=weapon["specialCost"],
                        price=weapon["price"],
                        level=weapon["level"],
                        image=image
                    )

                    asset_database.c.execute(ins)
                    print(f"{weapon['name']} inserted!")
    for item in headgear.headgear:
        image = item["image"][31:]
        ins = asset_database.headgear_table.insert(None).values(
            id=item["splatnet"],
            name=item["name"],
            brand=item["brand"],
            main_ablilty=item["main"]
        )

        asset_database.c.execute(ins)
        print(f"{item['name']} inserted!")
    
    for item in clothing.clothes:
        image = item["image"][34:]
        ins = asset_database.clothing_table.insert(None).values(
            id=item["splatnet"],
            name=item["name"],
            brand=item["brand"],
            main_ablilty=item["main"]
        )

        asset_database.c.execute(ins)
        print(f"{item['name']} inserted!")
    
    for item in shoes.shoes:
        image = item["image"][32:]
        ins = asset_database.shoes_table.insert(None).values(
            id=item["splatnet"],
            name=item["name"],
            brand=item["brand"],
            main_ablilty=item["main"]
        )

        asset_database.c.execute(ins)
        print(f"{item['name']} inserted!")

    for sub in subs.subs:
        ins = asset_database.sub_table.insert(None).values(
            name=sub["name"],
            image=sub["image"][28:],
            cost=sub["cost"]
        )

        asset_database.c.execute(ins)
        print(f"{sub['name']} inserted!")
    
    for special in specials.specials:
        ins = asset_database.sub_table.insert(None).values(
            name=special["name"],
            image=special["image"][28:]
        )

        asset_database.c.execute(ins)
        print(f"{special['name']} inserted!")
    
    for ability in gear_abilities.skills:
        ins = asset_database.ability_table.insert(None).values(
            name=ability["name"],
            image=ability["image"],
            id=ability["id"]
        )

        asset_database.c.execute(ins)
        print(f"{ability['name']} inserted!")


if __name__ == "__main__":
    asset_inserter()
