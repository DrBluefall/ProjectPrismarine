@CLIENT.command()
async def announce(ctx, *, text):
    if ctx.message.author.id != CONFIG["owner"]:
        await ctx.send("You're not authorized to use this!")
        return
    embed = discord.Embed(
        title="An Announcement from Dr. Bluefall...",
        description=text,
        color=discord.Color.blurple(),
    )
    embed.set_author(name="Unit 10008-RSP", icon_url=CLIENT.user.avatar_url)
    embed.set_footer(text=f"Solidarity, Dr. P. Bluefall.", icon_url=ctx.author.avatar_url)
    channel = CLIENT.get_channel(561530381908836353)
    await channel.send(embed=embed)
