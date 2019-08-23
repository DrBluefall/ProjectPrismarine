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
    async def player(self, ctx: commands.Context):
        """Player command group. Use this to modify your own profile, as well as view the profiles of others."""
        pass

    @player.command()
    async def profile(self, ctx: commands.Context, user=None):
        """View a player's profile. If no user is specified, it will show your own profile."""
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
__Splat Zones__: {profile['sz']}
__Tower Control__: {profile['tc']}
__Rainmaker__: {profile['rm']}
__Clam Blitz__: {profile['cb']}
__Salmon Run__: {profile['sr']}
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
    async def create_profile(self, ctx: commands.Context):
        """Make a profile in the bot. Pretty self-explanatory."""
        self.client.dbh.add_profile(ctx.message.author.id)
        await ctx.send("Player profile created! :smiley:")
    
    @player.command()
    async def fc(self, ctx: commands.Context, *, friend_code):
        """Set your friend code."""
        valid = self.client.dbh.update_fc(ctx.message.author.id, friend_code)
        if valid:
            await ctx.send("Friend code updated! :smiley:")
        else:
            await ctx.send("Command Failed - Invalid Friend Code passed.")
    

    @player.command()
    async def ign(self, ctx: commands.Context, *, ign):
        """Set your in-game name."""
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
    async def level(self, ctx: commands.Context, level):
        """Set your level."""
        self.client.dbh.update_level(ctx.message.author.id, level)
        await ctx.send("Level updated! :smiley:")
    
    @player.command()
    async def rank(self, ctx: commands.Context, mode, *, rank):
        """Set your rank in specific modes.
        Aliases:
            - Splat Zones: `sz`, `splatzones`, `sz_rank`
            - Tower Control: `tc`, `towercontrol`, `tc_rank`
            - Rainmaker: `rm`, `rainmaker`, `rm_rank`
            - Clam Blitz: `cb`, `clamblitz`, `cb_rank`
            - Salmon Run: `sr`. `salmonrun`, `sr_rank`
        """
        updated = self.client.dbh.update_rank(ctx.message.author.id, mode, rank)
        if updated:
            await ctx.send("Rank updated! :smiley:")
        else:
            await ctx.send("Command Failed - Invalid Mode or Rank specified.")
    
    @player.command()
    async def position(self, ctx: commands.Context, position: int):
        """Set your position. Each one is mapped to an integer, which you must pass in as your position.
        ex) "pr.player position 2" sets your position to `Midline`.
        Position Map:
            0: Not Set
            1: Frontline
            2: Midline
            3: Frontline
            4: Flex
        """
        try:
            self.client.dbh.update_position(ctx.message.author.id, position)
            await ctx.send('Set position to %s!' % self.client.dbh.get_position(position))
        except ValueError:
            await ctx.send("Command Failed - Invalid Position specified.")
    
    @player.command()
    async def loadout(self, ctx: commands.Context, loadout_link: str):
        """Set your loadout within the bot. Use https://selicia.github.io/en_US/ to create a loadout, and give the bot the resulting link."""
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
                await ctx.send('Loadout Updated! :smiley:')
            elif msg.content.lower() == 'n':
                await ctx.send("Understood. Aborting update.")
    
    def set_head(self, msg: discord.Message):
        raise NotImplementedError

    def set_clothes(self, msg: discord.Message):
        raise NotImplementedError

    def set_pants(self, msg: discord.Message):
        raise NotImplementedError

    @player.command()
    async def ldgui(self, ctx: commands.Context):
        """Use a built in loadout GUI to set your loadout within the bot!"""

        embed = discord.Embed(
            title="Welcome to the Loadout Creation GUI!",
            description="""
This GUI will assist in getting your loadout within the bot. Below, you'll see reactions that you can, well, react to, and use to pick what gear you would like to set, what you would like to set (the gear itself, mains, subs), and finally, finalize the whole thing.
Here are the options:

🎩 - Hat

👕 - Clothes

👢 - Shoes

✅ - Confirm your new loadout!

❌ - Quit, discard all changes
            """,
            color=discord.Color.from_rgb(255, 0, 0)
        )
        embed.set_author(
            name=self.client.user.name,
            icon_url=self.client.user.avatar_url
        )
        loadout_msg = await ctx.send(embed=embed)
        for i in ["🎩", "👕", "👢", "✅", "❌"]:
            await loadout_msg.add_reaction(i)
        ld_dict = {
            'clothes': {
                'gear_id': 0, 
                'main': 0, 
                'subs': [0, 0, 0]
                },
            'head': {
                'gear_id': 0, 
                'main': 0, 
                'subs': [0, 0, 0]
                },
            'id': 0,
            'set': 0,
            'shoes': {
                'gear_id': 0, 
                'main': 0, 
                'subs': [0, 0, 0]
                }
            }
        switch = {
            "🎩": self.set_head, 
            "👕": self.set_clothes,
            "👢": self.set_pants
        }
        while True:
            reaction, user = await self.client.wait_for(
                'reaction_add', 
                check=lambda r, u: u == ctx.message.author \
                and str(r.emoji) in ["🎩", "👕", "👢", "✅", "❌"]
            )
            await loadout_msg.remove_reaction(reaction, user)
            if str(reaction.emoji) in switch.keys():
                switch[str(reaction.emoji)](loadout_msg)

    @player.command()
    async def toggle_fa(self, ctx: commands.Context):
        """Toggle whether or not to display your profile as that of a Free Agent."""
        await ctx.send(f"Free Agent Status set to `{self.client.dbh.toggle_free_agent(ctx.message.author.id)}`")

    @player.command()
    async def toggle_private(self, ctx: commands.Context):
        """Toggle privacy on your profile to `True` in order to hide your FC from anyone that's not you when using `pr.player profile`."""
        await ctx.send(f"Privacy Status set to `{self.client.dbh.toggle_private(ctx.message.author.id)}`")


def setup(client):
    client.add_cog(Player(client))