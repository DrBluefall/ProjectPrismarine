"""Module containing Moderation cog."""
import logging
import asyncio
import discord
from discord.ext import commands


class Moderation(commands.Cog):
    """Contains all Moderation commands."""

    def __init__(self, client):
        """Init the Moderation cog."""
        self.client = client

    @commands.group(case_insensitive=True)
    async def mod(self, ctx):
        """Found module command group. Does nothing on it's own."""

    @commands.has_permissions(kick_members=True,
                              ban_members=True,
                              manage_messages=True,
                              manage_nicknames=True)
    @mod.command()
    async def help(self, ctx):
        """Moderation command documentation."""
        embed = discord.Embed(
            title=f"Project Prismarine - {__class__.__name__} Documentation",
            color=discord.Color.dark_red())

        for command in self.walk_commands():
            embed.add_field(name=ctx.prefix + command.qualified_name,
                            value=command.help)

        await ctx.send(embed=embed)

    @commands.has_permissions(manage_nicknames=True)
    @mod.command()
    async def changename(self, ctx, name_user, *, nickname: str):
        """
        Change a user's nickname.
Parameters:
    - User (User ID/@ mention): The user you wish to change the name of.
    - Nickname: The nickname you wish to set.
        """
        try:
            name_user = ctx.message.mentions[0]
        except IndexError:
            name_user = int(name_user)
            name_user = ctx.guild.get_member(name_user)
        await name_user.edit(reason=None, nick=nickname)
        await ctx.send(
            f"`{name_user}`'s nickname has been changed to `{nickname}`.")

    @commands.has_permissions(manage_messages=True)
    @mod.command()
    async def delete(self, ctx, amount: int = 10):
        """
        Purge a number of messages.
Parameters:
    - Amount (Integer): Number of messages to delete.
Returns:
    - A message displaying the number of deleted messages. Deletes itself after 10 seconds.
Will not work if:
    - The command user does not have the `manage messages` permission.
        """
        channel = self.client.get_channel(ctx.channel.id)
        deleted = await channel.purge(limit=amount)
        await ctx.send("{} message(s) have been deleted.".format(len(deleted)),
                       delete_after=10)

    @delete.error
    async def delete_error(self, ctx, error):
        """Error when delete doesn't work."""
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(
                "Command failed. Make sure you have the `manage_messages` permission in order to use this command."
            )

    @commands.has_permissions(ban_members=True)
    @mod.command()
    async def ban(self, ctx, banned_user, time: int = 0, *,
                  reason: str = None):
        """
        Ban a user.
Parameters:
    - User (User ID/@ mention): The user you wish to ban.
    - Time (Integer): The number of days worth of messages you wish to delete from the user in the guild. Maximum is 7.
    - Reason: The reason for the ban.
Will not work if:
    - A user is not specified.
    - The command user does not have the `ban members` permission.
        """

        try:
            banned_user = ctx.message.mentions[0]
        except IndexError:
            banned_user = int(banned_user)
            banned_user = self.client.get_user(banned_user)
        try:
            await ctx.guild.ban(user=banned_user,
                                reason=reason,
                                delete_message_days=time)
            await ctx.send(f"The ban hammer has been dropped on {banned_user}!"
                           )
        except asyncio.TimeoutError:
            await ctx.send(
                "Command failed. Make sure all necessary arguments are provided and/or correct."
            )

    @ban.error
    async def ban_error(self, ctx, error):
        """Error when ban doesn't work."""
        if isinstance(error,
                      (commands.BadArgument, commands.MissingPermissions)):
            await ctx.send(
                "Command failed. Make sure you have the `ban_members` permission in order to use this command, or have specified the correct arguments."
            )
            logging.info("%i - %s", ctx.guild.id, error)

    @commands.has_permissions(kick_members=True)
    @mod.command()
    async def kick(self, ctx, kicked_user, *, reason: str = None):
        """
        Kick a user.
Parameters:
    - User (User ID/@ mention): The user you wish to kick.
    - Reason: The reason for the kick.
Will not work if:
    - A user is not specified.
    - The command user does not have the `kick members` permission.
        """

        try:
            kicked_user = ctx.message.mentions[0]
        except IndexError:
            kicked_user = int(kicked_user)
            kicked_user = self.client.get_user(kicked_user)
        await ctx.guild.kick(user=kicked_user, reason=reason)
        await ctx.send(f"User {kicked_user} has been kicked.")

    @kick.error
    async def kick_error(self, ctx, error):
        """Error when kick doesn't work."""
        if isinstance(
                error,
            (commands.MissingRequiredArgument, commands.MissingPermissions)):
            await ctx.send(
                "Command failed. Make sure you have the `kick_members` permission in order to use this command, or have specified the user you want to kick using an @mention."
            )
            logging.info("%i - %s", ctx.guild.id, error)

    @commands.has_permissions(kick_members=True)
    @mod.command()
    async def prune(self, ctx, time: int = 30):
        """
        Prune the server.
Parameters:
    - Time (Integer): The amount of time a user has to be inactive for them to be pruned. Defaults to 30 days.

Note: This will only work on users without an assigned role.
        """
        pruned = await ctx.guild.prune_members(days=time,
                                               compute_prune_count="False")
        # await ctx.send("Prune executed.")
        await ctx.send(f"{pruned} member(s) have been pruned from the server.")


def setup(client):
    """Add the module to the bot."""
    client.add_cog(Moderation(client))
    logging.info("Moderation Module online.")
