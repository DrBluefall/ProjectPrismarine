"""Module containing the Profiler cog."""
import logging
import re
from io import BytesIO
import discord
from discord.ext import commands
from sqlalchemy import select
from bin.loadout import Loadout, decode
from core import DBHandler


class SQLEngine(DBHandler):
    """Contains the methods to abstract queries for the Profiler. Documented in: `pr.profile help`"""

    def __init__(self):
        """Init SQLEngine."""
        super().__init__()
        self.table = self.get_table("main", "profile")

    def check_profile_exists(self, user_id):
        """Check if a profile exists in the database or not."""
        profile = self.get_db("main").execute(
            select([self.table]). \
            where(self.table.columns["user_id"] == user_id)
        ).fetchone()

        return profile is not None

    def create_profile_embed(self, user):
        """Create profile embed."""
        profile = self.get_db("main").execute(
            select([self.table]). \
            where(self.table.columns["user_id"] == user.id)
        ).fetchone()

        embed = discord.Embed(
            title=f"QA Tester #{profile[0]}'s Profile",
            color=discord.Color.dark_red()
        )

        embed.set_thumbnail(url=user.avatar_url)
        for name, index in zip(
            (
                "In-Game Name:", "Friend Code:", "Level:", "Rainmaker Rank:",
                "Tower Control Rank:", "Splat Zones Rank:", "Clam Blitz Rank:",
                "Salmon Run Rank:"
            ), range(8)
        ):
            embed.add_field(name=name, value=profile[index + 1])

        if profile["loadout_string"] is not None:
            loadout = self.create_loadout_image(profile["loadout_string"])
            embed.set_image(url="attachment://loadout.png")

        return embed, loadout

    @staticmethod
    async def no_profile(ctx):
        """Help function that sends a message telling the user they have no profile."""
        await ctx.send(
            f"QA Tester profile does not exist within PrismarineCo. Ltd.'s database. To create a profile, use `{ctx.prefix}profile init`.'"
        )

    @staticmethod
    def create_loadout_image(loadout_string):
        """Generate loadout image from string."""
        loadout = loadout_string
        loadout = decode(loadout)
        loadout = Loadout().convert_loadout(loadout)
        with Loadout().generate_loadout_image(loadout) as loadout:
            out_buffer = BytesIO()
            loadout.save(out_buffer, "png")
            out_buffer.seek(0)

        loadout = discord.File(fp=out_buffer, filename="loadout.png")
        return loadout


