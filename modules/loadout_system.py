"""Module contaning all loadout-related functionality of the bot."""
import discord
from discord.ext import commands
from bin import decoder
from bin.create_asset_db import AssetDB
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, select

class Loadout(commands.Cog):
    """Module containing all loadout-related functionality of the bot."""

    def __init__(self, client):
        """Initialize the class."""
        self.client = client

    def parse_loadout_string(self, loadout_string: str = None):
        """Convert the loadout string into usable data for generation."""
        if loadout_string is None:
            raise ValueError("Loadout string not specified.")

        loadout = decoder.decode(loadout_string)

        weapon = AssetDB.c.execute(
            select([AssetDB.weapons_table]).where(AssetDB.weapons_table.c.class_id == loadout["set"] and AssetDB.weapons_table.c.loadout_ink_id == loadout["weapon"])
        ).fetchone()
