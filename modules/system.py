import discord
from discord.ext import commands
import os


class System(commands.Cog):

    def __init__(self, CLIENT):
        self.CLIENT = CLIENT

    @commands.command()
    async def ping(ctx):
        """Ping the user."""
        embed = discord.Embed(color=0xDE2E43)
        embed.add_field(
            name=f":ping_pong: Latency: `{round(CLIENT.latency*1000, ndigits=4)}ms`", value="\u200B"
        )
        await ctx.channel.send(embed=embed)

    @commands.command()
    async def user(ctx, member: discord.User = None):
        """Get user info on a user."""
        if member is None:
            member = ctx.message.author
        else:
            member = ctx.message.mentions[0]
        name = f"`{member.name}#{member.discriminator}`"
        await ctx.channel.send(
            f"""Discord ID: {name}
    User ID: `{ctx.message.author.id}`
    Account Created: `{member.created_at} UTC`
    Status: `{member.status}`
    Joined Server At: `{member.joined_at} UTC`"""
        )

    @commands.is_owner()
    @commands.command()
    async def send(ctx, channel: str, *, content: str):
        """Send message to a channel as the bot."""
        channel = CLIENT.get_channel(int(channel))
        await channel.send(content)
        await ctx.send(f"Message sent to {channel}.")
        logging.info("Message sent to %s.", channel)

    @send.error
    async def send_error(ctx, error):
        if isinstance(error, (discord.ext.commands.errors.NotOwner)):
            await ctx.send(":warning: *You're not authorized to use this!* :warning:")

    def is_main_guild(ctx):
        return ctx.guild.id == 561529218949971989

    @commands.check(is_main_guild)
    @commands.has_permissions(administrator=True)
    @commands.command()
    async def announce(ctx, *, text):
        """Make an announcement as the bot."""
        embed = discord.Embed(
            title=f"An Announcement from {ctx.message.author.display_name}...",
            description=text,
            color=discord.Color.blurple(),
        )
        embed.set_author(name="Unit 10008-RSP", icon_url=CLIENT.user.avatar_url)
        embed.set_footer(
            text=f"Solidarity, {ctx.message.author.display_name}.", icon_url=ctx.author.avatar_url
        )
        announce_channel = CLIENT.get_channel(561530381908836353)
        if ctx.message.mention_everyone:
            await announce_channel.send("@everyone")
        await announce_channel.send(embed=embed)

    @announce.error
    async def send_error(ctx, error):
        """Error when announce is used by an unauthorized user"""
        if isinstance(error, (discord.ext.commands.errors.NotOwner)):
            await ctx.send(":warning: *You're not authorized to use this!* :warning:")

    @commands.is_owner()
    @commands.command()
    async def logout(ctx):
        """Quit the bot."""
        logging.info("Shutting down Project Prismarine...")
        await ctx.send("*Shutting down Project Prismarine...*")
        await CLIENT.logout()

    @logout.error
    async def logout_error(ctx, error):
        if isinstance(error, (discord.ext.commands.errors.NotOwner)):
            await ctx.send(":warning: *You're not authorized to use this!* :warning:")

    @commands.command()
    async def load(self, ctx, extension):
        """Loads the specified module within the bot."""
        CLIENT.load_extension(f"modules.{extension}")
        await ctx.send(f"Module `{extension}` loaded.")
        logging.info(f"{extension} module loaded.")

    @load.error()
    async def load_error(ctx, error):
        if isinstance(error, discord.ext.commands.errors.CommandInvokeError):
            await ctx.send("Module could not be loaded. Make sure that the module name is correct, and is in the correct directory.")

    @commands.command()
    async def unload(self, ctx, extension):
        """Unloads the specified module within the bot."""
        CLIENT.unload_extension(f"modules.{extension}")
        await ctx.send(f"Module `{extension}` unloaded.")
        logging.info(f"{extension} module unloaded.")

    @unload.error()
    async def unload_error(ctx, error):
        if isinstance(error, discord.ext.commands.errors.CommandInvokeError):
            await ctx.send("Module could not be unloaded. Make sure that the module name is correct, and is in the correct directory.")

    @commands.command()
    async def reload(self, ctx, extension):
        """Reloads the specified module within the bot."""
        CLIENT.unload_extension(f"modules.{extension}")
        CLIENT.load_extension(f"modules.{extension}")
        await ctx.send(f"Module `{extension}` reloaded.")
        logging.info(f"{extension} module reloaded.")

    @reload.error()
    async def reload_error(ctx, error):
        if isinstance(error, discord.ext.commands.errors.CommandInvokeError):
            await ctx.send("Module could not be unloaded. Make sure that the module name is correct, and is in the correct directory.")


def setup(CLIENT):
    CLIENT.add_cog(System(CLIENT))
