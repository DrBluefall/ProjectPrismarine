@CLIENT.command()
async def credits(ctx):
    embed = discord.Embed(
        title="The Credits",
        description="""This command exists to commemorate and properly credit those who have assisted, inspired, or otherwise contributed to the creation of Project Prismarine.

    @.MO#0401 - For initially inspiring me to learn Python and persue Computer Science and programming in a serious manner.

    @Ikaheishi#0003 - For reviewing Project Prismarine's code and general assistance in my code endeavors.
    @TruePikachu#1985 - For aiding me in fixing several commands and showing me just how much of a newbie I am at Python.

    @DuckyQuack#7707 - For his massive assistance in improving the backend of Project Prismarine and making a multitide of improvements in the bot.

    To all of these people, I only have one thing to say.

    Thank you.
    """,
        color=discord.Color.dark_gold(),
    )
    embed.set_author(name="Unit 10008-RSP", icon_url=CLIENT.user.avatar_url)
    embed.set_footer(text=f"Solidarity, Dr. Prismarine Bluefall.")
    await ctx.send(embed=embed)
