@commands.has_permissions(kick_members=True)
@CLIENT.command()
async def kick(ctx, kicked_user, *, reason: str = None):
    try:
        kicked_user = ctx.message.mentions[0]
    except IndexError:
        kicked_user = CLIENT.get_user(kicked_user)
    await ctx.guild.kick(user=kicked_user, reason=reason)
    await ctx.send(f"User {kicked_user} has been kicked.")


@kick.error
async def kick_error(ctx, error):
    if isinstance(error, (commands.MissingRequiredArgument, commands.MissingPermissions)):
        await ctx.send(
            "Command failed. Make sure you have the `kick_members` permission in order to use this command, or have specified the user you want to kick using an @mention."
        )
        print(error)
