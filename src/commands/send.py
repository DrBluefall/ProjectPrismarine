@CLIENT.command()
async def send(ctx, *, channel: str, content: str):
    if ctx.message.author.id != CONFIG["owner"]:
        await ctx.send("You're not authorized to use this!")
        return
    channel = CLIENT.get_channel(int(channel))
    await channel.send(content)
    await ctx.send(f"Message sent to {channel}.")
    logging.info("Message sent to %s.", channel)
