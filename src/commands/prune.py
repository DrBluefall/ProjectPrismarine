@commands.has_permissions(kick_members=True)
@CLIENT.command()
async def prune(ctx, *, reason: str, time: int = 0):
    pruned = await ctx.guild.prune_members(days=time, reason=reason)
    await ctx.send(f"{pruned} member(s) have been pruned from the server.")
