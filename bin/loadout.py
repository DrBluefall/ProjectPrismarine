"""Script to make dealing with loadouts in cogs easier."""
from sqlalchemy import create_engine, MetaData, select, and_
from PIL import Image
import decoder
from pprint import pprint

class Loadout:
    """Module containing all loadout-related functionality of the bot."""

    def __init__(self):
        """Initialize the class."""
        self.dbs = {
            'assets': {
                'db': create_engine("sqlite:///assets/assets.db"),
                'meta': MetaData()
            },
            'main': {
                'db': create_engine("sqlite:///main.db"),
                'meta': MetaData()
            }
        }
        self.dbs['assets']['meta'].reflect(self.dbs['assets']['db'])
        self.dbs['main']['meta'].reflect(self.dbs['main']['db'])

        self.dbs['assets']['connect'] = self.dbs['assets']['db'].connect()
        self.dbs['main']['connect'] = self.dbs['main']['db'].connect()

    def get_row(self, table, id, weapon_id=None):
        """Return row in database given table and the id."""
        asset_c = self.dbs['assets']['connect']
        if weapon_id is None:
            return asset_c.execute(
                select([table]).where(table.c.id == id)).fetchone()

        return asset_c.execute(
            select([table]).where(
                and_(table.c.class_id == id,
                     table.c.loadout_ink_id == weapon_id))).fetchone()
    
    def convert_loadout(self, raw_loadout):

        loadout = {
            "weapon": self.get_row(self.dbs['assets']['meta'].tables['weapons'], raw_loadout["class"], raw_loadout["weapon"]),
            "headgear": {
                "gear": self.get_row(self.dbs['assets']['meta'].tables['headgear'], raw_loadout['headgear']['gear']),
                "subs": [
                    self.get_row(self.dbs['assets']['meta'].tables['abilities'], raw_loadout['headgear']['subs'][0]),
                    self.get_row(self.dbs['assets']['meta'].tables['abilities'], raw_loadout['headgear']['subs'][1]),
                    self.get_row(self.dbs['assets']['meta'].tables['abilities'], raw_loadout['headgear']['subs'][2]),
                ],
                "main": self.get_row(self.dbs['assets']['meta'].tables['abilities'], raw_loadout['headgear']['main'])
            },
            "clothing": {
                "gear": self.get_row(self.dbs['assets']['meta'].tables['clothing'], raw_loadout['clothing']['gear']),
                "subs": [
                    self.get_row(self.dbs['assets']['meta'].tables['abilities'], raw_loadout['clothing']['subs'][0]),
                    self.get_row(self.dbs['assets']['meta'].tables['abilities'], raw_loadout['clothing']['subs'][1]),
                    self.get_row(self.dbs['assets']['meta'].tables['abilities'], raw_loadout['clothing']['subs'][2]),
                ],
                "main": self.get_row(self.dbs['assets']['meta'].tables['abilities'], raw_loadout['clothing']['main'])
            },
            "shoes": {
                "gear": self.get_row(self.dbs['assets']['meta'].tables['shoes'], raw_loadout['shoes']['gear']),
                "subs": [
                    self.get_row(self.dbs['assets']['meta'].tables['abilities'], raw_loadout['shoes']['subs'][0]),
                    self.get_row(self.dbs['assets']['meta'].tables['abilities'], raw_loadout['shoes']['subs'][1]),
                    self.get_row(self.dbs['assets']['meta'].tables['abilities'], raw_loadout['shoes']['subs'][2]),
                ],
                "main": self.get_row(self.dbs['assets']['meta'].tables['abilities'], raw_loadout['shoes']['main'])
            },
        }

        return loadout

    def generate_loadout_image(self, loadout):
        """Generate an image from provided loadout data."""


"""
        # Head
        image.paste(main, box=(154, 117), mask=main)
        image.paste(ability, box=(190, 126), mask=ability)
        image.paste(ability, box=(219, 126), mask=ability)
        image.paste(ability, box=(247, 126), mask=ability)
        image.paste(hat, box=(170, 29), mask=hat)

        # Shirt
        image.paste(main, box=(299, 117), mask=main)
        image.paste(ability, box=(335, 126), mask=ability)
        image.paste(ability, box=(364, 126), mask=ability)
        image.paste(ability, box=(392, 126), mask=ability)
        image.paste(shirt, box=(315, 29), mask=shirt)

        # Shoes
        image.paste(main, box=(444, 117), mask=main)
        image.paste(ability, box=(480, 126), mask=ability)
        image.paste(ability, box=(508, 126), mask=ability)
        image.paste(ability, box=(537, 126), mask=ability)
        image.paste(shoe, box=(460, 29), mask=shoe)

        # Weapon
        image.paste(sub, box=(28, 117), mask=sub)
        image.paste(special, box=(78, 117), mask=special)
        image.paste(wep, box=(23, 29), mask=wep)
"""

if __name__ == "__main__":
    pprint(Loadout().convert_loadout(decoder.decode("0000002054c006906a0071dab")))