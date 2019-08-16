# Third-Party Imports

from discord.ext import commands


class Team(commands.Cog):
    """Module for managing teams."""

    def __init__(self, client):
        self.client = client

    @commands.group()
    async def team(self, ctx):
        pass

def setup(client):
    client.add_cog(Team(client))