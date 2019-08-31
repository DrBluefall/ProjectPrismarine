# Standard Library Imports

from io import BytesIO
from datetime import datetime
from asyncio import TimeoutError

# Third-Party Imports

import discord
from discord.ext import commands

# Local Project Imports

from utils.loadout_gen import generate_image


class ScrimOrganization(commands.Cog):
    """Class made for organizing scrims."""

    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.group()
    async def scrim(self, ctx: commands.Context):
        pass

    @scrim.command()
    async def request(self, ctx: commands.Context, *, details):
        ret_code = self.client.dbh.add_scrim(ctx.message.author.id, details)

        if ret_code == 1:
            await ctx.send("Command Failed - User does not have a team.")
            return
        elif ret_code == 2:
            await ctx.send("Command Failed - Scrim request already registered into the database.")
            return
        elif ret_code == 3:
            await ctx.send("Command Failed - Team is currently being deleted.")
            return
        elif ret_code == 0:
            await ctx.send(
                f"Scrim registered! Your request will be active in the database, and you (along with other players) can view active requests with `{ctx.prefix}scrim active`. Good luck, and godspeed.")

    @scrim.command()
    async def active(self, ctx: commands.Context):
        scrim_list = self.client.dbh.get_scrims(ctx.message.author.id)

        scrim_embeds = []
        for scrim in scrim_list:
            c = self.client.get_user(scrim['captain_alpha'])
            embed = discord.Embed(
                title=f"Scrim Request: {scrim['team_alpha']['team']['name']}",
                color=discord.Color.from_rgb(255, 128, 8)
            )
            embed.add_field(name="Request ID:", value=scrim['id'])
            embed.add_field(
                name="Requested By:",
                value=c.mention if c is not None else "??????????????"
            )
            embed.add_field(name="Scrim Details:", value=scrim['details'])
            if scrim['team_alpha']['team']['thumbnail'] is not None:
                embed.set_thumbnail(url=scrim['team_alpha']['team']['thumbnail'])
            embed.add_field(
                name="Expires In:",
                value=str(round((
                                        datetime.fromtimestamp(scrim['expire_time']) - datetime.now()
                                ).seconds / 60 ** 2, ndigits=3)) + " hours"
            )
            embed.set_footer(
                text=f"To accept this request, use this command: {ctx.prefix}scrim accept {scrim['id']}",
                icon_url=self.client.user.avatar_url
            )
            scrim_embeds.append(embed)

        if len(scrim_embeds) == 0:
            await ctx.send("No scrims are currently active right now. How about you set one up?")
            return
        scrim_msg = await ctx.send(embed=scrim_embeds[0])
        await scrim_msg.add_reaction('❌')
        await scrim_msg.add_reaction('◀')
        await scrim_msg.add_reaction('▶')

        index = 0
        while True:
            try:
                reaction, user = await self.client.wait_for(
                    'reaction_add',
                    check=lambda r, u: u == ctx.message.author and str(r.emoji) in ['❌', '◀', '▶'],
                    timeout=300
                )
                await reaction.remove(user)
                if str(reaction.emoji) == '❌':
                    await scrim_msg.delete()
                    await ctx.message.delete()
                    return
                elif str(reaction.emoji) == '▶':
                    if index < len(scrim_embeds) - 1:
                        index += 1
                    else:
                        index = 0
                    await scrim_msg.edit(embed=scrim_embeds[index])
                elif str(reaction.emoji) == '◀':
                    if index >= 0:
                        index -= 1
                    else:
                        index = len(scrim_embeds) - 1
                    await scrim_msg.edit(embed=scrim_embeds[index])
            except TimeoutError:
                await scrim_msg.delete()
                await ctx.message.delete()
                return

    @scrim.command()
    async def accept(self, ctx: commands.Context, scrim_id):
        scrim = self.client.dbh.get_scrim(scrim_id)
        if scrim is None:
            await ctx.send("Command Failed - Invalid scrim ID.")
            return
        elif self.client.dbh.get_team(ctx.message.author.id) is None:
            await ctx.send(
                f"Command Failed - You don't have a team to scrim with! Create one with `{ctx.prefix}team create`.")
            return
        embed = discord.Embed(
            title=f"Scrim Opponent: {scrim['team_alpha']['team']['name']}",
            description=scrim['team_alpha']['team']['description'],
            color=discord.Color.from_rgb(255, 128, 8)
        )
        cap = self.client.get_user(scrim['captain_alpha'])
        if cap is not None:
            cap = cap.mention
        embed.add_field(name="Requested By:", value=cap)
        embed.add_field(name="Scrim Details:", value=scrim['details'])
        if scrim['team_alpha']['team']['thumbnail'] is not None:
            embed.set_thumbnail(url=scrim['team_alpha']['team']['thumbnail'])
        embed.add_field(
            name="Expires In:",
            value=str(round((
                                    datetime.fromtimestamp(scrim['expire_time']) - datetime.now()
                            ).seconds / 60 ** 2, ndigits=3)) + " hours"
        )
        tl = []
        if scrim['team_alpha']['team']['recent_tournaments'] is not None:
            for tourney in scrim['team_alpha']['team']['recent_tournaments']:
                s = f"""Tournament: `{tourney['tourney']}`\nPlace: `{tourney['place']}`\nResult Registered: `{datetime.fromtimestamp(tourney['date']).strftime("%d %B %Y")}`"""
                tl.append(s)
            embed.add_field(
                name="Recent Tournaments:",
                value='\n\n'.join(tl),
                inline=True
            )
        embed.add_field(
            name='Roster:',
            value='\n'.join([str(self.client.get_user(scrim['team_alpha']['players'][i]['id'])) for i in
                             range(len(scrim['team_alpha']['players']))])
        )
        if scrim['team_alpha']['team']['thumbnail'] is not None:
            embed.set_thumbnail(url=scrim['team_alpha']['team']['thumbnail'])

        player_embeds = []

        for profile in scrim['team_alpha']['players']:
            player = await self.client.fetch_user(profile['id'])
            pembed = discord.Embed(
                title=f"Player Profile - {player.name}",
                color=discord.Color.from_rgb(148, 0, 211)
            )

            pembed.add_field(
                name="In-Game Name:",
                value=f"`{profile['ign']}`"
            )
            pembed.add_field(
                name="Friend Code:",
                value=(f"SW-{profile['friend_code'][:4]}-{profile['friend_code'][4:8]}-{profile['friend_code'][8:12]}"
                       if any((
                            profile['is_private'] is False,
                            profile['id'] == ctx.message.author.id)
                        ) else "SW-XXXX-XXXX-XXXX")
            )
            pembed.add_field(
                name="Ranks:",
                value=f"""
        __Splat Zones__: {profile['sz']}
        __Tower Control__: {profile['tc']}
        __Rainmaker__: {profile['rm']}
        __Clam Blitz__: {profile['cb']}
        __Salmon Run__: {profile['sr']}
                                """
            )
            pembed.add_field(
                name="Level:",
                value=profile['level']
            )
            pembed.add_field(
                name="Position:",
                value=f"`{self.client.dbh.get_position(profile['position'])}`"
            )
            pembed.add_field(
                name="Team:",
                value=(profile['team_name'] + " :crown: ")
                if profile['team_id'] == profile['id'] else profile['team_name']
            )
            pembed.set_thumbnail(url=player.avatar_url)

            if profile['free_agent'] is True:
                pembed.set_footer(
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
                pembed.set_image(url='attachment://loadout.png')
            player_embeds.append({"embed": pembed, "file": loadout})
        scrim_msg = await ctx.send(embed=embed)
        player_msg = await ctx.send(**player_embeds[0])
        await player_msg.add_reaction('◀')
        await player_msg.add_reaction('▶')
        await player_msg.add_reaction('❌')
        await player_msg.add_reaction('✅')
        index = 0
        while True:
            try:
                reaction, user = await self.client.wait_for(
                    'reaction_add',
                    check=lambda r, u: u == ctx.message.author and str(r.emoji) in ['◀', '▶', '❌', '✅'],
                    timeout=300
                )
                await reaction.remove(user)
                if str(reaction.emoji) == '❌':
                    await player_msg.delete()
                    await scrim_msg.delete()
                    await ctx.message.delete()
                    return
                elif str(reaction.emoji) == '▶':
                    if index < len(player_embeds) - 1:
                        index += 1
                    else:
                        index = 0
                    await player_msg.edit(**player_embeds[index])
                elif str(reaction.emoji) == '◀':
                    if index >= 0:
                        index -= 1
                    else:
                        index = len(player_embeds) - 1
                    await player_msg.edit(**player_embeds[index])
                elif str(reaction.emoji) == '✅':
                    await player_msg.delete()
                    await scrim_msg.delete()
                    await ctx.send(
                        "Alright! I'll DM the opposing captain and let you know if they want to scrim with you.")
                    try:
                        alpha_cap = await self.client.fetch_user(scrim['captain_alpha'])
                        alpha_team = scrim['team_alpha']
                        bravo_cap = ctx.message.author
                        bravo_team = self.client.dbh.get_team(ctx.message.author.id)
                        response = await self.bravo_cap_msg(alpha_cap, alpha_team, bravo_cap, bravo_team)
                    except discord.NotFound:
                        await ctx.send("Command Failed - Unable to track down opposing captain.")
                        return
            except TimeoutError:
                await player_msg.delete()
                await scrim_msg.delete()
                await ctx.message.delete()
                return

    async def bravo_cap_msg(self,
                            alpha_cap: discord.User,
                            alpha_team: dict,
                            bravo_cap: discord.User,
                            bravo_team: dict):
        pass


def setup(client):
    client.add_cog(ScrimOrganization(client))
