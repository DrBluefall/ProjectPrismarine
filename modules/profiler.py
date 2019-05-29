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
    """Module containing commands pertaining to managing user profiles."""

    def __init__(self, client):
        self.client = client

    @commands.group(invoke_without_command=True, case_insensitive=True, ignore_extra=False)
    async def profile(self, ctx, user=None):  # set up querying of other users' profiles
        db = sqlite3.connect("ProjectPrismarine.db")
        c = db.cursor()
        if ctx.invoked_subcommand is None:
            # Get the output from this query and turn it into an embed, listing the user's IGN, level, and ranks.
            c.execute("SELECT * FROM profile WHERE user_id = ?", (ctx.message.author.id,))
            profile = c.fetchone()
            embed = discord.Embed(
                title=f"QA Tester #{profile[0]}'s Profile",
                color=discord.Color.dark_red()
            )
            embed.set_thumbnail(url=ctx.message.author.avatar_url)
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
        # Implement check if the user already has a profile, likely by using an SQL query and seeing if it outputs None.
        db = sqlite3.connect("ProjectPrismarine.db")
        c = db.cursor()
        c.execute("INSERT OR IGNORE INTO profile(user_id, ign, fc, level, rm_rank, tc_rank, sz_rank, cb_rank, sr_rank) VALUES (:user_id, :ign, :fc, :level, :rm_rank, :tc_rank, :sz_rank, :cb_rank, :sr_rank) ",
                  {'user_id': ctx.message.author.id, 'ign': 'N/A', 'fc': 'SW-0000-0000-0000', 'level': 1, 'rm_rank': 'C-', 'tc_rank': 'C-', 'sz_rank': 'C-', 'cb_rank': 'C-', 'sr_rank': 'Intern'})
        db.commit()
        print(ctx.message.author.id)


def setup(client):
    """Adds the module to the bot."""
    client.add_cog(Profiler(client))
    logging.info("Profiler Module Online.")
