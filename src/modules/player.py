# Third-Party Imports

from discord.ext import commands


class Player(commands.Cog):

    def __init__(self, client):
        self.client = client
    
    @commands.group()
    async def player(self, ctx):
        pass

    @player.group()
    async def create_profile(self, ctx):
        self.client.dbh.add_profile(ctx.message.author.id)
        await ctx.send("""Player profile created! :smile:""")


def setup(client):
    client.add_cog(Player(client))