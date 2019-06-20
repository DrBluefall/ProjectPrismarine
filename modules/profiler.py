"""Holds the profile cog."""
import logging
import re
import discord
from discord.ext import commands
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, select


class SQLEngine:
    """Class containing the SQLEngine."""

    main_db = create_engine("sqlite:///ProjectPrismarine.db")
    metadata = MetaData(main_db)
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
        Column("loadout_string", String),
    )

    metadata.create_all()
    c = main_db.connect()

    @classmethod
    def check_profile_exists(cls, user_id):
        """Check if a profile exists in the database or not."""
        profile = cls.c.execute(
            select([cls.table
                    ]).where(cls.table.c.user_id == user_id)).fetchone()

        return profile is not None

    @classmethod
    def create_profile_embed(cls, user):
        """Create profile embed."""
        profile_select = select([cls.table
                                 ]).where(cls.table.c.user_id == user.id)
        profile = cls.c.execute(profile_select)
        profile = profile.fetchone()

        embed = discord.Embed(title=f"QA Tester #{profile[0]}'s Profile",
                              color=discord.Color.dark_red())

        embed.set_thumbnail(url=user.avatar_url)
        for name, index in zip(
            (
                "In-Game Name:",
                "Friend Code:",
                "Level:",
                "Rainmaker Rank:",
                "Tower Control Rank:",
                "Splat Zones Rank:",
                "Clam Blitz Rank:",
                "Salmon Run Rank:",
            ),
                range(8),
        ):
            embed.add_field(name=name, value=profile[index + 1])
        return embed

    @staticmethod
    async def no_profile(ctx):
        """Help function that sends a message telling the user they have no profile."""
        await ctx.send(
            f"QA Tester profile does not exist within PrismarineCo. Ltd.'s database. To create a profile, use `{ctx.prefix}profile init`.'"
        )


class Profiler(commands.Cog, SQLEngine):
    """Module containing commands pertaining to managing and querying user profiles."""

    def __init__(self, client):
        """Initialize the Profiler cog."""
        super().__init__()
        self.client = client

    @commands.group(invoke_without_command=True,
                    case_insensitive=True,
                    ignore_extra=False)
    async def profile(self, ctx, user=None):
        """Profile command group. If run without a subcommand, it will query for the profile of either the message author or specified user."""
        if ctx.invoked_subcommand:
            return

        if user is None:
            user = ctx.message.author
        else:
            try:
                user = self.client.get_user(int(user))
            except ValueError:
                user = ctx.message.mentions[0]

        if user is None or __class__.check_profile_exists(user.id) is False:
            await __class__.no_profile(ctx)
        else:
            await ctx.send(embed=__class__.create_profile_embed(user))

    @profile.command()
    async def init(self, ctx):
        """Initialize a user profile."""
        if __class__.check_profile_exists(ctx.message.author.id):
            message = "Existing QA Profile detected. Aborting initialization..."
        else:
            Record.init_entry(ctx)
            message = "Quality Assurance Tester Profile initialized. Thank you for choosing PrismarineCo. Laboratories."

        await ctx.send(message)

    @profile.command()
    async def ign(self, ctx, *, name: str = None):
        """Update someone's IGN."""
        if __class__.check_profile_exists(ctx.message.author.id):
            if name is None:
                message = "Command Failed - No IGN specified."

            elif 1 <= len(name) <= 10:
                Record.ign_entry(ctx, name)
                message = "IGN successfully updated!"

            else:
                message = "Command Failed - IGN character limit is set at 10."

            await ctx.send(message)
        else:
            await __class__.no_profile(ctx)

    @profile.command()
    async def fc(self, ctx, *, friend_code):  # pylint: disable=invalid-name
        """Update someone's Friend Code."""
        if __class__.check_profile_exists(ctx.message.author.id):
            friend_code = re.sub(r"\D", "", friend_code)

            if len(friend_code) != 12:
                message = "Command Failed - Friend Code must be 12 characters long, grouped into 3 sets of 4.\nExample: `-profile fc SW-1234-1234-1234`."

            else:
                Record.fc_entry(ctx, friend_code)
                message = "Friend Code successfully updated!"

            await ctx.send(message)
        else:
            await __class__.no_profile(ctx)

    @profile.command()
    async def level(self, ctx, *, level: int = None):
        """Update someone's level."""
        if __class__.check_profile_exists(ctx.message.author.id):

            if level is None:
                message = "Command Failed - No level specified."

            else:
                Record.level_entry(ctx, level)
                message = "Level successfully updated!"

            await ctx.send(message)
        else:
            await __class__.no_profile(ctx)

    @profile.command()
    async def rank(self, ctx, gamemode: str = None, rank: str = None):
        """Update a person's rank in the database."""
        modes = get_modes()

        if __class__.check_profile_exists(ctx.message.author.id):
            if gamemode is None:
                message = "Command Failed - Argument not specified."
            else:
                for key, value in modes.items():
                    found, message = Record.try_rank_entry(
                        gamemode, key, value, rank)
                    if found:
                        break
                else:
                    message = "Command Failed - Gamemode was not and/or incorrectly specified."

            await ctx.send(message)
        else:
            await __class__.no_profile(ctx)


