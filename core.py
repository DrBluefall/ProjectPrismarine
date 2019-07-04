"""Core file holding the Prismarine Bot."""
import os
import logging
import json
from itertools import cycle
import discord
from discord.ext import commands, tasks
from sqlalchemy import create_engine, MetaData, select


class Bot(commands.Bot):
    """Class that holds discord bot events."""

    def __init__(self, *args, **kwargs):
        """Init the bot."""
        super().__init__(*args, **kwargs)
        self.task_starter = 0
        self.statuses = cycle(
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

    async def on_ready(self):
        """Execute on bot login."""
        logging.basicConfig(
            level=logging.INFO,
            format="%(name)s - %(levelname)s - %(asctime)s - %(message)s"
        )
        if self.task_starter == 0:
            self.stat_change.start()
            self.task_starter += 1
        logging.info("Project Prismarine is online.")

    @tasks.loop(seconds=30)
    async def stat_change(self):
        """Change the status of the bot every few seconds."""
        await self.change_presence(activity=discord.Game(next(self.statuses)))


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
        return commands.when_mentioned_or(CONFIG["prefix"])(client, message)
    prefix_dict = {}
    for server in raw_prefix_data:
        prefix_dict[str(server[0])] = server[1]
    if not message.guild:
        return commands.when_mentioned_or(CONFIG["prefix"])(client, message)
    if str(message.guild.id) not in prefix_dict.keys():
        return commands.when_mentioned_or(CONFIG["prefix"])(client, message)
    return commands.when_mentioned_or(prefix_dict[str(message.guild.id)]
                                      )(client, message)


def load_all_extensions(bot):
    """Load all files inside of modules."""
    for filename in os.listdir("./modules"):
        if filename.endswith(".py") \
        and filename[:-3] != "decoder" and filename[:-3] != "weapons":
            bot.load_extension(f"modules.{filename[:-3]}")


def set_logging():
    """Set the basic config of logging module."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(name)s - %(levelname)s - %(asctime)s - %(message)s"
    )


def get_config_file():
    """Open the config.json file and check if all parameters exist, then return the config dict."""
    with open("config.json", "r") as infile:
        try:
            infile = json.load(infile)
            _ = (
                infile["token"], infile["owner"], infile["dbl_token"],
                infile["prefix"]
            )

        except (KeyError, FileNotFoundError):
            raise EnvironmentError(
                "Your config.json file is either missing, or incomplete. Check your config.json and ensure it has the keys 'token', 'owner', 'dbl_token', and 'prefix'."
            )
    return infile


def main():
    """Run the bot."""
    bot = Bot(command_prefix=get_prefix, status=discord.Status.online)

    load_all_extensions(bot)
    set_logging()

    bot.remove_command("help")
    bot.run(CONFIG["token"])


if __name__ == '__main__':
    CONFIG = get_config_file()
    main()