class Profiler(commands.Cog, SQLEngine):
    """Contains all commands pertaining to managing and querying user profiles."""

    def __init__(self, client):
        """Init the Profiler cog."""
        super().__init__()
        self.client = client

    @commands.group(
        invoke_without_command=True, case_insensitive=True, ignore_extra=False
    )
    async def profile(self, ctx, user=None):
        """
        Profile command group. If run without a subcommand, it will query for the profile of either the message author or specified user.

        Parameters:
            - User (User ID/@ mention): The user to query for. Defaults to the message author.

        Will not work if:
            - The user in question doesn't have a profile.

        """
        if ctx.invoked_subcommand:
            return

        if user is None:
            user = ctx.message.author
        else:
            try:
                user = self.client.get_user(int(user))
            except ValueError:
                user = ctx.message.mentions[0]

        if user is None or self.check_profile_exists(user.id) is False:
            await self.no_profile(ctx)
        else:
            embed, loadout = self.create_profile_embed(user)
            await ctx.send(embed=embed, file=loadout)

    @profile.command()
    async def init(self, ctx):
        """Initialize a user profile. If your profile already exists, it will not create a new one."""
        if self.check_profile_exists(ctx.message.author.id):
            message = "Existing QA Profile detected. Aborting initialization..."
        else:
            self.rec_init_entry(ctx)
            message = "Quality Assurance Tester Profile initialized. Thank you for choosing PrismarineCo. Laboratories."

        await ctx.send(message)

    @profile.command()
    async def ign(self, ctx, *, name: str = None):
        """
        Update your in-game name.

        Parameters:
            - IGN: The in-game name you wish to set. (Note: There is a 10-character limit on your name, and it can't be blank, either.)

        """
        if self.check_profile_exists(ctx.message.author.id):
            if name is None:
                message = "Command Failed - No IGN specified."

            elif 1 <= len(name) <= 10:
                self.rec_ign_entry(ctx, name)
                message = "IGN successfully updated!"

            else:
                message = "Command Failed - IGN character limit is set at 10."

            await ctx.send(message)
        else:
            await __class__.no_profile(ctx)

    @profile.command()
    async def fc(self, ctx, *, friend_code):  # pylint: disable=invalid-name
        """
        Update your friend code.

        Parameters:
            - Friend Code: the friend code for your profile. This must be 12 characters long, and integers only.

        """
        if self.check_profile_exists(ctx.message.author.id):
            friend_code = re.sub(r"\D", "", friend_code)

            if len(friend_code) != 12:
                message = "Command Failed - Friend Code must be 12 characters long, grouped into 3 sets of 4.\nExample: `-profile fc SW-1234-1234-1234`."

            else:
                self.rec_fc_entry(ctx, friend_code)
                message = "Friend Code successfully updated!"

            await ctx.send(message)
        else:
            await __class__.no_profile(ctx)

    @profile.command()
    async def level(self, ctx, *, level: int = None):
        """
        Update your level.

        Parameters:
            - Level (Integer): The level you wish to set.

        """
        if self.check_profile_exists(ctx.message.author.id):

            if level is None:
                message = "Command Failed - No level specified."

            else:
                self.rec_level_entry(ctx, level)
                message = "Level successfully updated!"

            await ctx.send(message)
        else:
            await __class__.no_profile(ctx)

    @profile.command()
    async def rank(self, ctx, gamemode: str = None, rank: str = None):
        """
        Update your rank in the profile database.

        Parameters:
            - Gamemode: The game mode you wish to set your rank in. Valid names include mode initials (i.e. tc, sz, rm, cb), the full names (i.e. `towercontrol`, `splatzones`, `rainmaker`, `clamblitz`), or the initials followed by "_rank" (i.e. `sz_rank`, `tc_rank`, `cb_rank`, `rm_rank`).
            - Rank: The rank you wish to set. (Note: X Power is currently not supported. Sorry about that :P)

        """
        modes = self.get_modes()

        if self.check_profile_exists(ctx.message.author.id):
            if gamemode is None:
                message = "Command Failed - Argument not specified."
            else:
                for key, value in modes.items():
                    found, message = self.rec_try_rank_entry(
                        ctx, gamemode, key, value, rank
                    )
                    if found:
                        break
                else:
                    message = "Command Failed - Gamemode was not and/or incorrectly specified."

            await ctx.send(message)
        else:
            await __class__.no_profile(ctx)

    @profile.command()
    async def loadout(self, ctx, string: str = None):
        """
        Update your loadout with a loadout.ink link.

        Parameters:
            - loadout.ink link: The link to your loadout. Use `https://selicia.github.io/en_US/#0000000000000000000000000` to set your loadout.

        """
        if self.check_profile_exists(ctx.message.author.id):
            if string is not None and len(string) == 58:
                self.rec_loadout_string_entry(ctx, string[33:])
                message = "Loadout updated!"
            else:
                message = "Command failed - Loadout link is invalid."

            await ctx.send(message)
        else:
            await __class__.no_profile(ctx)

    @profile.command()
    async def help(self, ctx):
        """Profiler command documentation."""
        embed = discord.Embed(
            title=f"Project Prismarine - {__class__.__name__} Documentation",
            color=discord.Color.dark_red()
        )
        for command in self.walk_commands():
            embed.add_field(
                name=ctx.prefix + command.qualified_name, value=command.help
            )
        await ctx.send(embed=embed)

    def rec_init_entry(self, ctx):
        """Record the new profile in the database."""
        self.get_db("main").execute(
            self.table. \
            insert(None). \
            values(
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
        )

    def rec_ign_entry(self, ctx, name):
        """Record the ign in the database."""
        self.get_db("main").execute(
            self.table. \
            update(None). \
            where(self.table.columns["user_id"] == ctx.message.author.id). \
            values(ign=name)
        )

    def rec_fc_entry(self, ctx, fc_sw):
        """Record the fc in the database."""
        self.get_db("main").execute(
            self.table. \
            update(None). \
            where(self.table.columns["user_id"] == ctx.message.author.id). \
            values(fc=f"SW-{fc_sw[0:4]}-{fc_sw[4:8]}-{fc_sw[8:12]}")
        )

    def rec_level_entry(self, ctx, level):
        """Record the level in the database."""
        self.get_db("main").execute(
            self.table. \
            update(None). \
            where(self.table.columns["user_id"] == ctx.message.author.id). \
            values(level=level)
        )

    def rec_try_rank_entry(self, ctx, gamemode, key, value, rank):  # pylint: disable=too-many-arguments, unused-argument
        """Record the rank in the database."""
        if gamemode.lower() in value["aliases"]:

            changed_rank = self.change_rank(rank, value["rlist"])

            if changed_rank is None:
                message = "Command Failed - Rank was not and/or incorrectly specified."
            else:
                self.get_db("main").execute(
                    self.table. \
                    update(None). \
                    where(self.table.columns["user_id"] == ctx.message.author.id). \
                    values(**{value["aliases"][-1]: changed_rank})
                )
                message = f"{key} rank updated!"

            return True, message
        return False, 0

    def rec_loadout_string_entry(self, ctx, string: str = None):
        """Record a user's loadout.ink string into the database."""
        self.get_db("main").execute(
            self.table. \
            update(None). \
            where(self.table.columns["user_id"] == ctx.message.author.id). \
            values(loadout_string=string)
        )

    @staticmethod
    def change_rank(rank, rlist):
        """Change a rank given the rlist."""
        if rank.upper() in rlist:
            changed_rank = rank.upper()
        elif rank.capitalize() in rlist:
            changed_rank = rank.capitalize()
        else:
            changed_rank = None
        return changed_rank

    @staticmethod
    def get_modes():
        """Get modes."""
        rank_list = (
            "C-", "C", "C+", "B-", "B", "B+", "A-", "A", "A+", "S", "S+0",
            "S+1", "S+2", "S+3", "S+4", "S+5", "S+6", "S+7", "S+8", "S+9", "X"
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


def setup(client):
    """Add the module to the bot."""
    client.add_cog(Profiler(client))
    logging.info("Profiler Module Online.")
