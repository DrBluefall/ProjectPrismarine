import logging
import discord
import sqlite3
from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy import Table, Column
from sqlalchemy import Integer, String
from sqlalchemy import select
from discord.ext import commands

engine = create_engine("sqlite:///ProjectPrismarine.db")
metadata = MetaData(engine)
table = Table('profile', metadata,
              Column('user_id', Integer, primary_key=True),
              Column('ign', String),
              Column('fc', String),
              Column('level', Integer),
              Column('rm_rank', String),
              Column('tc_rank', String),
              Column('sz_rank', String),
              Column('cb_rank', String),
              Column('sr_rank', String),
              )

metadata.create_all()
c = engine.connect()

# Note to self: Remember to commit database changes!!!!!


class Profiler(commands.Cog):
    """Module containing commands pertaining to managing and querying user profiles."""

    def __init__(self, client):
        self.client = client

    @commands.group(invoke_without_command=True, case_insensitive=True, ignore_extra=False)
    async def profile(self, ctx, user=None):
        """Profile command group. If run without a subcommand, it will query for the profile of either the message author or specified user."""
        global engine
        global metadata
        global table
        global c
        if ctx.invoked_subcommand is None:
            if user is None:
                user = ctx.message.author
            else:
                try:
                    user = int(user)
                    user = self.client.get_user(user)
                except ValueError:
                    user = ctx.message.mentions[0]
            profile_select = select([table]).where(table.c.user_id == user.id)
            profile = c.execute(profile_select)
            profile = profile.fetchone()
            embed = discord.Embed(
                title=f"QA Tester #{profile[0]}'s Profile",
                color=discord.Color.dark_red()
            )

            embed.set_thumbnail(url=user.avatar_url)
            embed.add_field(name="In-Game Name:", value=profile[1])
            embed.add_field(name="Level:", value=profile[3])
            embed.add_field(name="Friend Code:", value=profile[2])
            embed.add_field(name="Rainmaker Rank:", value=profile[4])
            embed.add_field(name="Tower Control Rank:", value=profile[5])
            embed.add_field(name="Splat Zones Rank:", value=profile[6])
            embed.add_field(name="Clam Blitz Rank:", value=profile[7])
            embed.add_field(name="Salmon Run Rank:", value=profile[8])
            await ctx.send(embed=embed)

    @profile.command()
    async def init(self, ctx):
        global engine
        global metadata
        global table
        global c
        profile_select = select([table]).where(table.c.user_id == ctx.message.author.id)
        profile = c.execute(profile_select)
        profile = profile.fetchone()
        if profile is None:
            ins = table.insert().values(user_id=ctx.message.author.id, ign='N/A', fc='SW-0000-0000-0000',
                                        level=1, rm_rank='C-', tc_rank='C-', sz_rank='C-', cb_rank='C-', sr_rank='Intern')
            c.execute(ins)
            await ctx.send("QA Tester Profile Initialized. Thank you for choosing PrismarineCo. Laboratories.")
        else:
            await ctx.send("Existing QA Profile detected. Aborting initialization...")


def setup(client):
    """Adds the module to the bot."""
    client.add_cog(Profiler(client))
    logging.info("Profiler Module Online.")
