import discord, logging
from discord.ext import commands

client = commands.Bot(command_prefix="-", status=discord.Status.online, activity=discord.Game(name="with my creator!"))
logging.basicConfig(level=logging.INFO, format="%(name)s - %(levelname)s - %(asctime)s - %(message)s")

def is_bot(message):
    return discord.User.bot

# Client Events #

@client.event
async def on_ready():
    logging.basicConfig(level=logging.INFO, format="%(name)s - %(levelname)s - %(asctime)s - %(message)s")
    logging.info("Log successfuly launched. Project Prismarine is online.")

# Bot Commands #

@client.command()
async def ping(ctx):
    ping_ = client.latency
    ping = round(ping_ * 1000, ndigits=4)
    await ctx.channel.send(f"""Pong!

Latency: {ping} ms""")

@client.command()
async def user(ctx, member:discord.User = None):
    if member == None:
        member = ctx.message.author
    else:
        member = ctx.message.mentions[0]
    name = f"`{member.name}#{member.discriminator}`"
    await ctx.channel.send(f"""Discord ID: {name}
User ID: `{ctx.message.author.id}`
Account Created: `{member.created_at} UTC`
Status: `{member.status}`
Joined Server At: `{member.joined_at} UTC`""")

@client.command()
async def send(ctx, channel:str, *, content:str):
    if ctx.message.author.id != 490650609641324544:
        await ctx.send("You're not authorized to use this!")
        return
    channel = client.get_channel(int(channel))
    await channel.send(content)
    await ctx.send(f"Message sent to {channel}.")
    logging.info(f"Message sent to {channel}.")


@client.command()
async def announce(ctx,*, text):
    if ctx.message.author.id != 490650609641324544:
        await ctx.send("You're not authorized to use this!")
        return
    embed = discord.Embed(title="An Announcement from Dr. Bluefall...", description=text, color=discord.Color.blurple())
    embed.set_author(name="Unit 10008-RSP", icon_url=client.user.avatar_url)
    embed.set_footer(text=f"Solidarity, Dr. P. Bluefall.", icon_url=ctx.author.avatar_url)
    channel = client.get_channel(561530381908836353)
    await channel.send(embed=embed)

@commands.has_permissions(manage_messages=True)
@client.command()
async def delete(ctx, amount:int = 10):
    channel = client.get_channel(ctx.channel.id)
    deleted = await channel.purge(limit=amount)
    await ctx.send("{} message(s) have been deleted.".format(len(deleted)),delete_after=10)

@delete.error
async def delete_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("Command failed. Make sure you have the `manage_messages` permission in order to use this command.")

@commands.has_permissions(ban_members=True)
@client.command()
async def ban(ctx, user__, time:int = 0, *, reason:str = ""):
    try:
        user = ctx.message.mentions[0]
    except:
        user_ = int(user__)
        user = client.get_user(user_)
    try:
        await ctx.guild.ban(user=user,reason=reason,delete_message_days=time)
        await ctx.send(f"The ban hammer has been dropped on {user}!")
    except:
        await ctx.send("Command failed. Make sure all necessary arguments are provided and/or correct.")

@ban.error
async def ban_error(ctx, error):
    if isinstance(error,commands.BadArgument) or isinstance(error, commands.MissingPermissions):
        await ctx.send("Command failed. Make sure you have the `ban_members` permission in order to use this command, or have specified the correct arguments.")
        print(error)

@commands.has_permissions(kick_members=True)
@client.command()
async def kick(ctx, user__, *, reason:str=None):
    try:
        user = ctx.message.mentions[0]
    except:
        user_ = int(user__)
        user = client.get_user(user_)
    await ctx.guild.kick(user=user,reason=reason)
    await ctx.send(f"User {user} has been kicked.")

@kick.error
async def kick_error(ctx, error):
    if isinstance(error,commands.MissingRequiredArgument) or isinstance(error, commands.MissingPermissions):
        await ctx.send("Command failed. Make sure you have the `kick_members` permission in order to use this command, or have specified the user you want to kick using an @mention.")
        print(error)

@commands.has_permissions(kick_members=True)
@client.command()
async def prune(ctx, time:int = 0, *, reason:str):
    pruned = await ctx.guild.prune_members(days=time,reason=reason)
    await ctx.send(f"{pruned} member(s) have been pruned from the server.")

@commands.has_permissions(manage_nicknames=True)
@client.command()
async def changename(ctx, user__, *, nickname:str):
    try:
        user = ctx.message.mentions[0]
    except:
        user_ = int(user__)
        user = client.get_user(user_)
        print(user)
    await user.edit(reason=None, nick=nickname)
    await ctx.send(f"`{user}`'s nickname has been changed to `{nickname}`.")


@client.command()
async def logout(ctx):
    if ctx.message.author.id != 490650609641324544:
        await ctx.send("You're not authorized to use this!")
        return
    logging.info("Shutting down Project Prismarine...")
    await ctx.send("*Shutting down Project Prismarine...*")
    await client.logout()

client.run("NTY4NDY5NDM3Mjg0NjE0MTc0.XLnOww.bHZ06CxgJVo4oYj-W-Vyj5VxSbM")
#test2
