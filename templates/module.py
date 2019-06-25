"""Module containing all MyModule commands."""
import logging
from discord.ext import commands


class MyModule(commands.Cog):
    """Module containing all MyModule commands."""

    def __init__(self, client):
        """Init the MyModule cog."""
        self.client = client

    @commands.group(case_insensitive=True)
    async def module_group(self, ctx):
        """Run module group thing."""
        if ctx.invoked_subcommand is not None:
            return

        # ... Do something

    @module_group.command()
    async def subcommand(self, ctx):
        """Run group sub-command thing."""
        # ... Write group command

    @commands.command()
    async def mycommand(self, ctx, name_user, *, nickname: str):
        """Run module command thing."""
        # ... Write module command


def setup(client):
    """Add the module to the bot."""
    client.add_cog(MyModule(client))
    logging.info("MyModule Module Online.")
