# Third-Party Imports

from discord.ext import commands


class Player(commands.Cog):

    def __init__(self, client):
        self.client = client



def setup(client):
    client.add_cog(Player(client))