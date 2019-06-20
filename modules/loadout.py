"""Module contaning all loadout-related functionality of the bot."""
import logging
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, select, and_
from pprint import pprint
import discord
from discord.ext import commands

from bin import decoder


def setup(client):
    """Add the module to the bot."""
    client.add_cog(Loadout(client))
    logging.info("%s Module Online.", Loadout.__name__)


class Loadout(commands.Cog):
    """Module containing all loadout-related functionality of the bot."""

    def __init__(self, client):
        """Initialize the Loadout Cog."""
        self.client = client

        asset_db = create_engine("sqlite:///assets/assets.db")
        self.asset_metadata = MetaData()
        self.asset_metadata.reflect(asset_db)
        main_db = create_engine("sqlite:///ProjectPrismarine.db")
        self.main_metadata = MetaData()
        self.main_metadata.reflect(main_db)

        self.ac = asset_db.connect()
        self.mc = main_db.connect()

    @commands.group(case_insensitive=True, ignore_extra=True)
    async def loadout(self, ctx):
        pass

    def parse_string(self, string):
        """Convert the loadout string into usable data for generation."""
        return decoder.decode(string)

    def get_row(self, table, id, weapon_id=None):
        if weapon_id is None:
            return self.ac.execute(select([table]).where(table.ac.id == id)).fetchone()

        return self.ac.execute(select([table]).where(and_(table.ac.class_id == id, table.ac.loadout_ink_id == weapon_id))).fetchone()
