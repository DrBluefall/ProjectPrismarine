"""Core file and entry point for the bot."""
# Core Language Imports

import logging
import json

# Third-Party Imports

import discord
from discord.ext import commands
import coloredlogs



class Client(commands.Bot):
    """The base class of Project Prismarine."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
def main():
    coloredlogs.install()
    with open("../config.json") as infile:
        cfg = json.load(infile)
    client = Client(
        command_prefix=cfg["prefix"], 
        owners=cfg["owners"])
    client.run(cfg["token"])

if __name__ == "__main__":
    main()