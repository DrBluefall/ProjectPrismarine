"""Module containing all adminitstrative commands. DEVELOPER-ONLY."""
import logging
import discord
from discord.ext import commands


def is_main_guild(ctx):
    """Checks if the guild is the main one."""
    return ctx.guild.id == 561529218949971989


class System(commands.Cog):
    """Module containing all administrative commands. DEVELOPER-ONLY."""

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def ping(self, ctx):
        """Ping the user."""
        embed = discord.Embed(color=0xDE2E43)
        embed.add_field(
            name=f":ping_pong: Latency: `{round(self.client.latency*1000, ndigits=4)}ms`", value="\u200B"
        )
        await ctx.channel.send(embed=embed)

    @commands.command()
    async def user(self, ctx, member=None):
        """Get user info on a user."""
        if member is None:
            member = ctx.message.author
        else:
            try:
                member = int(member)
                member = ctx.guild.get_member(member)
            except ValueError:
                member = ctx.message.mentions[0]
        name = f"`{member.name}#{member.discriminator}`"
        await ctx.channel.send(
            f"""Discord ID: {name}
User ID: `{member.id}
Account Created: `{member.created_at} UTC`
Status: `{member.status}`
Joined Server At: `{member.joined_at} UTC`"""
        )

    @commands.is_owner()
    @commands.command()
    async def send(self, ctx, channel: str, *, content: str):
        """Send message to a channel as the bot."""
        channel = self.client.get_channel(int(channel))
        await channel.send(content)
        await ctx.send(f"Message sent to {channel}.")
        logging.info("Message sent to %s.", channel)

    @send.error
    async def send_error(self, ctx, error):
        """Error if the user of the command is not the bot owner."""
        if isinstance(error, (discord.ext.commands.errors.NotOwner)):
            await ctx.send(":warning: *You're not authorized to use this!* :warning:")

    @commands.check(is_main_guild)
    @commands.has_permissions(administrator=True)
    @commands.command()
    async def announce(self, ctx, *, text):
        """Make an announcement as the bot."""
        embed = discord.Embed(
            title=f"An Announcement from {ctx.message.author.display_name}...",
            description=text,
            color=discord.Color.blurple(),
        )
        embed.set_author(name="Unit 10008-RSP", icon_url=self.client.user.avatar_url)
        embed.set_footer(
            text=f"Solidarity, {ctx.message.author.display_name}.", icon_url=ctx.author.avatar_url
        )
        announce_channel = self.client.get_channel(561530381908836353)
        if ctx.message.mention_everyone:
            await announce_channel.send("@everyone")
        await announce_channel.send(embed=embed)

    @announce.error
    async def announce_error(self, ctx, error):
        """Error when announce is used by an unauthorized user"""
        if isinstance(error, (discord.ext.commands.errors.NotOwner)):
            await ctx.send(":warning: *You're not authorized to use this!* :warning:")

    @commands.is_owner()
    @commands.command()
    async def logout(self, ctx):
        """Quit the bot."""
        logging.info("Shutting down Project Prismarine...")
        await ctx.send("*Shutting down Project Prismarine...*")
        await self.client.logout()

    @logout.error
    async def logout_error(self, ctx, error):
        """Error if the person using the command is not the bot owner."""
        if isinstance(error, (discord.ext.commands.errors.NotOwner)):
            await ctx.send(":warning: *You're not authorized to use this!* :warning:")

    @commands.command()
    async def load(self, ctx, extension):
        """Loads the specified module within the bot."""
        self.client.load_extension("modules.%s", extension)
        await ctx.send("Module `%s` loaded.", extension)
        logging.info("%s module loaded.", extension)

    @load.error
    async def load_error(self, ctx, error):
        """Error if the specified module cannot be loaded."""
        if isinstance(error, discord.ext.commands.errors.CommandInvokeError):
            await ctx.send("Module could not be loaded. Make sure that the module name is correct, and is in the correct directory.")

    @commands.command()
    async def unload(self, ctx, extension):
        """Unloads the specified module within the bot."""
        self.client.unload_extension("modules.%s", extension)
        await ctx.send("Module `%s` unloaded.", extension)
        logging.info("%s module unloaded.", extension)

    @unload.error
    async def unload_error(self, ctx, error):
        """Error if the specified module cannot be unloaded."""
        if isinstance(error, discord.ext.commands.errors.CommandInvokeError):
            await ctx.send("Module could not be unloaded. Make sure that the module name is correct, and is in the correct directory.")

    @commands.command()
    async def reload(self, ctx, extension):
        """Reloads the specified module within the bot."""
        self.client.unload_extension("modules.%s", extension)
        self.client.load_extension("modules.%s", extension)
        await ctx.send("Module `%s` reloaded.", extension)
        logging.info("%s module reloaded.", extension)

    @reload.error
    async def reload_error(self, ctx, error):
        """Error if the specified module cannot be reloaded."""
        if isinstance(error, discord.ext.commands.errors.CommandInvokeError):
            await ctx.send("Module could not be reloaded. Make sure that the module name is correct, and is in the correct directory.")


def setup(client):
    """Adds the module to the bot."""
    client.add_cog(System(client))
    logging.info("System Module Online.")
