@commands.has_permissions(manage_messages=True)
@CLIENT.command()
async def delete(ctx, amount: int = 10):
    channel = CLIENT.get_channel(ctx.channel.id)
    deleted = await channel.purge(limit=amount)
    await ctx.send("{} message(s) have been deleted.".format(len(deleted)), delete_after=10)


@delete.error
async def delete_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(
            "Command failed. Make sure you have the `manage_messages` permission in order to use this command."
        )
