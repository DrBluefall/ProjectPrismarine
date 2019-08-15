# Core Language Imports

from io import BytesIO

# Third-Party Imports

import discord
from discord.ext import commands

# Local Project Imports

from utils.decoder import decode
from utils.loadout_gen import generate_image, compile_loadout_dict


class Player(commands.Cog):

    def __init__(self, client):
        self.client = client
    
    @commands.group()
    async def player(self, ctx):
        pass

    @player.command()
    async def profile(self, ctx, user=None):
        if user is None:
            user = ctx.message.author
        else:
            try:
                user = ctx.message.mentions[0]
            except IndexError:
                try:
                    user = self.client.get_user(user)
                    if user is None:
                        raise ValueError
                except ValueError:
                    await ctx.send("Command Failed - Invalid User specified.")
                    return

        profile = self.client.dbh.get_profile(user.id)
        if profile is None:
            await ctx.send("Command Failed - User does not have a profile.")
            return
        
        
        embed = discord.Embed(
            title="Player Profile: %s" % user.display_name,
            color=discord.Color.from_rgb(255, 0, 0) \
                if profile['free_agent'] is False else discord.Color.from_rgb(0, 255, 0)
        )
        embed.add_field(
            name="In-Game Name:",
            value=f"`{profile['ign']}`"
        )
        embed.add_field(
            name="Friend Code:",
            value=(f"SW-{profile['friend_code'][:4]}-{profile['friend_code'][4:8]}-{profile['friend_code'][8:12]}" \
                if any((profile['is_private'] is False, profile['id'] == ctx.message.author.id)) else "SW-XXXX-XXXX-XXXX")
        )
        embed.add_field(
            name="Ranks:",
            value=f"""
Splat Zones: {profile['sz']}
Tower Control: {profile['tc']}
Rainmaker: {profile['rm']}
Clam Blitz: {profile['cb']}
Salmon Run: {profile['sr']}
            """
        )
        embed.add_field(
            name="Level:",
            value=profile['level']
        )
        embed.add_field(
            name="Position:",
            value=f"`{self.client.dbh.get_position(profile['position'])}`"
        )
        embed.add_field(
            name="Team:",
            value=(profile['team_name'] + " :crown: ") \
                if profile['is_captain'] is True else profile['team_name']
        )
        embed.set_thumbnail(url=user.avatar_url)

        if profile['free_agent'] is True:
            embed.set_footer(
                text="This user is a free agent! Perhaps you should consider recruiting them?",
                icon_url=self.client.user.avatar_url
                )
        loadout = None
        if profile['loadout'] is not None:
            loadout = generate_image(profile['loadout'])
            buffer = BytesIO()
            loadout.save(buffer, "png")
            buffer.seek(0)
            loadout = discord.File(filename='loadout.png', fp=buffer)
            embed.set_image(url='attachment://loadout.png')
        await ctx.send(embed=embed, file=loadout)


    @player.command()
    async def create_profile(self, ctx):
        self.client.dbh.add_profile(ctx.message.author.id)
        await ctx.send("Player profile created! :smiley:")
    
    @player.command()
    async def fc(self, ctx, *, friend_code):
        valid = self.client.dbh.update_fc(ctx.message.author.id, friend_code)
        if valid:
            await ctx.send("Friend code updated! :smiley:")
        else:
            await ctx.send("Command Failed - Invalid Friend Code passed.")
    

    @player.command()
    async def ign(self, ctx, *, ign):
        if any(
                (
                len(ign) > 10, 
                len(ign) < 1
                )
            ):
            await ctx.send("Command Failed - Invalid Name specified.")
        else:
            self.client.dbh.update_ign(ctx.message.author.id, ign)
            await ctx.send("In-Game Name updated! :smiley:")
    
    @player.command()
    async def level(self, ctx, level):
        self.client.dbh.update_level(ctx.message.author.id, level)
        await ctx.send("Level updated! :smiley:")
    
    @player.command()
    async def rank(self, ctx, mode, *, rank):
        updated = self.client.dbh.update_rank(ctx.message.author.id, mode, rank)
        if updated:
            await ctx.send("Rank updated! :smiley:")
        else:
            await ctx.send("Command Failed - Invalid Mode or Rank specified.")
    
    @player.command()
    async def position(self, ctx, position: int):
        try:
            self.client.dbh.update_position(ctx.message.author.id, position)
            await ctx.send('Set position to %s!' % self.client.dbh.get_position(position))
        except ValueError:
            await ctx.send("Command Failed - Invalid Position specified.")
    
    @player.command()
    async def loadout(self, ctx, loadout_link: str):
        if loadout_link.startswith('https://selicia.github.io/en_US/#'):
            loadout = compile_loadout_dict(decode(loadout_link[33:]))
            ld_image = generate_image(loadout)
            buffer = BytesIO()
            ld_image.save(buffer, 'png')
            buffer.seek(0)
            ld_image = discord.File(filename='loadout.png', fp=buffer)
            await ctx.send("Is this correct? `[Y/n]`", file=ld_image)
            msg = await self.client.wait_for('message', check=lambda m: all((m.author == ctx.message.author, (m.content.lower() == 'y' or m.content.lower() == 'n'))))
            if msg.content.lower() == 'y':
                self.client.dbh.update_loadout(ctx.message.author.id, loadout)
                await ctx.send('foo')
            pass

    @player.command()
    async def toggle_fa(self, ctx):
        await ctx.send(f"Free Agent Status set to `{self.client.dbh.toggle_free_agent(ctx.message.author.id)}`")

    @player.command()
    async def toggle_private(self, ctx):
        await ctx.send(f"Privacy Status set to `{self.client.dbh.toggle_private(ctx.message.author.id)}`")


def setup(client):
    client.add_cog(Player(client))