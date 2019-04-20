import discord, logging
from discord.ext import commands

client = commands.Bot(command_prefix=";", status=discord.Status.online, activity=discord.Game(name="with my creator!"))
logging.basicConfig(level=logging.INFO, format="%(name)s - %(levelname)s - %(asctime)s - %(message)s")

@client.event
async def on_ready():
    logging.basicConfig(level=logging.INFO, format="%(name)s - %(levelname)s - %(asctime)s - %(message)s")
    logging.info("Log successfuly launched. Project Prismarine is online.")

@client.event
async def on_member_join(member):
    print(f"{member} has joined the server.")

@client.event
async def on_member_remove(member):
    print(f"{member} has left the server.")

@client.command()
async def ping(ctx):
    ping_ = client.latency
    ping = round(ping_, ndigits=5)
    await ctx.channel.send(f"Latency: {ping} sec.")

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

@client.command()
async def logout(ctx):
    if ctx.message.author.id != 490650609641324544:
        await ctx.send("You're not authorized to use this!")
        return
    logging.info("Shutting down Project Prismarine...")
    await ctx.send("*Shutting down Project Prismarine...*")
    await client.logout()


client.run("NTY4NDY5NDM3Mjg0NjE0MTc0.XLnOww.bHZ06CxgJVo4oYj-W-Vyj5VxSbM")
