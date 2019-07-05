"""Module that stores all weapons from Splatoon 2."""
# yapf: disable

from sqlalchemy import Table, Column, Integer, String
from assets.data import abilities, clothing, headgear, shoes, specials, subs, weapons
from core import DBHandler

class AssetDB(DBHandler):
    """Class containing all tables with assets for the bot."""

    def __init__(self):
        """Create the asset.db."""
        super().__init__()
        self.get_meta("assets").drop_all(bind=self.get_db("assets"))
        self.reload_meta("assets")

        self.abilities_table = Table("abilities", self.get_meta("assets"), Column("id", Integer, primary_key=True),
            Column("name", String),
            Column("image", String))

        self.clothing_table = Table("clothing", self.get_meta("assets"), Column("id", Integer, primary_key=True),
            Column("name", String),
            Column("image", String),
            Column("ablilty", String),
            Column("brand", String),
            Column("splatnet", Integer))

        self.headgear_table = Table("headgear", self.get_meta("assets"), Column("id", Integer, primary_key=True),
            Column("name", String),
            Column("image", String),
            Column("ablilty", String),
            Column("brand", String),
            Column("splatnet", Integer))

        self.shoes_table = Table("shoes", self.get_meta("assets"), Column("id", Integer, primary_key=True),
            Column("name", String),
            Column("image", String),
            Column("ablilty", String),
            Column("brand", String),
            Column("splatnet", Integer))

        self.specials_table = Table("specials", self.get_meta("assets"), Column("id", Integer, primary_key=True),
            Column("name", String),
            Column("image", String))

        self.subs_table = Table("subs", self.get_meta("assets"), Column("id", Integer, primary_key=True),
            Column("name", String),
            Column("image", String),
            Column("cost", Integer))

        self.weapons_table = Table("weapons", self.get_meta("assets"), Column("id", Integer, primary_key=True),
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

        self.get_meta("assets").create_all(bind=self.get_db("assets"))

    def insert_assets(self):
        """Insert weapons, subs, specials, and abilities into the asset database."""
        for ability in abilities:
            status(f"Inserting: 'abilities': {ability['name']}...")
            ins = self.abilities_table.insert(None).values(id=ability["id"],
                name=ability["name"],
                image="assets/img/abilities/"+ability["image"][28:])
            self.get_db("assets").execute(ins)

        for item in clothing:
            status(f"Inserting: 'clothing': '{item['name']}'...")
            ins = self.clothing_table.insert(None).values(id=item["id"],
                name=item["name"],
                image="assets/img/clothing/"+item["image"][34:],
                ablilty=item["main"],
                brand=item["brand"],
                splatnet=item["splatnet"])
            self.get_db("assets").execute(ins)

        for item in headgear:
            status(f"Inserting: 'headgear': '{item['name']}'...")
            ins = self.headgear_table.insert(None).values(id=item["id"],
                name=item["name"],
                image="assets/img/headgear/"+item["image"][31:],
                ablilty=item["main"],
                brand=item["brand"],
                splatnet=item["splatnet"])
            self.get_db("assets").execute(ins)

        for item in shoes:
            status(f"Inserting: 'shoes': '{item['name']}'...")
            ins = self.shoes_table.insert(None).values(id=item["id"],
                name=item["name"],
                image="assets/img/shoes/"+item["image"][32:],
                ablilty=item["main"],
                brand=item["brand"],
                splatnet=item["splatnet"])
            self.get_db("assets").execute(ins)

        for special in specials:
            status(f"Inserting: 'specials': {special['name']}...")
            ins = self.specials_table.insert(None).values(
                name=special["name"],
                image="assets/img/specials/"+special["image"][28:])
            self.get_db("assets").execute(ins)

        for sub in subs:
            status(f"Inserting: 'subs': {sub['name']}...")
            ins = self.subs_table.insert(None).values(
                name=sub["name"],
                image="assets/img/subs/"+sub["image"][28:],
                cost=sub["cost"])
            self.get_db("assets").execute(ins)

        for weapon_class in weapons:
            for weapon in weapon_class["weapons"]:
                status(f"Inserting: 'weapons': {weapon_class['type']}: '{weapon['name']}'...")
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
                self.get_db("assets").execute(ins)


def status(msg):
    """Print message in status format."""
    print('\033[K\x1b[2K\r' + msg, end='\r')


def main():
    """Create and insert assets into the DATABASE."""
    asset_db = AssetDB()
    asset_db.insert_assets()
    status("Completed!")

if __name__ == "__main__":
    main()
