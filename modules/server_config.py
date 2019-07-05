"""Module contining all server configurations for the bot (i.e. custom prefixes)."""
import logging
import json

import discord
from discord.ext import commands

from sqlalchemy import select
from core import DBHandler


class PrefixDBHandler(DBHandler):
    """Manages Database connections for the module."""

    def __init__(self):
        """Init PrefixDBHandler."""
        super().__init__()
        self.prefix_table = self.get_table("main", "prefix")

    def get_server_prefix(self, ctx):
        """Retrieve a server's prefix."""
        return self.get_db("main").execute(
            select([self.prefix_table]). \
            where(self.prefix_table.columns["server_id"] == ctx.message.guild.id)
        ).fetchone()

    def insert_server_prefix(self, ctx, prefix):
        """Insert a new server prefix into the database."""
        return self.get_db("main").execute(
            self.prefix_table. \
            insert(None). \
            values(server_id=ctx.message.guild.id, prefix=prefix)
        )

    def update_server_prefix(self, ctx, prefix):
        """Update a server's prefix."""
        return self.get_db("main").execute(
            self.prefix_table. \
            update(None). \
            where(self.prefix_table.columns["server_id"] == ctx.message.guild.id). \
            values(prefix=prefix)
        )

    def delete_server_prefix(self, ctx):
        """Delete a server's prefix from the database."""
        return self.get_db("main").execute(
            self.prefix_table. \
            delete(None). \
            where(self.prefix_table.columns["server_id"] == ctx.message.guild.id)
         )


class ServerConfig(commands.Cog, PrefixDBHandler):
    """Contains all server-configuraton related functionality of the bot. Documented in: `pr.config help`"""

    def __init__(self, client):
        """Init the class."""
        super().__init__()
        self.client = client

    @commands.has_permissions(administrator=True)
    @commands.group(case_insensitive=True)
    async def config(self, ctx):
        """Configure command group. Does nothing on it's own."""

    @config.command()
    async def set_prefix(self, ctx, prefix: str = None):
        """
        Set the bot's prefix within the server. By default, it is 'pr.', and it also responds to being @ mentioned.

        Parameters:
            - Prefix: The prefix to be set.

        """
        if prefix is None:
            message = "Command failed - No prefix specified."

        else:
            if self.get_server_prefix(ctx) is None:
                self.insert_server_prefix(ctx, prefix)
            else:
                self.update_server_prefix(ctx, prefix)
            message = f"Your prefix has been set to `{prefix}`."

        await ctx.send(message)

    @config.command()
    async def reset_prefix(self, ctx):
        """Reset the bot's prefix within the server. Will ask you to confirm the reset."""
        prefix = self.get_server_prefix(ctx)

        if prefix is not None:
            await ctx.send(
                f"Your current prefix is: `{prefix[1]}`.\n\nAre you sure you wish to reset the bot's prefix to `{CONFIG['prefix']}`? (Y/N)"
            )
            confirm = await self.client.wait_for(
                "message", check=lambda m: m.author == ctx.message.author
            )

            if confirm.content.lower() == "y":
                self.delete_server_prefix(ctx)
                message = "Understood. Your prefix has been reset."
            else:
                message = "Understood. Aborting reset."

        else:
            message = "Command failed - prefix is already set to default."

        await ctx.send(message)

    @config.command()
    async def help(self, ctx):
        """Config command documentation."""
        embed = discord.Embed(
            title=f"Project Prismarine - {__class__.__name__} Documentation",
            color=discord.Color.dark_red()
        )

        for command in self.walk_commands():
            embed.add_field(
                name=ctx.prefix + command.qualified_name, value=command.help
            )

        await ctx.send(embed=embed)


with open("config.json", "r") as infile:
    CONFIG = json.load(infile)


def setup(client):
    """Add the module to the bot."""
    client.add_cog(ServerConfig(client))
    logging.info("ServerConfig Module Online.")
