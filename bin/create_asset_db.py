"""Module that stores all weapons from Splatoon 2."""
# yapf: disable
# pylint: disable=all

from sqlalchemy import create_engine, MetaData
from sqlalchemy import Table, Column, Integer, String
from assets.data import abilities, clothing, headgear, shoes, specials, subs, weapons

class AssetDB:
    """Class containing all tables with assets for the bot."""

    def __init__(self):
        """Create the asset.db."""
        engine = create_engine("sqlite:///assets/assets.db")
        metadata = MetaData(engine)

        self.abilities_table = Table("abilities", metadata, Column("id", Integer, primary_key=True),
            Column("name", String),
            Column("image", String))

        self.clothing_table = Table("clothing", metadata, Column("id", Integer, primary_key=True),
            Column("name", String),
            Column("image", String),
            Column("ablilty", String),
            Column("brand", String),
            Column("splatnet", Integer))

        self.headgear_table = Table("headgear", metadata, Column("id", Integer, primary_key=True),
            Column("name", String),
            Column("image", String),
            Column("ablilty", String),
            Column("brand", String),
            Column("splatnet", Integer))

        self.shoes_table = Table("shoes", metadata, Column("id", Integer, primary_key=True),
            Column("name", String),
            Column("image", String),
            Column("ablilty", String),
            Column("brand", String),
            Column("splatnet", Integer))

        self.specials_table = Table("specials", metadata, Column("id", Integer, primary_key=True),
            Column("name", String),
            Column("image", String))

        self.subs_table = Table("subs", metadata, Column("id", Integer, primary_key=True),
            Column("name", String),
            Column("image", String),
            Column("cost", Integer))

        self.weapons_table = Table("weapons", metadata, Column("id", Integer, primary_key=True),
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

        self.c = engine.connect()

    def insert_assets(self):
        """Insert weapons, subs, specials, and abilities into the asset database."""
        print("\nInserting: 'abilities'...")
        for ability in abilities:
            print(f"\tInserting: {ability['name']}...")
            ins = self.abilities_table.insert(None).values(id=ability["id"],
                name=ability["name"],
                image="assets/img/abilities/"+ability["image"][28:])
            self.c.execute(ins)

        print("\nInserting: 'clothing'...")
        for item in clothing:
            print(f"\tInserting: '{item['name']}'...")
            ins = self.clothing_table.insert(None).values(id=item["id"],
                name=item["name"],
                image="assets/img/clothing/"+item["image"][34:],
                ablilty=item["main"],
                brand=item["brand"],
                splatnet=item["splatnet"])
            self.c.execute(ins)

        print("\nInserting: 'headgear'...")
        for item in headgear:
            print(f"\tInserting: '{item['name']}'...")
            ins = self.headgear_table.insert(None).values(id=item["id"],
                name=item["name"],
                image="assets/img/headgear/"+item["image"][31:],
                ablilty=item["main"],
                brand=item["brand"],
                splatnet=item["splatnet"])
            self.c.execute(ins)

        print("\nInserting: 'shoes'...")
        for item in shoes:
            print(f"\tInserting: '{item['name']}'...")
            ins = self.shoes_table.insert(None).values(id=item["id"],
                name=item["name"],
                image="assets/img/shoes/"+item["image"][32:],
                ablilty=item["main"],
                brand=item["brand"],
                splatnet=item["splatnet"])
            self.c.execute(ins)

        print("\nInserting: 'specials'...")
        for special in specials:
            print(f"\tInserting: {special['name']}...")
            ins = self.specials_table.insert(None).values(
                name=special["name"],
                image="assets/img/specials/"+special["image"][28:])
            self.c.execute(ins)

        print("\nInserting: 'subs'...")
        for sub in subs:
            print(f"\tInserting: {sub['name']}...")
            ins = self.subs_table.insert(None).values(
                name=sub["name"],
                image="assets/img/subs/"+sub["image"][28:],
                cost=sub["cost"])
            self.c.execute(ins)

        print("\nInserting: 'weapons'...")
        for weapon_class in weapons:
            print(f"\tInserting: {weapon_class['type']}...")
            for weapon in weapon_class["weapons"]:
                print(f"\t\tInserting: '{weapon['name']}'...")
                ins = self.weapons_table.insert(None).values(
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
                self.c.execute(ins)

def main():
    """Create and insert assets into the DATABASE."""
    DATABASE = AssetDB()
    DATABASE.insert_assets()

if __name__ == "__main__":
    main()
