import discord, time, asyncio

client = discord.Client()
joined = 0
messages = 0

async def update_log():
    await client.wait_until_ready()
    global messages, joined
    while not client.is_closed():
        try:
            with open("stats.txt") as f:
                f.write(f"Time: {int(time.time())}, Messages: {messages}, Members Joined: {joined}\n")
                print("writing to log...")
                messages = 0
                joined = 0

                await asyncio.sleep(5)
        except Exception as e:
            print(e)
            await asyncio.sleep(5)

@client.event
async def on_ready():
    print("ready!")

@client.event
async def on_message(message):
    global messages
    messages += 1
    print(message.content)
    id = client.get_guild(561529218949971989)
    if message.content == "!hello":
        await message.channel.send("yo.")
    elif message.content == "!close":
        await message.channel.send("Closing up shop...")
        print("Sleep tight, Prismarine.")
        await client.logout()
    elif message.content == "!users":
        await message.channel.send(f"""Member Count: {id.member_count}""")

@client.event
async def on_member_join():
    global joined
    joined += 1


client.loop.create_task(update_log())
client.run("NTY4NDY5NDM3Mjg0NjE0MTc0.XLnOww.bHZ06CxgJVo4oYj-W-Vyj5VxSbM")
