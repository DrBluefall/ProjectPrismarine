"""Module containing the MyModule cog."""
import logging
from discord.ext import commands


class MyModule(commands.Cog):
    """Contains all MyModule commands."""

    def __init__(self, client):
        """Init the MyModule cog."""
        self.client = client

    @commands.group(case_insensitive=True)
    async def module_group(self, ctx):
        """... Write command group docstring."""
        if ctx.invoked_subcommand is not None:
            return

        # ... Write command group

    @module_group.command()
    async def subcommand(self, ctx):
        """... Write group command docstring."""
        # ... Write group command

    @commands.command()
    async def mycommand(self, ctx, name_user, *, nickname: str):
        """... Write module command docstring."""
        # ... Write module command


def setup(client):
    """Add the module to the bot."""
    client.add_cog(MyModule(client))
    logging.info("MyModule Module Online.")
