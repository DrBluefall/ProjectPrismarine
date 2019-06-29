"""Module containing the MyModule cog."""

# ... Anything starting with "..." should be replaced
# All comments (including these 2) should be removed entirely

import logging
import discord
from discord.ext import commands


class MyModule(commands.Cog):
    """Contains all MyModule commands."""

    # ... The order of methods in these classes are:
    # ... - Command groups
    # ... - Subcommands (in same order as command groups)
    # ... - Help subcommand
    # ... - Module commands
    # ... - Other discord.ext methods
    # ... - Normal methods
    # ... - Class methods
    # ... - Static methods

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

    @module_group.command()
    async def help(self, ctx):
        """Mymodule command documentation."""
        embed = discord.Embed(
            title=f"Project Prismarine - {__class__.__name__} Documentation",
            color=discord.Color.dark_red()
        )
        for command in self.walk_commands():
            embed.add_field(
                name=ctx.prefix + command.qualified_name, value=command.help
            )
        await ctx.send(embed=embed)

    @commands.command()
    async def mycommand(self, ctx, name_user, *, nickname: str):
        """... Write module command docstring."""
        # ... Write module command


def setup(client):
    """Add the module to the bot."""
    client.add_cog(MyModule(client))
    logging.info("MyModule Module Online.")
