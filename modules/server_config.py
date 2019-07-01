"""Module contining all server configurations for the bot (i.e. custom prefixes)."""
import logging
import json
import discord
from discord.ext import commands
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, select


class DBcManager:
    """Manages Database connections for the module."""

    db = create_engine("sqlite:///main.db")
    metadata = MetaData(db)
    prefix_table = Table(
        "prefix", metadata, Column("server_id", Integer, primary_key=True),
        Column("prefix", String)
    )

    metadata.create_all()
    c = db.connect()

    @classmethod
    def get_server_prefix(cls, ctx):
        """Retrieve a server's prefix."""
        return cls.c.execute(
            select(
                [cls.prefix_table]
            ).where(cls.prefix_table.c.server_id == ctx.message.guild.id)
        ).fetchone()

    @classmethod
    def insert_server_prefix(cls, ctx, prefix):
        """Insert a new server prefix into the database."""
        return cls.c.execute(
            cls.prefix_table.insert(None).values(
                server_id=ctx.message.guild.id, prefix=prefix
            )
        )

    @classmethod
    def update_server_prefix(cls, ctx, prefix):
        """Update a server's prefix."""
        return cls.c.execute(
            cls.prefix_table.update(None).where(
                cls.prefix_table.c.server_id == ctx.message.guild.id
            ).values(prefix=prefix)
        )

    @classmethod
    def delete_server_prefix(cls, ctx):
        """Delete a server's prefix from the database."""
        return cls.c.execute(
            cls.prefix_table.delete(None).where(
                cls.prefix_table.c.server_id == ctx.message.guild.id
            )
        )


class ServerConfig(commands.Cog, DBcManager):
    """Contains all server-configuraton related functionality of the bot."""

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