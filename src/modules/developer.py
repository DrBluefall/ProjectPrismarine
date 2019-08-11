"""Developer Administration commands."""
# Core Language Imports

import logging

# Third-Party Imports

from discord.ext import commands



class Developer(commands.Cog):
    """Developer commands to assist in the bot's administration and gathering debug info."""

    def __init__(self, client):
        self.client = client
    
    @commands.is_owner()
    @commands.group(aliases=["dev", "sudo"])
    async def developer(self, ctx):
        pass

    @developer.command()
    async def logout(self, ctx, fast='false'):
        truth_values = ['Y', 'YES', 'TRUE', '1', 'T']
        
        if fast.upper() not in truth_values:
            await ctx.send("Are you sure you wish to shutdown the bot?")
            msg = await self.client.wait_for('message', check=lambda m: m.author == ctx.message.author)
            
            if msg.content.upper() in truth_values:
                confirm = True
            else:
                confirm = False
            
            if confirm is True:
                await ctx.send("Understood. *Shutting down %s...*" % self.client.user.name)
                logging.warning("Shutting down %s...", self.client.user.name)
                await self.client.logout()
            else:
                await ctx.send("Understood. Aborting logout.")
        else:
            await ctx.send("Understood. *Shutting down %s...*" % self.client.user.name)
            logging.warning("Shutting down %s...", self.client.user.name)
            await self.client.logout()



def setup(client):
    client.add_cog(Developer(client))
            