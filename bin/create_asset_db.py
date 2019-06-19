"""Module that stores all weapons from Splatoon 2."""
# pylint: disable=all
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from assets.data import abilities, clothing, headgear, shoes, specials, subs, weapons

class AssetDB:
    """Class containing all tables with assets for the bot."""

    engine = create_engine("sqlite:///assets/assets.db")
    metadata = MetaData(engine)

    abilities_table = Table("abilities", metadata, Column("id", Integer, primary_key=True),
        Column("name", String),
        Column("image", String))

    clothing_table = Table("clothing", metadata, Column("id", Integer, primary_key=True),
        Column("name", String),
        Column("image", String),
        Column("ablilty", String),
        Column("brand", String))

    headgear_table = Table("headgear", metadata, Column("id", Integer, primary_key=True),
        Column("name", String),
        Column("image", String),
        Column("ablilty", String),
        Column("brand", String))

    shoes_table = Table("shoes", metadata, Column("id", Integer, primary_key=True),
        Column("name", String),
        Column("image", String),
        Column("ablilty", String),
        Column("brand", String))

    specials_table = Table("specials", metadata, Column("id", Integer, primary_key=True),
        Column("name", String),
        Column("image", String))

    subs_table = Table("subs", metadata, Column("id", Integer, primary_key=True),
        Column("name", String),
        Column("image", String),
        Column("cost", Integer))

    weapons_table = Table("weapons", metadata, Column("id", Integer, primary_key=True),
        Column("name", String),
        Column("image", String),
        Column("loadout_ink_id", Integer),
        Column("weapon_class", String),
        Column("class_id", Integer),
        Column("sub", String),
        Column("special", String),
        Column("special_cost", String),
        Column("level", Integer),
        Column("cost", String))

    metadata.drop_all()
    metadata.create_all()
    c = engine.connect()

    @classmethod
    def asset_inserter(cls):
        """Insert weapons, subs, specials, and abilities into the asset database."""
        for ability in abilities:
            ins = cls.abilities_table.insert(None).values(id=ability["id"],
                name=ability["name"],
                image="assets/img/abilities/"+ability["image"][28:])

            cls.c.execute(ins)
            print(f"Inserted: {ability['name']}")

        for item in clothing:
            ins = cls.clothing_table.insert(None).values(id=item["splatnet"],
                name=item["name"],
                image="assets/img/clothing/"+item["image"][34:],
                ablilty=item["main"],
                brand=item["brand"])

            cls.c.execute(ins)
            print(f"Inserted: '{item['name']}'")

        for item in headgear:
            ins = cls.headgear_table.insert(None).values(id=item["splatnet"],
                name=item["name"],
                image="assets/img/headgear/"+item["image"][31:],
                ablilty=item["main"],
                brand=item["brand"])

            cls.c.execute(ins)
            print(f"Inserted: '{item['name']}'")

        for item in shoes:
            ins = cls.shoes_table.insert(None).values(id=item["splatnet"],
                name=item["name"],
                image="assets/img/shoes/"+item["image"][32:],
                ablilty=item["main"],
                brand=item["brand"])

            cls.c.execute(ins)
            print(f"Inserted: '{item['name']}'")

        for special in specials:
            ins = cls.specials_table.insert(None).values(
                name=special["name"],
                image="assets/img/specials/"+special["image"][28:])

            cls.c.execute(ins)
            print(f"Inserted: {special['name']}")

        for sub in subs:
            ins = cls.subs_table.insert(None).values(
                name=sub["name"],
                image="assets/img/subs/"+sub["image"][28:],
                cost=sub["cost"])

            cls.c.execute(ins)
            print(f"Inserted: {sub['name']}")

        for weapon_class in weapons:
            for key in weapon_class:
                if key != "weapons":
                    continue

                for weapon in weapon_class["weapons"]:
                    ins = cls.weapons_table.insert(None).values(
                        name=weapon["name"],
                        image="assets/img/weapons/"+weapon["image"][29:],
                        loadout_ink_id=weapon["id"],
                        weapon_class=weapon["class"],
                        class_id=weapon_class["id"],
                        sub=weapon["sub"],
                        special=weapon["special"],
                        special_cost=weapon["specialCost"],
                        level=weapon["level"],
                        cost=weapon["price"])

                    cls.c.execute(ins)
                    print(f"Inserted: '{weapon['name']}'")


if __name__ == "__main__":
    AssetDB.asset_inserter()
