"""Module contining all server configurations for the bot (i.e. custom prefixes)."""
import logging
import json
import discord
from discord.ext import commands
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, select

with open("config.json", "r") as infile:
    CONFIG = json.load(infile)


def setup(client):
    """Add the module to the bot."""
    client.add_cog(ServerConfig(client))
    logging.info("%s Module Online.", ServerConfig.__name__)

class ServerConfig(commands.Cog):
    """Module conatining all server-configuraton related functionality of the bot."""

    def __init__(self, client):
        """Initialize the class."""
        self.client = client
        self.db = create_engine("sqlite:///ProjectPrismarine.db")
        self.metadata = MetaData(self.db)
        self.prefix_table = Table(
            "prefix",
            self.metadata,
            Column("server_id", Integer, primary_key=True),
            Column("prefix", String)
        )
        self.metadata.create_all()
        self.c = self.db.connect()

    @commands.has_permissions(administrator=True)
    @commands.group(case_insensitive=True)
    async def config(self, ctx):
        """Configuration command group. Does nothing on it's own."""
        pass

    @config.command()
    async def set_prefix(self, ctx, prefix: str = None):
        """Set the bot's prefix within the server. By default, it is 'pr.', and it also responds to being @ mentioned."""
        if prefix is None:
            await ctx.send("Command failed - No prefix specified.")
        if self.c.execute(
            select([self.prefix_table])\
            .where(self.prefix_table.c.server_id == ctx.message.guild.id)
        ).fetchone() is None:
            self.c.execute(
                self.prefix_table.insert(None)\
                .values(server_id=ctx.message.guild.id, prefix=prefix)
            )
            await ctx.send(f"Your prefix has been set to `{prefix}`.")
        else:
            self.c.execute(
                self.prefix_table.update(None).\
                where(self.prefix_table.c.server_id == ctx.message.guild.id)\
                .values(prefix=prefix)
            )
            await ctx.send(f"Your prefix has been set to `{prefix}`.")

    @config.command()
    async def reset_prefix(self, ctx):
        """Reset the bot's prefix within the server."""
        def check(m):
            return True
        prefix = self.c.execute(
            select([self.prefix_table])\
            .where(self.prefix_table.c.server_id == ctx.message.guild.id)
            ).fetchone()
        if prefix is not None:
            await ctx.send(f"Your current prefix is: `{prefix[1]}`. \n \n Are you sure you wish to reset the bot's prefix to `{CONFIG['prefix']}`? (Y/N)")
            confirm = await self.client.wait_for("message", check=check)
            if confirm.content.lower() == "y":
                self.c.execute(
                    self.prefix_table.delete()\
                    .where(self.prefix_table.c.server_id == ctx.message.guild.id)
                )
                await ctx.send("Understood. Your prefix has been reset.")
            else:
                await ctx.send("Understood. Aborting reset.")
        else:
            await ctx.send("Command failed - prefix is already set to default.")
