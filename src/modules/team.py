# Third-Party Imports

from discord.ext import commands


class Team(commands.Cog):
    """Module for managing teams."""

    def __init__(self, client):
        self.client = client

    @commands.group()
    async def team(self, ctx):
        pass

    @team.command()
    async def create(self, ctx, name: str = None):
        """Create a brand-new team."""

        await ctx.send("Team creation in progress...")
        if name is None:
            await ctx.send("What will be the name of your new team?")
            name = await self.client.wait_for('message', timeout=60, check=lambda m: m.author == ctx.message.author)
        
        res = self.client.dbh.new_team(ctx.message.author.id, name)
        if res is None:
            await ctx.send("Command Failed - Every user may only captain one team. If you wish to captain a new team, please delete your current team or assign it a new captain.")
        else:
            await ctx.send(
                f"""Team created! Your team can be queried by your user ID: `{res[0]}`. You can get this at any time by enabling `Developer Mode` in your settings, and right-clicking on your icon in a channel or in the right sidebar.
                \rThat's all for now. Good luck and godspeed.""")

def setup(client):
    client.add_cog(Team(client))