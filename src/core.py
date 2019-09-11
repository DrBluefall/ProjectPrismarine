"""Core file and entry point for the bot."""
# Standard Library Imports:

import logging
import os
from datetime import datetime

# Third-Party Imports:

from discord.ext import commands
import coloredlogs

# Local Project Imports

from config import token, owner_ids, prefix


class Client(commands.Bot):
    """The core class of Project Prismarine."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.start_time = datetime.utcnow()
        self.started_up = False

    async def on_ready(self):
        if not self.started_up:
            logging.info(f"""All systems are clear. {self.user.name} is online!""")
            self.started_up = True


def load_extensions(client):
    for file in os.listdir("./modules"):
        if file.endswith(".py"):
            client.load_extension("modules.%s" % file[:-3])
            logging.info("%s module: Online!", file[:-3].capitalize())


def main():
    coloredlogs.DEFAULT_FIELD_STYLES.update({'funcName': {'color': 'cyan'}})
    coloredlogs.DEFAULT_FIELD_STYLES["name"]["color"] = 'yellow'
    coloredlogs.install(
        level="INFO",
        fmt="[%(hostname)s] %(asctime)s %(funcName)s:%(lineno)s %(name)s %(levelname)s %(message)s"
    )
    logging.debug("Log configuration complete.")
    client = Client(command_prefix=commands.when_mentioned_or(prefix), owners=owner_ids)
    load_extensions(client)
    client.run(token)


if __name__ == "__main__":
    main()
