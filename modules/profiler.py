import logging
import discord
import sqlite3
import aiosqlite
from discord.ext import commands


class Profiler(commands.Cog):
    """Module containing commands pertaining to managing user profiles."""

    def __init__(self, client):
        self.client = client

    @commands.group(invoke_without_command=True, case_insensitive=True, ignore_extra=False)
    async def profile(self, ctx, user=None):
        db = sqlite3.connect("profile.db")
        c = db.cursor()
        if ctx.invoked_subcommand is None:
            c.execute("SELECT * FROM profile WHERE user_id =?", (ctx.message.author.id,))
            print(c.fetchone())
            print("aaa")

    @profile.command()
    async def init(self, ctx):
        db = sqlite3.connect("profile.db")
        c = db.cursor()
        c.execute("INSERT INTO profile(user_id, user, ign, fc, level, rm_rank, tc_rank, sz_rank, cb_rank) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) ",
                  (ctx.message.author.id, ctx.message.author, 'N/A', 'SW-0000-0000-0000', 1, 'C-', 'C-', 'C-', 'C-'))
        print("aaaa")


def setup(client):
    """Adds the module to the bot."""
    client.add_cog(Profiler(client))
    logging.info("Profiler Module Online.")
