"""Core file holding the Prismarine Bot."""
import os
import logging
import json
from itertools import cycle
import discord
from discord.ext import commands, tasks
from sqlalchemy import create_engine, MetaData, select


class DBHandler:
    """Class to handle database global management."""

    def __init__(self):
        """Init the handler."""
        self.dbs = {
            "main": {
                "db": create_engine("sqlite:///main.db").connect(),
                "meta": MetaData()
            },
            "assets": {
                "db": create_engine("sqlite:///assets/assets.db").connect(),
                "meta": MetaData()
            }
        }
        self.dbs["main"]["meta"].reflect(self.dbs["main"]["db"])
        self.dbs["assets"]["meta"].reflect(self.dbs["assets"]["db"])

    def get_db(self, key):
        """Return the database at the specified key."""
        return self.dbs[key]["db"]

    def get_meta(self, key):
        """Return the metadata at the specified key."""
        return self.dbs[key]["meta"]


def get_prefix(client, message):
    """Retrieve a guild's prefix."""
    dbh = DBHandler()
    try:
        raw_prefix_data = dbh.get_db("main").execute(
            select([dbh.get_meta("main").tables["prefix"]])
        ).fetchall()
    except KeyError:
        return commands.when_mentioned_or(CONFIG["prefix"])
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

task_starter = 0  # pylint: disable=invalid-name


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


@CLIENT.event
async def on_command_error(ctx, err):
    """Execute on command error."""
    if not isinstance(err, commands.CommandNotFound):
        await ctx.send(
            f"""
            Command Error - Unhandled Exception:
            ```swift
            {err}
            ```
            Please report this error to the support server immediately: https://discord.gg/XpX5nKr"""
        )
        logging.exception(err)


@tasks.loop(seconds=30)
async def stat_change():
    """Change the status of the bot every few seconds."""
    await CLIENT.change_presence(activity=discord.Game(next(STATUS)))


for filename in os.listdir("./modules"):
    if filename.endswith(".py") \
    and filename[:-3] != "decoder" and filename[:-3] != "weapons":
        CLIENT.load_extension(f"modules.{filename[:-3]}")
logging.basicConfig(
    level=logging.INFO,
    format="%(name)s - %(levelname)s - %(asctime)s - %(message)s"
)
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

CLIENT.remove_command("help")
CLIENT.run(CONFIG["token"])
