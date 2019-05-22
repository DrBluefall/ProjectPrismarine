@commands.has_permissions(ban_members=True)
@CLIENT.command()
async def ban(ctx, *, banned_user, time: int = 0, reason: str = ""):
    try:
        banned_user = ctx.message.mentions[0]
    except IndexError:
        banned_user = CLIENT.get_user(banned_user)
    try:
        await ctx.guild.ban(user=user, reason=reason, delete_message_days=time)
        await ctx.send(f"The ban hammer has been dropped on {user}!")
    except asyncio.TimeoutError:
        await ctx.send(
            "Command failed. Make sure all necessary arguments are provided and/or correct."
        )


@ban.error
async def ban_error(ctx, error):
    if isinstance(error, (commands.BadArgument, commands.MissingPermissions)):
        await ctx.send(
            "Command failed. Make sure you have the `ban_members` permission in order to use this command, or have specified the correct arguments."
        )
        print(error)
