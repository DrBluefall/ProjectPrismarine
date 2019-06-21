"""Module contaning all loadout-related functionality of the bot."""
from sqlalchemy import create_engine, MetaData, select, and_
from . import decoder


class Loadout:
    """Module containing all loadout-related functionality of the bot."""

    def __init__(self):
        self.dbs = {
            'assets': {
                'db': create_engine("sqlite:///assets/assets.db"),
                'meta': MetaData()
            },
            'main': {
                'db': create_engine("sqlite://ProjectPrismarine.db"),
                'meta': MetaData()
            }
        }
        self.dbs['assets']['meta'].reflect(self.dbs['assets']['db'])
        self.dbs['main']['meta'].reflect(self.dbs['main']['db'])

        self.dbs['assets']['connect'] = self.dbs['assets']['db'].connect()
        self.dbs['main']['connect'] = self.dbs['main']['db'].connect()

    async def loadout(self, string):
        """Loadout cog. Handles all loadout-related functionality in the bot."""
        string = decoder.decode(string)

    def get_row(self, table, id, weapon_id=None):
        """Return row in database given table and the id."""
        asset_c = self.dbs['assets']['connect']
        if weapon_id is None:
            return asset_c.execute(
                select([table]).where(table.asset_c.id == id)).fetchone()

        return asset_c.execute(
            select([table]).where(
                and_(table.asset_c.class_id == id,
                     table.asset_c.loadout_ink_id == weapon_id))).fetchone()

    def generate_loadout_image(self):
        pass
