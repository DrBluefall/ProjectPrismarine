@commands.has_permissions(manage_nicknames=True)
@CLIENT.command()
async def changename(ctx, *, name_user, nickname: str):
    try:
        name_user = ctx.message.mentions[0]
    except IndexError:
        name_user = int(name_user)
        name_user = CLIENT.get_user(name_user)
    await user.edit(reason=None, nick=nickname)
    await ctx.send(f"`{name_user}`'s nickname has been changed to `{nickname}`.")
