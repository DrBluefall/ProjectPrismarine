"""Holds the profile cog."""
import logging
import re
import discord
from discord.ext import commands
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, select


def check_profile_exists(user_id):
    """Check if a profile exists in the database or not."""
    profile = Profiler.c.execute(
        select([Profiler.table]).where(Profiler.table.c.user_id == user_id)
    ).fetchone()
    if profile is None:
        output = False
    else:
        output = True
    return output


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

    @commands.group(
        invoke_without_command=True, case_insensitive=True, ignore_extra=False
    )
    async def profile(self, ctx, user=None):
        """Profile command group. If run without a subcommand, it will query for the profile of either the message author or specified user."""
        if ctx.invoked_subcommand is None:
            if user is None:
                user = ctx.message.author
                if check_profile_exists(ctx.message.author.id) is False:
                    ctx.send(
                        "QA Tester profile does not exist within PrismarineCo. Ltd.'s database. Please use `pr.profile init` to create a profile."
                    )
            else:
                try:
                    user = int(user)
                    user = self.client.get_user(user)
                    if user is None:
                        ctx.send(
                            "QA Tester profile does not exist within PrismarineCo. Ltd.'s database."
                        )
                    elif check_profile_exists(user.id) is False:
                        ctx.send(
                            "QA Tester profile does not exist within PrismarineCo. Ltd.'s database."
                        )
                except ValueError:
                    user = ctx.message.mentions[0]
            profile_select = select([__class__.table]).where(
                __class__.table.c.user_id == user.id
            )
            profile = __class__.c.execute(profile_select)
            profile = profile.fetchone()
            embed = discord.Embed(
                title=f"QA Tester #{profile[0]}'s Profile",
                color=discord.Color.dark_red(),
            )

            embed.set_thumbnail(url=user.avatar_url)
            for name, index in zip(
                (
                    "In-Game Name:",
                    "Level:",
                    "Friend Code:",
                    "Rainmaker Rank:",
                    "Tower Control Rank:",
                    "Splat Zones Rank:",
                    "Clam Blitz Rank:",
                    "Salmon Run Rank:",
                ),
                range(8),
            ):
                embed.add_field(name=name, value=profile[index + 1])
            await ctx.send(embed=embed)

    @profile.command()
    async def init(self, ctx):
        """Initialize a user profile."""
        profile = __class__.c.execute(
            select([__class__.table]).where(
                __class__.table.c.user_id == ctx.message.author.id
            )
        )
        profile = profile.fetchone()
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

    @profile.command()
    async def ign(self, ctx, *, name: str = None):
        """Update someone's IGN."""
        try:
            assert check_profile_exists(ctx.message.author.id) is True
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
        except AssertionError:
            ctx.send(
                "QA Tester profile does not exist within PrismarineCo. Ltd.'s database. To create a profile, use `pr.profile init`.'"
            )

    @profile.command()
    async def fc(self, ctx, *, friend_code):
        """Update someone's Friend Code."""
        try:
            assert check_profile_exists(ctx.message.author.id) is True
            friend_code = re.sub(r"\D", "", friend_code)
            if len(friend_code) != 12:
                message = "Command Failed - Friend Code must be 12 characters long, grouped into 3 sets of 4.\nExample: `-profile fc SW-1234-1234-1234`."
            else:
                p_1 = friend_code[0:3]
                p_2 = friend_code[4:7]
                p_3 = friend_code[8:11]
                friend_code = (
                    __class__.table.update(None)
                    .where(__class__.table.c.user_id == ctx.message.author.id)
                    .values(fc=f"SW-{p_1}-{p_2}-{p_3}")
                )
                __class__.c.execute(friend_code)
                message = "Friend Code successfully updated!"
            await ctx.send(message)
        except AssertionError:
            ctx.send(
                "QA Tester profile does not exist within PrismarineCo. Ltd.'s database. To create a profile, use `pr.profile init`.'"
            )

    @profile.command()
    async def level(self, ctx, *, level: int = None):
        """Update someone's level."""
        try:
            assert check_profile_exists(ctx.message.author.id) is True
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
        except AssertionError:
            ctx.send(
                "QA Tester profile does not exist within PrismarineCo. Ltd.'s database. To create a profile, use `pr.profile init`.'"
            )

    @profile.command()
    async def rank(self, ctx, gamemode: str = None, rank: str = None):
        """Update a person's rank in the database."""
        # fmt: off
        rank_list = (
            "C-", "C", "C+",
            "B-", "B", "B+",
            "A-", "A", "A+",
            "S", "S+0", "S+1",
            "S+2", "S+3", "S+4",
            "S+5", "S+6", "S+7",
            "S+8", "S+9", "X",
        )
        # fmt: on
        modes = {
            "Splat Zones": {
                "aliases": ("sz", "splatzones", "sz_rank"),
                "rlist": rank_list,
            },
            "Rainmaker": {
                "aliases": ("rm", "rainmaker", "rm_rank"),
                "rlist": rank_list,
            },
            "Tower Control": {
                "aliases": ("tc", "towercontrol", "tc_rank"),
                "rlist": rank_list,
            },
            "Clam Blitz": {
                "aliases": ("cb", "clamblitz", "cb_rank"),
                "rlist": rank_list,
            },
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
        try:
            assert check_profile_exists(ctx.message.author.id) is True
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
                            eval(  # pylint: disable=eval-used
                                str(__class__)
                                + """.c.execute((Profiler.table.update(None).where(Profiler.table.c.user_id == ctx.message.author.id).values("""
                                + value["aliases"][-1]
                                + """=changed_rank)))"""
                            )
                            await ctx.send(f"{key} rank updated!")
                            break
                    else:
                        await ctx.send(
                            "Command Failed - Gamemode was not and/or incorrectly specified."
                        )
        except AssertionError:
            ctx.send(
                "QA Tester profile does not exist within PrismarineCo. Ltd.'s database. To create a profile, use `pr.profile init`.'"
            )


def setup(client):
    """Add the module to the bot."""
    client.add_cog(Profiler(client))
    logging.info("Profiler Module Online.")
