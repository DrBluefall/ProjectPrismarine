"""Module containing all adminitstrative commands. DEVELOPER-ONLY."""
import logging
import json
import asyncio
import discord
from discord.ext import commands, tasks
import dbl


class System(commands.Cog):
    """Contains all administrative commands. DEVELOPER-ONLY."""

    def __init__(self, client):
        """Init the System cog."""
        self.client = client
        self.dbl = dbl.Client(self.client, CONFIG["dbl_token"])
        if discord.ClientUser.id == 568469437284614174:  # pylint: disable=no-member
            self.update = self.update_stats.start()  # pylint: disable=no-member

    @tasks.loop()
    async def update_stats(self):
        """Update the stats of the server count."""
        while not self.client.is_closed():
            logging.info("Posting server count...")
            try:
                await self.dbl.post_guild_count()
                logging.info("Posted server count: %s", self.dbl.guild_count())
            except Exception as e:  # pylint: disable=broad-except, invalid-name
                logging.exception(
                    "Failed to post server count\n%s: %s",
                    type(e).__name__, e
                )
            await asyncio.sleep(900)

    @commands.group(case_insensitive=True)
    async def system(self, ctx):
        """System command group. Does nothing on it's own."""

    @system.command()
    async def ping(self, ctx):
        """
        Ping the user.

        Returns:
            - An embed displaying the client's latency.
        """
        embed = discord.Embed(color=0xDE2E43)
        embed.add_field(
            name=
            f":ping_pong: Latency: `{round(self.client.latency*1000, ndigits=4)}ms`",
            value="\u200B",
        )
        await ctx.channel.send(embed=embed)

    @system.command()
    async def user(self, ctx, member=None):
        """
        Get user info on a user.

        Parameters:
            - User (User ID/@ mention): The user to retrieve info on. Defaults to the message author.
        Returns:
            - An embed containing miscellaneous info on a user.
        """
        if member is None:
            member = ctx.message.author
        else:
            try:
                member = int(member)
                member = self.client.get_user(member)
            except ValueError:
                member = ctx.message.mentions[0]
        name = f"`{member.name}#{member.discriminator}`"
        if member.bot is False:
            user_type = "`User`"
        else:
            user_type = "`Bot`"
        embed = discord.Embed(
            title=f"User Report: {member.display_name}",
            color=discord.Color.blurple()
        )
        embed.add_field(name="Discord ID:", value=name, inline=True)
        embed.add_field(name="User ID:", value=f"`{member.id}`", inline=True)
        embed.add_field(
            name="Account Created At:",
            value=f"`{member.created_at}`",
            inline=True
        )
        embed.add_field(name="Account Type:", value=user_type, inline=True)
        embed.set_thumbnail(url=member.avatar_url)
        embed.set_footer(
            text=
            f"Date Generated: {ctx.message.created_at}, Requested By: {ctx.message.author}"
        )
        await ctx.channel.send(embed=embed)

    @commands.is_owner()
    @system.command()
    async def send(self, ctx, channel, *, content: str):
        """
        Send message to a channel as the bot.

        Parameters:
            - Channel (Channel ID only): The channel to send the message to.
            - Content: The message to send.
        Returns:
            - A sent message to the specified channel.
            - A confirmation message where the command was invoked from.
        Will not work if:
            - The channel ID is not provided and/or invalid.
        """
        channel = int(channel)
        channel = self.client.get_channel(channel)
        await channel.send(content)
        await ctx.send(f"Message sent to {channel}.")
        logging.info("Message sent to %s.", channel)

    @send.error
    async def send_error(self, ctx, error):
        """Error if the user of the command is not the bot owner."""
        if isinstance(error, (discord.ext.commands.errors.NotOwner)):
            await ctx.send(
                ":warning: *You're not authorized to use this!* :warning:"
            )

    @commands.check(lambda ctx: ctx.guild.id == 561529218949971989)
    @commands.has_permissions(administrator=True)
    @system.command()
    async def announce(self, ctx, *, text):
        """
        Make an announcement as the bot.

        Parameters:
            - Text: The announcement to be made. If the message contains an @everyone mention, the bot will automatically ping everyone.
        Returns:
            - An announcement in an embed in the support server announcement channel.
        Will not work if:
            - The command is invoked outside the support server.

        """
        embed = discord.Embed(
            title=f"An Announcement from {ctx.message.author.name}...",
            description=text,
            color=discord.Color.blurple(),
        )
        embed.set_author(
            name="Unit 10008-RSP", icon_url=self.client.user.avatar_url
        )
        embed.set_footer(
            text=f"Solidarity, {ctx.message.author.display_name}.",
            icon_url=ctx.author.avatar_url
        )
        announce_channel = self.client.get_channel(583704659080773642)
        if ctx.message.mention_everyone:
            await announce_channel.send("@everyone")
        await announce_channel.send(embed=embed)

    @announce.error
    async def announce_error(self, ctx, error):
        """Error when announce is used by an unauthorized user."""
        if isinstance(error, (discord.ext.commands.errors.NotOwner)):
            await ctx.send(
                ":warning: *You're not authorized to use this!* :warning:"
            )
        else:
            print(error)

    @system.command()
    async def info(self, ctx):
        """
        Show info from Discord Bot List in an embed.

        Returns:
            - An embedded image of a Discord Bot List widget containing info about the bot.
        """
        embed = discord.Embed(color=discord.Color.blurple())
        embed.set_image(
            url=await
            self.dbl.generate_widget_large(bot_id="568469437284614174")
        )
        await ctx.send(embed=embed)

    @commands.is_owner()
    @system.command()
    async def logout(self, ctx):
        """Quit the bot."""
        logging.info("Shutting down Project Prismarine...")
        await ctx.send("*Shutting down Project Prismarine...*")
        await self.client.logout()

    @logout.error
    async def logout_error(self, ctx, error):
        """Error if the person using the command is not the bot owner."""
        if isinstance(error, (discord.ext.commands.errors.NotOwner)):
            await ctx.send(
                ":warning: *You're not authorized to use this!* :warning:"
            )

    @commands.check(
        lambda ctx: ctx.message.author.id == 490650609641324544 \
        or ctx.message.author.id == 571494333090496514
    )
    @system.command()
    async def help(self, ctx):
        """System command documentation."""
        embed = discord.Embed(
            title=f"Project Prismarine - {__class__.__name__} Documentation",
            color=discord.Color.dark_red()
        )
        for command in self.walk_commands():
            embed.add_field(
                name=ctx.prefix + command.qualified_name, value=command.help
            )
        await ctx.send(embed=embed)


with open("config.json", "r") as infile:
    CONFIG = json.load(infile)


def setup(client):
    """Add the module to the bot."""
    client.add_cog(System(client))
    logging.info("System Module Online.")
