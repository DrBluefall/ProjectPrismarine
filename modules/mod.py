"""Module containing all moderator-usable commands."""
import logging
import asyncio
from discord.ext import commands


class Moderation(commands.Cog):
    """Module containing all moderator-usable commands."""

    def __init__(self, client):
        self.client = client

    @commands.has_permissions(manage_nicknames=True)
    @commands.command()
    async def changename(self, ctx, name_user, *, nickname: str):
        """Change user's nick."""
        try:
            name_user = ctx.message.mentions[0]
        except IndexError:
            name_user = int(name_user)
            name_user = self.client.get_user(name_user)  # CLIENT should be self.client
        await name_user.edit(reason=None, nick=nickname)
        await ctx.send(f"`{name_user}`'s nickname has been changed to `{nickname}`.")

    @commands.has_permissions(manage_messages=True)
    @commands.command()
    async def delete(self, ctx, amount: int = 10):
        """Purge a number of messages."""
        channel = self.client.get_channel(ctx.channel.id)  # CLIENT should be self.client
        deleted = await channel.purge(limit=amount)
        await ctx.send("{} message(s) have been deleted.".format(len(deleted)), delete_after=10)

    @delete.error
    async def delete_error(self, ctx, error):
        """Error when delete doesn't work."""
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(
                "Command failed. Make sure you have the `manage_messages` permission in order to use this command."
            )

    @commands.has_permissions(ban_members=True)
    @commands.command()
    async def ban(self, ctx, banned_user, time: int = 0, *, reason: str = None):
        """Ban a user."""
        try:
            banned_user = ctx.message.mentions[0]
        except IndexError:
            banned_user = self.client.get_user(banned_user)
        try:
            await ctx.guild.ban(user=banned_user, reason=reason, delete_message_days=time)
            await ctx.send(f"The ban hammer has been dropped on {banned_user}!")
        except asyncio.TimeoutError:
            await ctx.send(
                "Command failed. Make sure all necessary arguments are provided and/or correct."
            )

    @ban.error
    async def ban_error(self, ctx, error):  # forgot "self"
        """Error when ban doesn't work."""
        if isinstance(error, (commands.BadArgument, commands.MissingPermissions)):
            await ctx.send(  # Moderation has no "send" attribute
                "Command failed. Make sure you have the `ban_members` permission in order to use this command, or have specified the correct arguments."
            )
            print(error)

    @commands.has_permissions(kick_members=True)
    @commands.command()
    async def kick(self, ctx, kicked_user, *, reason: str = None):
        """Kick a user."""
        try:
            kicked_user = ctx.message.mentions[0]
        except IndexError:
            kicked_user = self.client.get_user(kicked_user)  # CLIENT should be self.client
        await ctx.guild.kick(user=kicked_user, reason=reason)
        await ctx.send(f"User {kicked_user} has been kicked.")

    @kick.error
    async def kick_error(self, ctx, error):  # forgot "self"
        """Error when kick doesn't work."""
        if isinstance(error, (commands.MissingRequiredArgument, commands.MissingPermissions)):
            await ctx.send(  # Moderation has no "send" attribute
                "Command failed. Make sure you have the `kick_members` permission in order to use this command, or have specified the user you want to kick using an @mention."
            )
            print(error)

    @commands.has_permissions(kick_members=True)
    @commands.command()
    async def prune(self, ctx, time: int = 0, *, reason: str):
        """Prune the server."""
        pruned = await ctx.guild.prune_members(days=time, reason=reason)
        await ctx.send(f"{pruned} member(s) have been pruned from the server.")


def setup(client):
    """Adds the cog to the bot."""
    client.add_cog(Moderation(client))
    logging.info("Moderation module online.")
