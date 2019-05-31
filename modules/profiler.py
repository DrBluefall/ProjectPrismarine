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
        """Initializes a user profile."""
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
            await ctx.send("Quality Assurance Tester Profile initialized. Thank you for choosing PrismarineCo. Laboratories.")
        else:
            await ctx.send("Existing QA Profile detected. Aborting initialization...")

    @profile.command()
    async def ign(self, ctx, *, name: str = None):
        global engine
        global metadata
        global table
        global c
        if name is not None:
            if not len(name) > 10:
                ign = table.update().where(table.c.user_id == ctx.message.author.id).values(ign=name)
                c.execute(ign)
                await ctx.send("IGN successfully updated!")
            else:
                await ctx.send("Command Failed - IGN character limit is set at 10.")
        else:
            await ctx.send("Command Failed - No IGN specified.")

    @profile.command()
    async def fc(self, ctx, friend: int = None, code: int = None, here: int = None):
        global engine
        global metadata
        global table
        global c
        if friend is not None and code is not None and here is not None:
            friend, code, here = str(friend), str(code), str(here)
            fc_len = len(friend) + len(code) + len(here)
            if fc_len == 12 and len(friend) == 4 and len(code) == 4 and len(here) == 4:
                fc = table.update().where(table.c.user_id == ctx.message.author.id).values(
                    fc=f"SW-{friend}-{code}-{here}")
                c.execute(fc)
                await ctx.send("Friend Code successfully updated!")
            else:
                await ctx.send("""Command Failed - Friend Code must be 12 characters long, grouped into 3 sets of 4. /n Example: `-profile fc 1234 5678 9101`""")
        else:
            await ctx.send("Command Failed - Friend Code must be 12 characters long, grouped into 3 sets of 4. /n Example: `-profile fc 1234 5678 9101`.")

    @profile.command()
    async def level(self, ctx, *, level: int = None):
        global engine
        global metadata
        global table
        global c
        if level is not None:
            level = table.update().where(table.c.user_id == ctx.message.author.id).values(level=level)
            c.execute(level)
            await ctx.send("Level successfully updated!")
        else:
            await ctx.send("Command Failed - No level specified.")

    @profile.command()
    async def rank(self, ctx, gamemode: str = None, rank: str = None):
        global engine
        global metadata
        global table
        global c
        game_mode = ['cb', 'tc', 'sz', 'rm', 'sr']
        rank_list = ['c-', 'c', 'c+', 'b-', 'b', 'b+', 'a-', 'a', 'a+', 's', 's+0',
                     's+1', 's+2', 's+3', 's+4', 's+5', 's+6', 's+7', 's+8', 's+9', 'x']
        sr_rank_list = ['intern', 'apprentice', 'part-timer',
                        'go-getter', 'overachiever', 'profreshional']
        try:
            if gamemode.lower() in game_mode:
                if rank.lower() in rank_list:
                    if gamemode == game_mode[0]:
                        rank = table.update().where(table.c.user_id == ctx.message.author.id).values(cb_rank=rank.upper())
                        c.execute(rank)
                        await ctx.send("Clam Blitz rank updated!")
                    elif gamemode == game_mode[1]:
                        rank = table.update().where(table.c.user_id == ctx.message.author.id).values(tc_rank=rank.upper())
                        c.execute(rank)
                        await ctx.send("Tower Control rank updated!")
                    elif gamemode == game_mode[2]:
                        rank = table.update().where(table.c.user_id == ctx.message.author.id).values(sz_rank=rank.upper())
                        c.execute(rank)
                        await ctx.send("Splat Zones rank updated!")
                    elif gamemode == game_mode[3]:
                        rank = table.update().where(table.c.user_id == ctx.message.author.id).values(rm_rank=rank.upper())
                        c.execute(rank)
                        await ctx.send("Rainmaker rank updated!")
                elif rank.lower() == sr_rank_list[0]:
                    rank = table.update().where(table.c.user_id == ctx.message.author.id).values(sr_rank='Intern')
                    await ctx.send("Salmon Run rank updated!")
                elif rank.lower() == sr_rank_list[1]:
                    rank = table.update().where(table.c.user_id == ctx.message.author.id).values(sr_rank='Apprentice')
                    await ctx.send("Salmon Run rank updated!")
                elif rank.lower() == sr_rank_list[2]:
                    rank = table.update().where(table.c.user_id == ctx.message.author.id).values(sr_rank='Part-Timer')
                    await ctx.send("Salmon Run rank updated!")
                elif rank.lower() == sr_rank_list[3]:
                    rank = table.update().where(table.c.user_id == ctx.message.author.id).values(sr_rank='Go-Getter')
                    await ctx.send("Salmon Run rank updated!")
                elif rank.lower() == sr_rank_list[4]:
                    rank = table.update().where(table.c.user_id == ctx.message.author.id).values(sr_rank='Overachiever')
                    await ctx.send("Salmon Run rank updated!")
                elif rank.lower() == sr_rank_list[5]:
                    rank = table.update().where(table.c.user_id == ctx.message.author.id).values(sr_rank='Profreshional')
                    await ctx.send("Salmon Run rank updated!")
                else:
                    await ctx.send("Command Failed - Rank was not and/or incorrectly specified.")
            else:
                await ctx.send("Command Failed - Gamemode was not and/or incorrectly specified.")
        except AttributeError:
            await ctx.send("Command Failed - Argument not specified.")


def setup(client):
    """Adds the module to the bot."""
    client.add_cog(Profiler(client))
    logging.info("Profiler Module Online.")
