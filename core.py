"""Core file holding the Prismarine Bot."""
import os
import logging
import json
from itertools import cycle
import sqlite3  # pylint: disable=unused-import
import discord
from discord.ext import commands, tasks

with open("config.json", "r") as infile:
    try:
        CONFIG = json.load(infile)
        _ = CONFIG["token"]
        _ = CONFIG["owner"]

    except (KeyError, FileNotFoundError):
        raise EnvironmentError(
            "Your config.json file is either missing, or incomplete. Check your config.json and ensure it has the keys 'token' and 'owner'"
        )

STATUS = cycle(
    [
        "with my creator!",
        "with life, the universe, and everything.",
        "with my ROBOT ARMY!",
        "with a rubber ducky :)",
        "with Agent 3 and her Pokemon!",
        "with Python and waifus!",
        "with SCIENCE!",
        "with ~~atomic bombs~~ ...toys",
    ]
)

CLIENT = commands.Bot(command_prefix="pr.", status=discord.Status.online)

logging.basicConfig(
    level=logging.INFO, format="%(name)s - %(levelname)s - %(asctime)s - %(message)s"
)

# --- Client Events

task_starter = 0  # only set variables that are constants here.


@CLIENT.event
async def on_ready():
    """What happens whem the bot is ready."""
    global task_starter  # Try to avoid using global statements
    logging.basicConfig(
        level=logging.INFO, format="%(name)s - %(levelname)s - %(asctime)s - %(message)s"
    )
    if task_starter == 0:
        stat_change.start()
        task_starter += 1
    logging.info("Log successfuly launched. Project Prismarine is online.")


@CLIENT.event
async def on_command_error(ctx, error):
    """Logs the error."""
    logging.info("%i - %s", ctx.guild.id, error)


# --- Bot Commands


@commands.is_owner()
@CLIENT.command()
async def load(ctx, extension):
    """Loads the specified module within the bot."""
    CLIENT.load_extension(f"modules.{extension}")
    await ctx.send(f"Module `{extension}` loaded.")
    logging.info("%s module loaded.", extension)


@load.error
async def load_error(ctx, error):
    """Error if the specified module cannot be loaded."""
    if isinstance(error, discord.ext.commands.errors.CommandInvokeError):
        await ctx.send(
            "Module could not be loaded. Make sure that the module name is correct, and is in the correct directory."
        )


@commands.is_owner()
@CLIENT.command()
async def unload(ctx, extension):
    """Unloads the specified module within the bot."""
    CLIENT.unload_extension(f"modules.{extension}")
    await ctx.send(f"Module `{extension}` unloaded.")
    logging.info("%s module unloaded.", extension)


@unload.error
async def unload_error(ctx, error):
    """Error if the specified module cannot be unloaded."""
    if isinstance(error, discord.ext.commands.errors.CommandInvokeError):
        await ctx.send(
            "Module could not be unloaded. Make sure that the module name is correct, and is in the correct directory."
        )


@commands.is_owner()
@CLIENT.command()
async def reload(ctx, extension):
    """Reloads the specified module within the bot."""
    CLIENT.unload_extension(f"modules.{extension}")
    CLIENT.load_extension(f"modules.{extension}")
    await ctx.send(f"Module `{extension}` reloaded.")
    logging.info("%s module reloaded.", extension)


@reload.error
async def reload_error(ctx, error):
    """Error if the specified module cannot be reloaded."""
    if isinstance(error, discord.ext.commands.errors.CommandInvokeError):
        await ctx.send(
            "Module could not be reloaded. Make sure that the module name is correct, and is in the correct directory."
        )
        print(error)


@CLIENT.command()
async def credits(ctx):
    """Credits the people who have contributed to the bot."""
    embed = discord.Embed(
        title="The Credits",
        description="""This command exists to commemorate and properly credit those who have assisted, inspired, or otherwise contributed to the creation of Project Prismarine.

    <@274983796414349313> - For initially inspiring me to learn Python and persue Computer Science and programming in a serious manner, as well as for his open-source Splatoon bot, from which I referenced frequently in Project Prismarine's development.

    <@196470965402730507> - For reviewing Project Prismarine's code and general assistance in my code endeavors.
    <@323922433654390784> - For aiding me in fixing several commands and showing me just how much of a newbie I am at Python.

    <@571494333090496514> - For his massive assistance in improving the backend of Project Prismarine and making a multitide of improvements in the bot.

    To all of these people, I only have one thing to say:
    Thank you.
    """,
        color=discord.Color.gold(),
    )
    embed.set_author(name="Unit 10008-RSP", icon_url=CLIENT.user.avatar_url)
    embed.set_footer(text=f"Solidarity, Dr. Prismarine Bluefall.")
    credits_message = await ctx.send(embed=embed)
    await credits_message.add_reaction("🏆")


# --- Misc. Code


@tasks.loop(seconds=30)
async def stat_change():
    """Changes the status of the bot every few seconds."""
    await CLIENT.change_presence(activity=discord.Game(next(STATUS)))


for filename in os.listdir("./modules"):
    if filename.endswith(".py"):
        CLIENT.load_extension(f"modules.{filename[:-3]}")

CLIENT.run(CONFIG["token"])
