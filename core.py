"""Core file holding the Prismarine Bot."""
import logging
import asyncio
import json
import discord
from discord.ext import commands

with open("config.json", "r") as infile:
    try:
        CONFIG = json.load(infile)
        _ = CONFIG["token"]
        _ = CONFIG["owner"]

    except (KeyError, FileNotFoundError):
        raise EnvironmentError(
            "Your config.json file is either missing, or incomplete. Check your config.json and ensure it has the keys 'token' and 'owner'"
        )

CLIENT = commands.Bot(
    command_prefix="-",
    status=discord.Status.online,
    activity=discord.Game(name="with my creator!"),
)
logging.basicConfig(
    level=logging.INFO, format="%(name)s - %(levelname)s - %(asctime)s - %(message)s"
)

# --- Client Events


@CLIENT.event
async def on_ready():
    """What happens whem the bot is ready."""
    logging.basicConfig(
        level=logging.INFO, format="%(name)s - %(levelname)s - %(asctime)s - %(message)s"
    )
    logging.info("Log successfuly launched. Project Prismarine is online.")


# --- Bot Commands


@CLIENT.command()
async def ping(ctx):
    """Ping the user."""
    embed = discord.Embed(color=0xDE2E43)
    embed.add_field(
        name=f":ping_pong: Latency: `{round(CLIENT.latency*1000, ndigits=4)}ms`", value="\u200B"
    )
    await ctx.channel.send(embed=embed)


@CLIENT.command()
async def user(ctx, *, member: discord.User = None):
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
@CLIENT.command()
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
@CLIENT.command()
async def announce(ctx, *, text):
    """Make an announcement as the bot"""
    embed = discord.Embed(
        title=f"An Announcement from {ctx.message.author.display_name}...",
        description=text,
        color=discord.Color.blurple(),
    )
    embed.set_author(name="Unit 10008-RSP", icon_url=CLIENT.user.avatar_url)
    embed.set_footer(
        text=f"Solidarity, {ctx.message.author.display_name}.", icon_url=ctx.author.avatar_url)
    channel = CLIENT.get_channel(561530381908836353)
    await channel.send(embed=embed)


@announce.error
async def send_error(ctx, error):
    """Error when announce is used by an unauthorized user"""
    if isinstance(error, (discord.ext.commands.errors.NotOwner)):
        await ctx.send(":warning: *You're not authorized to use this!* :warning:")


@commands.has_permissions(manage_messages=True)
@CLIENT.command()
async def delete(ctx, amount: int = 10):
    """Purge a number of messages."""
    channel = CLIENT.get_channel(ctx.channel.id)
    deleted = await channel.purge(limit=amount)
    await ctx.send("{} message(s) have been deleted.".format(len(deleted)), delete_after=10)


@delete.error
async def delete_error(ctx, error):
    """Error when delete doesn't work."""
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(
            "Command failed. Make sure you have the `manage_messages` permission in order to use this command."
        )


@commands.has_permissions(ban_members=True)
@CLIENT.command()
async def ban(ctx, *, banned_user, time: int = 0, reason: str = ""):
    """Ban a user."""
    try:
        banned_user = ctx.message.mentions[0]
    except IndexError:
        banned_user = CLIENT.get_user(banned_user)
    try:
        await ctx.guild.ban(user=user, reason=reason, delete_message_days=time)
        await ctx.send(f"The ban hammer has been dropped on {user}!")
    except asyncio.TimeoutError:
        await ctx.send(
            "Command failed. Make sure all necessary arguments are provided and/or correct."
        )


@ban.error
async def ban_error(ctx, error):
    """Error when ban doesn't work."""
    if isinstance(error, (commands.BadArgument, commands.MissingPermissions)):
        await ctx.send(
            "Command failed. Make sure you have the `ban_members` permission in order to use this command, or have specified the correct arguments."
        )
        print(error)


@commands.has_permissions(kick_members=True)
@CLIENT.command()
async def kick(ctx, *, kicked_user, reason: str = None):
    """Kick a user."""
    try:
        kicked_user = ctx.message.mentions[0]
    except IndexError:
        kicked_user = CLIENT.get_user(kicked_user)
    await ctx.guild.kick(user=kicked_user, reason=reason)
    await ctx.send(f"User {kicked_user} has been kicked.")


@kick.error
async def kick_error(ctx, error):
    """Error when kick doesn't work."""
    if isinstance(error, (commands.MissingRequiredArgument, commands.MissingPermissions)):
        await ctx.send(
            "Command failed. Make sure you have the `kick_members` permission in order to use this command, or have specified the user you want to kick using an @mention."
        )
        print(error)


@commands.has_permissions(kick_members=True)
@CLIENT.command()
async def prune(ctx, *, reason: str, time: int = 0):
    """Prune the server."""
    pruned = await ctx.guild.prune_members(days=time, reason=reason)
    await ctx.send(f"{pruned} member(s) have been pruned from the server.")


@commands.has_permissions(manage_nicknames=True)
@CLIENT.command()
async def changename(ctx, *, name_user, nickname: str):
    """Change user's nick."""
    try:
        name_user = ctx.message.mentions[0]
    except IndexError:
        name_user = int(name_user)
        name_user = CLIENT.get_user(name_user)
    await user.edit(reason=None, nick=nickname)
    await ctx.send(f"`{name_user}`'s nickname has been changed to `{nickname}`.")


@commands.is_owner()
@CLIENT.command()
async def logout(ctx):
    """Quit the bot."""
    logging.info("Shutting down Project Prismarine...")
    await ctx.send("*Shutting down Project Prismarine...*")
    await CLIENT.logout()


@logout.error
async def logout_error(ctx, error):
    if isinstance(error, (discord.ext.commands.errors.NotOwner)):
        await ctx.send(":warning: *You're not authorized to use this!* :warning:")


@CLIENT.command()
async def credits(ctx):
    embed = discord.Embed(
        title="The Credits",
        description="""This command exists to commemorate and properly credit those who have assisted, inspired, or otherwise contributed to the creation of Project Prismarine.

    @.MO#0401 - For initially inspiring me to learn Python and persue Computer Science and programming in a serious manner.

    @Ikaheishi#0003 - For reviewing Project Prismarine's code and general assistance in my code endeavors.
    @TruePikachu#1985 - For aiding me in fixing several commands and showing me just how much of a newbie I am at Python.

    @DuckyQuack#7707 - For his massive assistance in improving the backend of Project Prismarine and making a multitide of improvements in the bot.

    To all of these people, I only have one thing to say.

    Thank you.
    """,
        color=discord.Color.dark_gold(),
    )
    embed.set_author(name="Unit 10008-RSP", icon_url=CLIENT.user.avatar_url)
    embed.set_footer(text=f"Solidarity, Dr. Prismarine Bluefall.")
    await ctx.send(embed=embed)


CLIENT.run(CONFIG["token"])
