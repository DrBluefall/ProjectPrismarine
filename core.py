"""Core file holding the Prismarine Bot."""
import os
import logging
import coloredlogs
import json
from itertools import cycle
import discord
from discord.ext import commands, tasks
from sqlalchemy import create_engine, MetaData, select
from sqlalchemy import Table, Column, Integer, String


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
            self.stat_change.start()  # pylint: disable=E1101
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
        self.dbs["main"]["meta"].reflect(bind=self.dbs["main"]["db"])
        self.dbs["assets"]["meta"].reflect(bind=self.dbs["assets"]["db"])

    def reload_meta(self, key):
        """Set metadata at specified key to the latest information."""
        self.dbs[key]["meta"] = MetaData()
        self.dbs[key]["meta"].reflect(bind=self.dbs[key]["db"])

    def get_table(self, key, name):
        """Return table from metadata at specified key."""
        try:
            return self.get_meta(key).tables[name]
        except KeyError:
            self.create_main_db()
            return self.get_meta(key).tables[name]

    def get_db(self, key):
        """Return the database at the specified key."""
        return self.dbs[key]["db"]

    def get_meta(self, key):
        """Return the metadata at the specified key."""
        return self.dbs[key]["meta"]

    def create_main_db(self):
        """Create the main.db."""
        self.get_meta("main").drop_all(bind=self.get_db("main"))
        self.reload_meta("main")

        Table(
            "prefix", self.get_meta("main"),
            Column("server_id", Integer, primary_key=True),
            Column("prefix", String)
        )
        Table(
            "profile", self.get_meta("main"),
            Column("user_id", Integer, primary_key=True),
            Column("ign", String), Column("fc", String),
            Column("level", Integer), Column("rm_rank", String),
            Column("tc_rank", String), Column("sz_rank", String),
            Column("cb_rank", String), Column("sr_rank", String),
            Column("loadout_string", String, server_default="0" * 25)
        )
        Table(
            "team_profile", self.get_meta("main"),
            Column("team_id", Integer, primary_key=True),
            Column("name", String), Column("description", String),
            Column("captain", Integer, nullable=False),
            Column("player_2", Integer, nullable=False),
            Column("player_3", Integer, nullable=False),
            Column("player_4", Integer, nullable=False),
            Column("player_5", Integer), Column("player_6", Integer),
            Column("player_7", Integer)
        )
        Table(
            "team_comp", self.get_meta("main"),
            Column("comp_id", Integer, primary_key=True),
            Column("author_id", Integer), Column("name", String),
            Column("description", String),
            Column("weapon_1", String, server_default="0" * 25),
            Column("weapon_1_role", String), Column("weapon_1_desc", String),
            Column("weapon_2", String, server_default="0" * 25),
            Column("weapon_2_role", String), Column("weapon_2_desc", String),
            Column("weapon_3", String, server_default="0" * 25),
            Column("weapon_3_role", String), Column("weapon_3_desc", String),
            Column("weapon_4", String, server_default="0" * 25),
            Column("weapon_4_role", String), Column("weapon_4_desc", String)
        )

        self.get_meta("main").create_all(bind=self.get_db("main"))


def get_prefix(client, message):
    """Retrieve a guild's prefix."""
    dbh = DBHandler()
    try:
        raw_prefix_data = dbh.get_db("main").execute(
            select([dbh.get_table("main", "prefix")])
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
    coloredlogs.install(level='INFO')
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    logger.info("Log initialized.")

    return logger

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
