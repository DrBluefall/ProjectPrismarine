"""Holds the profile cog."""
import logging
import discord
from discord.ext import commands
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, select


class Profiler(commands.Cog):
    """Module containing commands pertaining to managing and querying user profiles."""

    def __init__(self, client):
        """Initialize the Profiler cog."""
        self.client = client

    engine = create_engine("sqlite:///ProjectPrismarine.db")
    metadata = MetaData(engine)
    table = Table(
        "profile",
        metadata,
        Column("user_id", Integer, primary_key=True),
        Column("ign", String),
        Column("fc", String),
        Column("level", Integer),
        Column("rm_rank", String),
        Column("tc_rank", String),
        Column("sz_rank", String),
        Column("cb_rank", String),
        Column("sr_rank", String),
    )

    metadata.create_all()
    c = engine.connect()

    @commands.group(invoke_without_command=True, case_insensitive=True, ignore_extra=False)
    async def profile(self, ctx, user=None):
        """Profile command group. If run without a subcommand, it will query for the profile of either the message author or specified user."""
        if ctx.invoked_subcommand is None:
            if user is None:
                user = ctx.message.author
            else:
                try:
                    user = int(user)
                    user = self.client.get_user(user)
                except ValueError:
                    user = ctx.message.mentions[0]
            profile_select = select([__class__.table]).where(__class__.table.c.user_id == user.id)
            profile = __class__.c.execute(profile_select)
            profile = profile.fetchone()
            embed = discord.Embed(
                title=f"QA Tester #{profile[0]}'s Profile", color=discord.Color.dark_red()
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
        """Initialize a user profile."""
        profile = __class__.c.execute(
            select([__class__.table]).where(__class__.table.c.user_id == ctx.message.author.id)
        )
        profile = profile.fetchone()
        assert len(profile.fetchall()) == 1 or len(profile.fetchall()) is None
        if profile is None:
            ins = __class__.table.insert(None).values(
                user_id=ctx.message.author.id,
                ign="N/A",
                fc="SW-0000-0000-0000",
                level=1,
                rm_rank="C-",
                tc_rank="C-",
                sz_rank="C-",
                cb_rank="C-",
                sr_rank="Intern",
            )
            __class__.c.execute(ins)
            await ctx.send(
                "Quality Assurance Tester Profile initialized. Thank you for choosing PrismarineCo. Laboratories."
            )
        else:
            await ctx.send("Existing QA Profile detected. Aborting initialization...")

    @staticmethod
    def check_profile_exists(user_id):
        """Check if a profile exists in the database or not."""
        profile = __class__.c.execute(
            select([__class__.table]).where(__class__.table.c.user_id == user_id)
        ).fetchone()
        if profile is None:
            output = False
        else:
            output = True
        return output

    @profile.command()
    async def ign(self, ctx, *, name: str = None):
        """Update someone's IGN."""
        if name is not None:
            if not len(name) > 10:
                ign = (
                    __class__.table.update(None)
                    .where(__class__.table.c.user_id == ctx.message.author.id)
                    .values(ign=name)
                )
                __class__.c.execute(ign)
                await ctx.send("IGN successfully updated!")
            else:
                await ctx.send("Command Failed - IGN character limit is set at 10.")
        else:
            await ctx.send("Command Failed - No IGN specified.")

    @profile.command()
    async def fc(self, ctx, friend: int = None, code: int = None, here: int = None):
        """Update someone's Friend Code."""
        if friend is not None and code is not None and here is not None:
            friend, code, here = str(friend), str(code), str(here)
            fc_len = len(friend) + len(code) + len(here)
            if fc_len == 12 and len(friend) == 4 and len(code) == 4 and len(here) == 4:
                fc = (
                    __class__.table.update(None)
                    .where(__class__.table.c.user_id == ctx.message.author.id)
                    .values(fc=f"SW-{friend}-{code}-{here}")
                )
                __class__.c.execute(fc)
                await ctx.send("Friend Code successfully updated!")
            else:
                await ctx.send(
                    """Command Failed - Friend Code must be 12 characters long, grouped into 3 sets of 4. /n Example: `-profile fc 1234 5678 9101`"""
                )
        else:
            await ctx.send(
                "Command Failed - Friend Code must be 12 characters long, grouped into 3 sets of 4. /n Example: `-profile fc 1234 5678 9101`."
            )

    @profile.command()
    async def level(self, ctx, *, level: int = None):
        """Update someone's level."""
        if level is not None:
            level = (
                __class__.table.update(None)
                .where(__class__.table.c.user_id == ctx.message.author.id)
                .values(level=level)
            )
            __class__.c.execute(level)
            await ctx.send("Level successfully updated!")
        else:
            await ctx.send("Command Failed - No level specified.")

    @profile.command()
    async def rank(self, ctx, gamemode: str = None, rank: str = None):
        """Update a person's rank in the database."""
        rank_list = (
            "C-",
            "C",
            "C+",
            "B-",
            "B",
            "B+",
            "A-",
            "A",
            "A+",
            "S",
            "S+0",
            "S+1",
            "S+2",
            "S+3",
            "S+4",
            "S+5",
            "S+6",
            "S+7",
            "S+8",
            "S+9",
            "X",
        )
        modes = {
            "Splat Zones": {"aliases": ("sz", "splatzones", "sz_rank"), "rlist": rank_list},
            "Rainmaker": {"aliases": ("rm", "rainmaker", "rm_rank"), "rlist": rank_list},
            "Tower Control": {"aliases": ("tc", "towercontrol", "tc_rank"), "rlist": rank_list},
            "Clam Blitz": {"aliases": ("cb", "clamblitz", "cb_rank"), "rlist": rank_list},
            "Salmon Run": {
                "aliases": ("sr", "salmonrun", "sr_rank"),
                "rlist": (
                    "Intern",
                    "Apprentice",
                    "Part-timer",
                    "Go-getter",
                    "Overachiever",
                    "Profreshional",
                ),
            },
        }
        if gamemode is None:
            await ctx.send("Command Failed - Argument not specified.")
        else:
            for key, value in modes.items():
                if gamemode.lower() in value["aliases"]:

                    if rank.upper() in value["rlist"]:
                        changed_rank = rank.upper()
                    elif rank.capitalize() in value["rlist"]:
                        changed_rank = rank.capitalize()
                    else:
                        changed_rank = None

                    if changed_rank is None:
                        await ctx.send(
                            "Command Failed - Rank was not and/or incorrectly specified."
                        )
                    else:
                        eval(
                            """Profiler.c.execute((Profiler.table.update(None).where(Profiler.table.c.user_id == ctx.message.author.id).values("""
                            + value["aliases"][-1]
                            + """=changed_rank)))"""
                        )
                        await ctx.send(f"{key} rank updated!")
                    break
            else:
                await ctx.send("Command Failed - Gamemode was not and/or incorrectly specified.")


def setup(client):
    """Add the module to the bot."""
    client.add_cog(Profiler(client))
    logging.info("Profiler Module Online.")
