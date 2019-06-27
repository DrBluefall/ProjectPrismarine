"""Core file holding the Prismarine Bot."""
import os
import logging
import json
from itertools import cycle
import discord
from discord.ext import commands, tasks
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, select

with open("config.json", "r") as infile:
    try:
        CONFIG = json.load(infile)
        _ = (
            CONFIG["token"], CONFIG["owner"], CONFIG["dbl_token"],
            CONFIG["prefix"]
        )

    except (KeyError, FileNotFoundError):
        raise EnvironmentError(
            "Your config.json file is either missing, or incomplete. Check your config.json and ensure it has the keys 'token', 'owner', 'dbl_token', and 'prefix'."
        )
STATUS = cycle(
    [
        "with my creator!",
        "with life, the universe, and everything.",
        "with my ROBOT ARMY!",
        "with a rubber ducky :)",
        "with Agent 3 and her Pokémon!",
        "with Python and waifus!",
        "with SCIENCE!",
        "with an atomic bo-I MEAN TOYS! Toys. Yeah. That's a thing bots do, right?",
    ]
)

db = create_engine("sqlite:///main.db")
metadata = MetaData(db)
metadata.reflect()
c = db.connect()


def get_prefix(client, message):
    """Retrieve a guild's prefix."""
    raw_prefix_data = c.execute(select([metadata.tables["prefix"]])).fetchall()
    prefix_dict = {}
    for server in raw_prefix_data:
        prefix_dict[str(server[0])] = server[1]
    if not message.guild:
        return commands.when_mentioned_or(CONFIG["prefix"])(client, message)
    if str(message.guild.id) not in prefix_dict.keys():
        return commands.when_mentioned_or(CONFIG["prefix"])(client, message)
    return commands.when_mentioned_or(prefix_dict[str(message.guild.id)]
                                      )(client, message)


CLIENT = commands.Bot(command_prefix=get_prefix, status=discord.Status.online)

logging.basicConfig(
    level=logging.INFO,
    format="%(name)s - %(levelname)s - %(asctime)s - %(message)s"
)

task_starter = 0

@CLIENT.event
async def on_ready():
    """Execute on bot login."""
    global task_starter  # pylint: disable=global-statement, invalid-name
    logging.basicConfig(
        level=logging.INFO,
        format="%(name)s - %(levelname)s - %(asctime)s - %(message)s"
    )
    if task_starter == 0:
        stat_change.start()
        task_starter += 1
    logging.info("Project Prismarine is online.")


class Core(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.client.remove_command("help")
        self.client.add_cog(self)

    @commands.command()
    async def help(self, ctx):
        """Client command documentation."""
        embed = discord.Embed(
            title="Project Prismarine - User Manual",
            color=discord.Color.dark_red()
        )
        for module_name, module in self.client.cogs.items():
            embed.add_field(name=module_name, value=module.description)

        await ctx.send(embed=embed)


    @commands.command()
    async def prefix(self, ctx):
        """Get a server's prefix."""
        server_prefix = c.execute(
            select([metadata.tables["prefix"]])\
            .where(metadata.tables["prefix"].c.server_id == ctx.message.guild.id)
        ).fetchone()
        if server_prefix is not None:
            await ctx.send(f"Your prefix is `{server_prefix[1]}`")
        else:
            await ctx.send(f"Your prefix is `{CONFIG['prefix']}`")


    @commands.is_owner()
    @commands.command()
    async def load(self, ctx, extension):
        """Load the specified module within the bot."""
        try:
            self.client.load_extension(f"modules.{extension}")
            await ctx.send(f"Module `{extension}` loaded.")
            logging.info("%s module loaded.", extension)
        except (commands.CommandInvokeError, commands.ExtensionNotLoaded, commands.ExtensionNotFound) as error:
            await ctx.send("Module could not be loaded. Check the console to assure that there are no errors, and that the name of the module was spelled correctly.")
            logging.exception("%i - %s", ctx.guild.id, error)

    @commands.is_owner()
    @commands.command()
    async def unload(self, ctx, extension):
        """Unload the specified module within the bot."""
        try:
            self.client.unload_extension(f"modules.{extension}")
            await ctx.send(f"Module `{extension}` unloaded.")
            logging.info("%s module unloaded.", extension)
        except (commands.CommandInvokeError, commands.ExtensionNotLoaded, commands.ExtensionNotFound) as error:
            await ctx.send("Module could not be unloaded. Check the console to assure that there are no errors, and that the name of the module was spelled correctly.")
            logging.exception("%i - %s", ctx.guild.id, error)

    @commands.is_owner()
    @commands.command()
    async def reload(self, ctx, extension):
        """Reload the specified module within the bot."""
        try:
            self.client.unload_extension(f"modules.{extension}")
            self.client.load_extension(f"modules.{extension}")
            await ctx.send(f"Module `{extension}` reloaded.")
            logging.info("%s module reloaded.", extension)
        except (commands.CommandInvokeError, commands.ExtensionNotLoaded, commands.ExtensionNotFound) as error:
            await ctx.send("Module could not be reloaded. Check the console to assure that there are no errors, and that the name of the module was spelled correctly.")
            logging.exception("%i - %s", ctx.guild.id, error)

    @commands.command()
    async def credits(self, ctx):
        """Credits the people who have contributed to the bot."""
        embed = discord.Embed(
            title="The Credits",
            description=
            """This command exists to commemorate and properly credit those who have assisted, inspired, or otherwise contributed to the creation of Project Prismarine.

        *Personal Commendations*

        :military_medal: <@274983796414349313> - For initially inspiring me to learn Python and persue Computer Science and programming in a serious manner, as well as for his open-source Splatoon bot, from which I referenced frequently in Project Prismarine's development.

        :military_medal: <@196470965402730507> - For reviewing Project Prismarine's code and general assistance in my code endeavors, and a really interesting person to talk with in general, whether the topic be programming or otherwise.
        :military_medal: <@323922433654390784> - For aiding me in fixing several commands and showing me just how much of a newbie I am at Python.

        :military_medal: <@571494333090496514> - For his massive assistance in improving the backend of Project Prismarine, as well as the endless refactoring of my bodged code, and seeing solutions to issues I genuinely would have never thought of to implement myself.

        *Communal Commenations*

        Splatoon2.ink - for providing the data used within the Splatnet module.

        To all of these people, I only have one thing to say:
        Thank you.
        """,
            color=discord.Color.gold(),
        )
        embed.set_author(name="Unit 10008-RSP", icon_url=self.client.user.avatar_url)
        embed.set_footer(text=f"Solidarity, Dr. Prismarine Bluefall.")
        credits_message = await ctx.send(embed=embed)
        await credits_message.add_reaction("🏆")


@tasks.loop(seconds=30)
async def stat_change():
    """Change the status of the bot every few seconds."""
    await CLIENT.change_presence(activity=discord.Game(next(STATUS)))


for filename in os.listdir("./modules"):
    if filename.endswith(".py") \
    and filename[:-3] != "decoder" and filename[:-3] != "weapons":
        CLIENT.load_extension(f"modules.{filename[:-3]}")

CLIENT.run(CONFIG["token"])
