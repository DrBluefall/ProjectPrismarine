@CLIENT.command()
async def user(ctx, member: discord.User = None):
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
