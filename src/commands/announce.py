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
    embed.set_footer(text=f"Solidarity, {ctx.message.author.display_name}.", icon_url=ctx.author.avatar_url)
    channel = CLIENT.get_channel(561530381908836353)
    await channel.send(embed=embed)
