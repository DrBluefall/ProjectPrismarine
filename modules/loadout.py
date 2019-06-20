"""Module contaning all loadout-related functionality of the bot."""
import logging
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, select

import discord
from discord.ext import commands

from bin import decoder
from bin import create_asset_db

AssetDB = create_asset_db.AssetDB


def setup(client):
    """Add the module to the bot."""
    client.add_cog(Loadout(client))
    logging.info("%s Module Online.", Loadout.__name__)


class Loadout(commands.Cog):
    """Module containing all loadout-related functionality of the bot."""

    def __init__(self, client):
        """Initialize the Loadout Cog."""
        self.client = client

    @commands.group(case_insensitive=True, ignore_extra=True)
    async def loadout(self, ctx):
        pass

    @loadout.command()
    async def test(self, ctx, string = None):
        print(string)
        loadout = __class__.parse_string(string)
        print(loadout)

    def parse_string(self, string):
        """Convert the loadout string into usable data for generation."""
        if string is None:
            raise ValueError("Loadout string not specified.")

        loadout = decoder.decode(string)

        weapon = AssetDB.c.execute(
            select([AssetDB.weapons_table]).where(
                AssetDB.weapons_table.c.class_id == loadout["set"]
                and AssetDB.weapons_table.c.loadout_ink_id == loadout["weapon"]
            )).fetchone()

        headgear = {
            "gear":
            AssetDB.c.execute(
                select([AssetDB.headgear_table
                        ]).where(AssetDB.headgear_table.c.id == loadout["head"]
                                 ["gear"])).fetchone(),
            "main":
            AssetDB.c.execute(
                select([AssetDB.abilities_table
                        ]).where(AssetDB.abilities_table.c.id ==
                                 loadout["head"]["main"])).fetchone(),
            "subs": [
                AssetDB.c.execute(
                    select([AssetDB.abilities_table
                            ]).where(AssetDB.abilities_table.c.id ==
                                     loadout["head"]["subs"][1])).fetchone(),
                AssetDB.c.execute(
                    select([AssetDB.abilities_table
                            ]).where(AssetDB.abilities_table.c.id ==
                                     loadout["head"]["subs"][2])).fetchone(),
                AssetDB.c.execute(
                    select([AssetDB.abilities_table
                            ]).where(AssetDB.abilities_table.c.id ==
                                     loadout["head"]["subs"][3])).fetchone()
            ]
        }

        return {"weapoon": weapon, "headgear": headgear}
