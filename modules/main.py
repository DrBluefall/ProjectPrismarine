"""Module containing the main commands."""

import logging
import json
import discord
from discord.ext import commands
from sqlalchemy import select
from core import DBHandler


class Main(DBHandler, commands.Cog):
    """Contains all the main commands."""

    def __init__(self, client):
        """Init the MyModule cog."""
        super().__init__()
        self.client = client

    @commands.group(case_insensitive=True)
    async def main(self, ctx):
        """Define main command group. Does nothing on it's own."""

    @main.command()
    async def help(self, ctx):
        """Define main command documentation."""
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
    async def modules(self, ctx):
        """Client command documentation."""
        embed = discord.Embed(
            title="Project Prismarine - User Manual",
            color=discord.Color.dark_red()
        )
        for module_name, module in self.client.cogs.items():
            embed.add_field(name=module_name, value=module.description)

        await ctx.send(embed=embed)

    @commands.command()
    async def load(self, ctx, extension):
        """Load the specified module within the bot."""
        try:
            self.client.load_extension(f"modules.{extension}")
            await ctx.send(f"Module `{extension}` loaded.")
            logging.info("%s module loaded.", extension)
        except (
            commands.CommandInvokeError, commands.ExtensionNotLoaded,
            commands.ExtensionNotFound
        ) as error:
            await ctx.send(
                "Module could not be loaded. Check the console to assure that there are no errors, and that the name of the module was spelled correctly."
            )
            logging.exception("%i - %s", ctx.guild.id, error)

    @commands.command()
    async def unload(self, ctx, extension):
        """Unload the specified module within the bot."""
        try:
            self.client.unload_extension(f"modules.{extension}")
            await ctx.send(f"Module `{extension}` unloaded.")
            logging.info("%s module unloaded.", extension)
        except (
            commands.CommandInvokeError, commands.ExtensionNotLoaded,
            commands.ExtensionNotFound
        ) as error:
            await ctx.send(
                "Module could not be unloaded. Check the console to assure that there are no errors, and that the name of the module was spelled correctly."
            )
            logging.exception("%i - %s", ctx.guild.id, error)

    @commands.command()
    async def reload(self, ctx, extension):
        """Reload the specified module within the bot."""
        try:
            self.client.unload_extension(f"modules.{extension}")
            self.client.load_extension(f"modules.{extension}")
            await ctx.send(f"Module `{extension}` reloaded.")
            logging.info("%s module reloaded.", extension)
        except (
            commands.CommandInvokeError, commands.ExtensionNotLoaded,
            commands.ExtensionNotFound
        ) as error:
            await ctx.send(
                "Module could not be reloaded. Check the console to assure that there are no errors, and that the name of the module was spelled correctly."
            )
            logging.exception("%i - %s", ctx.guild.id, error)

    @commands.command()
    async def credits(self, ctx):
        """Credits the people who have contributed to the bot."""
        embed = discord.Embed(
            title="The Credits",
            description="""
                This command exists to commemorate and properly credit those who have assisted, inspired, or otherwise contributed to the creation of Project Prismarine.

                *Personal Commendations*

                :military_medal: <@274983796414349313> - For initially inspiring me to learn Python and persue Computer Science and programming in a serious manner, as well as for his open-source Splatoon bot, from which I referenced frequently in Project Prismarine's development.

                :military_medal: <@196470965402730507> - For reviewing Project Prismarine's code and general assistance in my code endeavors, and a really interesting person to talk with in general, whether the topic be programming or otherwise.
                :military_medal: <@323922433654390784> - For aiding me in fixing several commands and showing me just how much of a newbie I am at Python.

                :military_medal: <@571494333090496514> - For his massive assistance in improving the backend of Project Prismarine, as well as the endless refactoring of my bodged code, and seeing solutions to issues I genuinely would have never thought of to implement myself.

                :military_medal: @DaysyMarunss (Twitter) - For creating the profile image for Project Prismarine.

                *Communal Commenations*

                Splatoon2.ink - for providing the data used within the Splatnet module.

                To all of these people, I only have one thing to say:
                Thank you.""",
            color=discord.Color.gold(),
        )
        embed.set_author(
            name="Project Prismarine", icon_url=self.client.user.avatar_url
        )
        embed.set_footer(text=f"Solidarity, Dr. Prismarine Bluefall.")
        credits_message = await ctx.send(embed=embed)
        await credits_message.add_reaction("🏆")

    @commands.command()
    async def prefix(self, ctx):
        """Get a server's prefix."""
        server_prefix = self.get_db("main").execute(
            select([self.get_table("main", "prefix")]). \
            where(self.get_table("main", "prefix").columns["server_id"] == ctx.message.guild.id)
        ).fetchone()
        if server_prefix is not None:
            await ctx.send(f"Your prefix is `{server_prefix[1]}`")
        else:
            await ctx.send(f"Your prefix is `{CONFIG['prefix']}`")


with open("config.json", "r") as infile:
    CONFIG = json.load(infile)


def setup(client):
    """Add the module to the bot."""
    client.add_cog(Main(client))
    logging.info("main Module Online.")
