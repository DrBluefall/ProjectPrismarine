@commands.is_owner()
@CLIENT.command()
async def send(ctx, channel: str, *, content: str):
    """Send message to a channel as the bot."""
    channel = CLIENT.get_channel(int(channel))
    await channel.send(content)
    await ctx.send(f"Message sent to {channel}.")
    logging.info("Message sent to %s.", channel)
