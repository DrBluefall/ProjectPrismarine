"""Module containing documentation from the bot."""
import os
import re
import importlib
import logging
import discord
from discord.ext import commands

def setup(client):
    """Add the module to the bot."""
    client.add_cog(Help(client))
    logging.info("Help Module online.")

class Help(commands.Cog):
    """Module containing documentation for the bot."""

    def __init__(self, client):
        """Initialize the class."""
        self.client = client
        self.client.remove_command("help")
    
    @commands.group(case_insensitive=True)
    async def help(self, ctx):
        if ctx.invoked_subcommand is not None:
            return
        embed = discord.Embed(
            title="Project Prismarine - User Manual",
            color=discord.Color.dark_red()
        )
        for module in os.listdir("./modules"):
            if re.search(r".py$", module) is not None:
                module = importlib.import_module(f"modules.{module[:-3]}")
                embed.add_field(name=f"__{module.__name__[8:]}__", value=module.__doc__, inline=True)
        
        await ctx.send(embed=embed)



            