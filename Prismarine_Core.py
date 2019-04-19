import discord
import time
import asyncio

messages = joined = 0

client = discord.Client()


async def update_stats():
    await client.wait_until_ready()
    global messages, joined

    while not client.is_closed():
        try:
            with open("stats.txt", "a") as f:
                f.write(f"Time: {int(time.time())}, Messages: {messages}, Members Joined: {joined}\n")

            messages = 0
            joined = 0

            await asyncio.sleep(5)
        except Exception as e:
            print(e)
            await asyncio.sleep(5)



@client.event
async def on_member_join(member):
    global joined
    joined += 1
    for channel in member.server.channels:
        if str(channel) == "general":
            await client.send_message(f"""Welcome to the server {member.mention}""")


@client.event
async def on_message(message):
    global messages
    messages += 1

    id = client.get_guild(561529218949971989)
    channels = ["prismarines-room"]
    valid_users = ["Dr. Prismarine Bluefall#3305"]

    if str(message.channel) in channels and str(message.author) in valid_users:
        if message.content.find("!hello") != -1:
            await message.channel.send("Hi")
        elif message.content == "!users":
            await message.channel.send(f"""# of Members: {id.member_count}""")
        elif message.content == "!close":
            await message.channel.send("Closing up shop...")
            print("Sleep tight, Prismarine.")
            await client.logout()

client.loop.create_task(update_stats())
client.run("NTY4NDY5NDM3Mjg0NjE0MTc0.XLnOww.bHZ06CxgJVo4oYj-W-Vyj5VxSbM")
