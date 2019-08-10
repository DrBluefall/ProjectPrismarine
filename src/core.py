"""Core file and entry point for the bot."""
# Core Language Imports

import os
import logging
import traceback
import json

# Third-Party Imports

import discord
from discord.ext import commands
import coloredlogs



class Client(commands.Bot):
    """The base class of Project Prismarine."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.started_up = False
    
    async def on_ready(self):
        if not self.started_up:
            logging.info("All systems are clear. %s is online!", self.user.name)
    
    async def on_command_error(self, ctx, exception):
        if isinstance(
            exception,
            (commands.CommandNotFound, commands.UserInputError)
            ):
            return
        elif isinstance(exception, (commands.NotOwner, commands.MissingPermissions)):
            await ctx.send("Command Failed - *You are not authorized to use this!* :warning:")
        else:
            err_msg = traceback.format_exception(
                type(exception), exception, exception.__traceback__
            )
            err_msg = ''.join(err_msg)

            logging.error("Unhandled exception in %s:\nInvocation Context: Server - %s (%i), Channel - #%s (%i)\n%s",
            ctx.command.qualified_name, ctx.guild.name, ctx.guild.id, ctx.channel.name, ctx.channel.id, err_msg)
    
def verify_config():
    with open("../config.json") as infile:
        cfg = json.load(infile)
        required_keys = [
            "token",
            "owners",
            "prefix"
        ]
        for key in required_keys:
            if key not in cfg.keys():
                raise Exception("Your config.json is incomplete! Please assure that it has the following keys: " + str(required_keys))

def load_extensions(client):
    for file in os.listdir("./modules"):
        if file.endswith(".py"):
            client.load_extension("modules.%s" % file[:-3])
            logging.info("%s module online", file[:-3].capitalize())

def main():
    coloredlogs.DEFAULT_FIELD_STYLES.update({'funcName': {'color': 'cyan' }})
    coloredlogs.DEFAULT_FIELD_STYLES["name"]["color"] = 'yellow'
    coloredlogs.install(
        fmt="[%(hostname)s] %(asctime)s %(funcName)s(%(lineno)s) %(name)s[%(process)d] %(levelname)s %(message)s"
    )
    verify_config()
    with open("../config.json") as infile:
        cfg = json.load(infile)
    client = Client(
        command_prefix=commands.when_mentioned_or(cfg["prefix"]),
        owners=cfg["owners"])
    load_extensions(client)
    client.run(cfg["token"])

if __name__ == "__main__":
    main()