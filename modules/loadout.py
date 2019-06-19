"""Module contaning all loadout-related functionality of the bot."""
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, select

import discord
from discord.ext import commands

from bin import decoder
from bin.create_asset_db import AssetDB


class Loadout(commands.Cog):
    """Module containing all loadout-related functionality of the bot."""

    def __init__(self, client):
        """Initialize the Loadout Cog."""
        self.client = client

    def parse_string(self, string: str = None):
        """Convert the loadout string into usable data for generation."""
        if string is None:
            raise ValueError("Loadout string not specified.")

        loadout = decoder.decode(string)

        weapon = AssetDB.c.execute(
            select([AssetDB.weapons_table]).where(AssetDB.weapons_table.c.class_id ==
                                                  loadout["set"] and AssetDB.weapons_table.c.loadout_ink_id == loadout["weapon"])
        ).fetchone()

        headgear = {
            "gear": AssetDB.c.execute(
                select([AssetDB.headgear_table]).where(
                    AssetDB.headgear_table.c.id == loadout["head"]["gear"])
            ).fetchone(),
            "main": AssetDB.c.execute(
                select([AssetDB.abilities_table]).where(
                    AssetDB.abilities_table.c.id == loadout["head"]["main"])
            ).fetchone(),
            "subs": [
                AssetDB.c.execute(
                    select([AssetDB.abilities_table]).where(
                        AssetDB.abilities_table.c.id == loadout["head"]["subs"][1])
                ).fetchone(),
                AssetDB.c.execute(
                    select([AssetDB.abilities_table]).where(
                        AssetDB.abilities_table.c.id == loadout["head"]["subs"][2])
                ).fetchone(),
                AssetDB.c.execute(
                    select([AssetDB.abilities_table]).where(
                        AssetDB.abilities_table.c.id == loadout["head"]["subs"][3])
                ).fetchone()
            ]
        }
