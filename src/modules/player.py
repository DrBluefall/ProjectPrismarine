# Third-Party Imports

from discord.ext import commands


class Player(commands.Cog):

    def __init__(self, client):
        self.client = client
    
    @commands.group()
    async def player(self, ctx):
        pass

    @player.command()
    async def create_profile(self, ctx):
        self.client.dbh.add_profile(ctx.message.author.id)
        await ctx.send("Player profile created! :smiley:")
    
    @player.command()
    async def toggle_fa(self, ctx):
        await ctx.send(f"Free Agent Status set to `{self.client.dbh.toggle_free_agent(ctx.message.author.id)}`")

    @player.command()
    async def toggle_private(self, ctx):
        await ctx.send(f"Privacy Status set to `{self.client.dbh.toggle_private(ctx.message.author.id)}`")


def setup(client):
    client.add_cog(Player(client))