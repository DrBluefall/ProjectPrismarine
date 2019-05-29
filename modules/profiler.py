import logging
import discord
import sqlite3
from discord.ext import commands

db = sqlite3.connect("ProjectPrismarine.db")
c = db.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS profile(
user_id integer primary key,
ign text,
fc text,
level integer,
rm_rank text,
tc_rank text,
sz_rank text,
cb_rank text,
sr_rank text
)""")

# Note to self: Remember to commit database changes!!!!!


class Profiler(commands.Cog):
    """Module containing commands pertaining to managing and querying user profiles."""

    def __init__(self, client):
        self.client = client

    @commands.group(invoke_without_command=True, case_insensitive=True, ignore_extra=False)
    async def profile(self, ctx, user=None):
        """Profile command group. If run without a subcommand, it will query for the profile of either the message author or specified user."""
        db = sqlite3.connect("ProjectPrismarine.db")
        c = db.cursor()
        if ctx.invoked_subcommand is None:
            if user is None:
                user = ctx.message.author
            else:
                try:
                    user = int(user)
                    user = self.client.get_user(user)
                except ValueError:
                    user = ctx.message.mentions[0]
            c.execute("SELECT * FROM profile WHERE user_id = ?", (user.id,))
            profile = c.fetchone()
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
        db = sqlite3.connect("ProjectPrismarine.db")
        c = db.cursor()
        c.execute("SELECT * FROM profile WHERE user_id = ?", (ctx.message.author.id,))
        user = c.fetchone()
        if user is None:
            c.execute("INSERT OR IGNORE INTO profile(user_id, ign, fc, level, rm_rank, tc_rank, sz_rank, cb_rank, sr_rank) VALUES (:user_id, :ign, :fc, :level, :rm_rank, :tc_rank, :sz_rank, :cb_rank, :sr_rank) ",
                      {'user_id': ctx.message.author.id, 'ign': 'N/A', 'fc': 'SW-0000-0000-0000', 'level': 1, 'rm_rank': 'C-', 'tc_rank': 'C-', 'sz_rank': 'C-', 'cb_rank': 'C-', 'sr_rank': 'Intern'})
            db.commit()
            await ctx.send("QA Tester Profile Initialized. Thank you for choosing PrismarineCo. Laboratories.")
        else:
            await ctx.send("Existing QA Profile detected. Aborting initialization...")


def setup(client):
    """Adds the module to the bot."""
    client.add_cog(Profiler(client))
    logging.info("Profiler Module Online.")
