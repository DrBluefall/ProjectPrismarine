"""Module contining all server configurations for the bot (i.e. custom prefixes)."""
import logging
import json
from discord.ext import commands
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, select


class DBcManager:

    db = create_engine("sqlite:///ProjectPrismarine.db")
    metadata = MetaData(db)
    prefix_table = Table("prefix", metadata,
                         Column("server_id", Integer, primary_key=True),
                         Column("prefix", String))

    metadata.create_all()
    c = db.connect()

    @classmethod
    def get_server_prefix(cls, ctx):
        return cls.c.execute(
            select([cls.prefix_table]).where(cls.prefix_table.c.server_id ==
                                             ctx.message.guild.id)).fetchone()

    @classmethod
    def insert_server_prefix(cls, ctx, prefix):
        return cls.c.execute(
            cls.prefix_table.insert(None).values(
                server_id=ctx.message.guild.id, prefix=prefix))

    @classmethod
    def update_server_prefix(cls, ctx, prefix):
        return cls.c.execute(
            cls.prefix_table.update(None).where(
                cls.prefix_table.c.server_id == ctx.message.guild.id).values(
                    prefix=prefix))

    @classmethod
    def delete_server_prefix(cls, ctx):
        return cls.c.execute(
            cls.prefix_table.delete(None).where(
                cls.prefix_table.c.server_id == ctx.message.guild.id))


class ServerConfig(commands.Cog, DBcManager):
    """Module conatining all server-configuraton related functionality of the bot."""

    def __init__(self, client):
        """Initialize the class."""
        super().__init__()
        self.client = client

    @commands.has_permissions(administrator=True)
    @commands.group(case_insensitive=True)
    async def config(self, ctx):
        """Configuration command group. Does nothing on it's own."""

    @config.command()
    async def set_prefix(self, ctx, prefix: str = None):
        """Set the bot's prefix within the server. By default, it is 'pr.', and it also responds to being @ mentioned."""
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
        """Reset the bot's prefix within the server."""
        prefix = self.get_server_prefix(ctx)

        if prefix is not None:
            await ctx.send(
                f"Your current prefix is: `{prefix[1]}`.\n\nAre you sure you wish to reset the bot's prefix to `{CONFIG['prefix']}`? (Y/N)"
            )
            confirm = await self.client.wait_for(
                "message", check=lambda m: m.author == ctx.message.author)

            if confirm.content.lower() == "y":
                self.delete_server_prefix(ctx)
                message = "Understood. Your prefix has been reset."
            else:
                message = "Understood. Aborting reset."

        else:
            message = "Command failed - prefix is already set to default."

        await ctx.send(message)


with open("config.json", "r") as infile:
    CONFIG = json.load(infile)


def setup(client):
    """Add the module to the bot."""
    client.add_cog(ServerConfig(client))
    logging.info("%s Module Online.", ServerConfig.__name__)
