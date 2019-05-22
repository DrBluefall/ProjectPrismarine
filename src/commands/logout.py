@CLIENT.command()
async def logout(ctx):
    if ctx.message.author.id != CONFIG["owner"]:
        await ctx.send("You're not authorized to use this!")
        return
    logging.info("Shutting down Project Prismarine...")
    await ctx.send("*Shutting down Project Prismarine...*")
    await CLIENT.logout()
