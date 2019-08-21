"""Developer Administration commands."""
# Core Language Imports

import logging
import os
import platform
import subprocess
from datetime import datetime

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
        """Developer commands to assist in the bot's administration and gathering debug info."""

    @developer.command()
    async def logout(self, ctx, fast='false'):
        """Shutdown the bot. To skip the prompt, pass `y` for the `fast` argument."""
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
        """Get the latency of the bot."""
        await ctx.send("Client Latency: {}".format(round(self.client.latency * 1000, 3)))
    
    @developer.command()
    async def info(self, ctx):
        """Generate a report with data on the bot's current runtime."""
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
            value=f"`{platform.python_implementation()} {platform.python_version()} ({platform.python_build()[0]}, {platform.python_build()[1]})\n[{platform.python_compiler()}]`"
        )
        embed.add_field(
            name="Host Data:",
            value=f"Node Name: `{platform.node()}`\n Operating System: {platform.version()}"
        )
        embed.add_field(
            name="Operation Time:",
            value=f"{datetime.now() - self.client.start_time}"
        )
        embed.set_thumbnail(url=self.client.user.avatar_url)
        await ctx.send(embed=embed)
    
    @developer.command()
    async def user(self, ctx, user=None):
        """Generate a report with data on a user."""
        if user is None:
            user = ctx.message.author
        else:
            try:
                user = ctx.message.mentions[0]
            except IndexError:
                try:
                    user = await self.client.fetch_user(int(user))
                except (ValueError, discord.NotFound):
                    await ctx.send("Command failed - Invalid User specified.")
        
        embed = discord.Embed(
            title=f"User Report - {user.display_name}",
            color=discord.Color.from_rgb(255, 0, 0)
        )
        embed.add_field(
            name="Name:",
            value=f"`{user.name}#{user.discriminator}`"
        )
        embed.add_field(
            name="Discord ID:",
            value=f"`{user.id}`"
        )
        embed.add_field(
            name="Creation Date",
            value=f"`{user.created_at} UTC`"
        )
        
        embed.add_field(
            name="Account Type:",
            value=('`Bot`' if user.bot else "`User`")
        )

        embed.set_thumbnail(url=user.avatar_url)
        await ctx.send(embed=embed)

def setup(client):
    client.add_cog(Developer(client))
            