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
    async def fc(self, ctx, *, friend_code):
        valid = self.client.dbh.update_fc(ctx.message.author.id, friend_code)
        if valid:
            await ctx.send("Friend code updated! :smiley:")
        else:
            await ctx.send("Command Failed - Invalid Friend Code passed.")
    

    @player.command()
    async def ign(self, ctx, *, ign):
        if any(
                (
                len(ign) > 10, 
                len(ign) < 1
                )
            ):
            await ctx.send("Command Failed - Invalid Name specified.")
        else:
            self.client.dbh.update_ign(ctx.message.author.id, ign)
            await ctx.send("In-Game Name updated! :smiley:")
    
    @player.command()
    async def level(self, ctx, level):
        self.client.dbh.update_level(ctx.message.author.id, level)
        await ctx.send("Level updated! :smiley:")
    
    @player.command()
    async def rank(self, ctx, mode, *, rank):
        updated = self.client.dbh.update_rank(ctx.message.author.id, mode, rank)
        if updated:
            await ctx.send("Rank updated! :smiley:")
        else:
            await ctx.send("Command Failed - Invalid Mode or Rank specified.")
    
    @player.command()
    async def position(self, ctx, position: int):
        try:
            self.client.dbh.update_position(ctx.message.author.id, position)
        except ValueError:
            await ctx.send("Command Failed - Invalid Position specified.")

    @player.command()
    async def toggle_fa(self, ctx):
        await ctx.send(f"Free Agent Status set to `{self.client.dbh.toggle_free_agent(ctx.message.author.id)}`")

    @player.command()
    async def toggle_private(self, ctx):
        await ctx.send(f"Privacy Status set to `{self.client.dbh.toggle_private(ctx.message.author.id)}`")


def setup(client):
    client.add_cog(Player(client))