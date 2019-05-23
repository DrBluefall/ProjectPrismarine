@commands.has_permissions(kick_members=True)
@CLIENT.command()
async def prune(ctx, time: int = 0, *, reason: str):
    pruned = await ctx.guild.prune_members(days=time, reason=reason)
    await ctx.send(f"{pruned} member(s) have been pruned from the server.")
