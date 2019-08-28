# Third-Party Imports

from discord.ext import commands


class ScrimOrganization(commands.Cog):
    """Class made for organizing scrims."""

    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.group()
    async def scrim(self, ctx: commands.Context):
        pass

    @scrim.command()
    async def request(self, ctx: commands.Context, *, details):
        ret_code = self.client.dbh.add_scrim(ctx.message.author.id, details)

        if ret_code == 1:
            await ctx.send("Command Failed - User does not have a team.")
            return
        elif ret_code == 2:
            await ctx.send("Command Failed - Scrim request already registered into the database.")
            return
        elif ret_code == 3:
            await ctx.send("Command Failed - Team is currently being deleted.")
            return
        elif ret_code == 0:
            await ctx.send(
                f"Scrim registered! Your request will be active in the database, and you (along with other players) can view active requests with `{ctx.prefix}scrim active`. Good luck, and godspeed.")


def setup(client):
    client.add_cog(ScrimOrganization(client))
