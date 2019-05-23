@commands.is_owner()
@CLIENT.command()
async def logout(ctx):
    """Quit the bot."""
    logging.info("Shutting down Project Prismarine...")
    await ctx.send("*Shutting down Project Prismarine...*")
    await CLIENT.logout()