class Record(Profiler):
    """Holds the staticmethods that record profile options into the database."""

    @classmethod
    def init_entry(cls, ctx):
        """Record the new profile in the database."""
        ins = cls.table.insert(None).values(
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
        cls.c.execute(ins)

    @classmethod
    def ign_entry(cls, ctx, name):
        """Record the ign in the database."""
        ign = (cls.table.update(None).where(
            cls.table.c.user_id == ctx.message.author.id).values(ign=name))
        cls.c.execute(ign)

    @classmethod
    def fc_entry(cls, ctx, friend_code):
        """Record the fc in the database."""
        p_1, p_2, p_3 = friend_code[0:4], friend_code[4:8], friend_code[8:12]
        friend_code = (cls.table.update(None).where(
            cls.table.c.user_id == ctx.message.author.id).values(
                fc=f"SW-{p_1}-{p_2}-{p_3}"))
        cls.c.execute(friend_code)

    @classmethod
    def level_entry(cls, ctx, level):
        """Record the level in the database."""
        level = (cls.table.update(None).where(
            cls.table.c.user_id == ctx.message.author.id).values(level=level))
        cls.c.execute(level)

    @classmethod
    def try_rank_entry(cls, gamemode, key, value, rank):
        """Record the rank in the database."""
        if gamemode.lower() in value["aliases"]:

            if rank.upper() in value["rlist"]:
                changed_rank = rank.upper()
            elif rank.capitalize() in value["rlist"]:
                changed_rank = rank.capitalize()
            else:
                changed_rank = None
                message = "Command Failed - Rank was not and/or incorrectly specified."

            if changed_rank is not None:
                eval(  # pylint: disable=eval-used
                    "cls.c.execute((cls.table.update(None).where(cls.table.c.user_id==ctx.message.author.id).values({}=changed_rank)))"
                    .format(value["aliases"][-1]))
                message = f"{key} rank updated!"
            return True, message
        return False, None


def setup(client):
    """Add the module to the bot."""
    client.add_cog(Profiler(client))
    logging.info("%s Module Online.", Profiler.__name__)


def get_modes():
    """Get modes."""
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
        "Splat Zones": {
            "aliases": ("sz", "splatzones", "sz_rank"),
            "rlist": rank_list
        },
        "Rainmaker": {
            "aliases": ("rm", "rainmaker", "rm_rank"),
            "rlist": rank_list
        },
        "Tower Control": {
            "aliases": ("tc", "towercontrol", "tc_rank"),
            "rlist": rank_list
        },
        "Clam Blitz": {
            "aliases": ("cb", "clamblitz", "cb_rank"),
            "rlist": rank_list
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
    return modes
