"""Developer Administration commands."""
# Core Language Imports

import logging
import os
import sys
import platform
import subprocess

# Third-Party Imports

import psutil
import discord
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
        
    @developer.command()
    async def ping(self, ctx):
        await ctx.send("Client Latency: {}".format(round(self.client.latency * 1000, 3)))
    
    @developer.command()
    async def info(self, ctx):
        embed = discord.Embed(
            title="%s - System Information" % self.client.user.name,
            color=discord.Color.from_rgb(255, 0, 0)
        )
        process = psutil.Process(os.getpid())
        head = subprocess.check_output(['git', 'log', '-1', '--pretty=oneline']).decode('ascii').strip()
        system_info = platform.uname()
        embed.add_field(
            name="Memory Usage:",
            value=f"`{round(process.memory_info().rss / 1000000, 3)} MB ({round(process.memory_percent(), 3)}% of available resources)`"
        )
        embed.add_field(
            name="Revision Information:",
            value=f"Commit ID: `{head[:40]}`\n Message: {head[41:]}"
        )
        embed.add_field(
            name="Python Runtime Information:",
            value=f"`{platform.python_implementation()} {sys.version}`"
        )
        embed.add_field(
            name="Host Node:",
            value=f"{platform.node()}"
        )
        embed.set_thumbnail(url=self.client.user.avatar_url)
        await ctx.send(embed=embed)

def setup(client):
    client.add_cog(Developer(client))
            