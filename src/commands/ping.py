@CLIENT.command()
async def ping(ctx):
    ping_ms = round(CLIENT.latency * 1000, ndigits=4)
    await ctx.channel.send(
        f"""Pong!

Latency: {ping_ms} ms"""
    )
