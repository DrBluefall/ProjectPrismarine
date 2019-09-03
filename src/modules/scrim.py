# Standard Library Imports

from io import BytesIO
from datetime import datetime
from asyncio import TimeoutError, sleep

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
        scrim_msg = await ctx.send(content="Do you want to scrim this team?", embed=embed)
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
                        await self.bravo_cap_msg(ctx, alpha_cap, bravo_cap, bravo_team, scrim['id'])
                    except discord.NotFound:
                        await ctx.send("Command Failed - Unable to track down opposing captain.")
                        return
            except TimeoutError:
                await player_msg.delete()
                await scrim_msg.delete()
                await ctx.message.delete()
                return

    async def bravo_cap_msg(self,
                            ctx: commands.Context,
                            alpha_cap: discord.User,
                            bravo_cap: discord.User,
                            bravo_team: dict,
                            scrim_id: int):
        alpha_dm = await alpha_cap.create_dm() if alpha_cap.dm_channel is None else alpha_cap.dm_channel
        bravo_dm = await bravo_cap.create_dm() if bravo_cap.dm_channel is None else bravo_cap.dm_channel

        team_embed = discord.Embed(
            title=f"Team Profile - {bravo_team['team']['name']}",
            color=discord.Color.from_rgb(148, 0, 211),
            description=bravo_team['team']['description']
        )
        tl = []
        if bravo_team['team']['recent_tournaments'] is not None:
            for tourney in bravo_team['team']['recent_tournaments']:
                s = f"""Tournament: `{tourney['tourney']}`\nPlace: `{tourney['place']}`\nResult Registered: `{datetime.fromtimestamp(tourney['date']).strftime("%d %B %Y")}`"""
                tl.append(s)
            team_embed.add_field(
                name="Recent Tournaments:",
                value='\n\n'.join(tl),
                inline=True
            )
        team_embed.add_field(
            name='Roster:',
            value='\n'.join(
                [str(self.client.get_user(bravo_team['players'][i]['id'])) for i in range(len(bravo_team['players']))])
        )
        team_embed.add_field(
            name="Captain:",
            value=bravo_cap.mention
        )
        team_embed.add_field(
            name="Team Created:",
            value=bravo_team['team']['creation_time']
        )

        if bravo_team['team']['thumbnail'] is not None:
            team_embed.set_thumbnail(url=bravo_team['team']['thumbnail'])

        player_embeds = []

        for profile in bravo_team['players']:
            player = await self.client.fetch_user(profile['id'])
            embed = discord.Embed(
                title=f"Player Profile - {player.name}",
                color=discord.Color.from_rgb(148, 0, 211)
            )

            embed.add_field(
                name="In-Game Name:",
                value=f"`{profile['ign']}`"
            )
            embed.add_field(
                name="Friend Code:",
                value=(f"SW-{profile['friend_code'][:4]}-{profile['friend_code'][4:8]}-{profile['friend_code'][8:12]}"
                       if any((
                    profile['is_private'] is False,
                    profile['id'] == ctx.message.author.id)
                ) else "SW-XXXX-XXXX-XXXX")
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
                value=(profile['team_name'] + " :crown: ")
                if profile['team_id'] == profile['id'] else profile['team_name']
            )
            embed.set_thumbnail(url=player.avatar_url)

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
            player_embeds.append({"embed": embed, "file": loadout})

        team_msg = await alpha_dm.send(
            content="You've gotten a response from an opponent! Here are their details. If you want to accept, react to ✅ to alert the opponent team captain and I'll set up a scrim room for you! If not, just react to ❌ and I'll be on my way.",
            embed=team_embed
        )

        player_msg = await alpha_dm.send(**player_embeds[0])
        await player_msg.add_reaction('◀')
        await player_msg.add_reaction('▶')
        await player_msg.add_reaction('❌')
        await player_msg.add_reaction('✅')
        index = 0
        while True:
            try:
                reaction, user = await self.client.wait_for(
                    'reaction_add',
                    check=lambda r, u: u == alpha_cap and str(r.emoji) in ['◀', '▶', '❌', '✅'],
                    timeout=300
                )
                if str(reaction.emoji) == '❌':
                    await player_msg.delete()
                    await team_msg.delete()
                    await alpha_dm.send(
                        "Understood. I'll let the opponent captain know and be on my way.",
                        delete_after=5
                    )
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
                    await team_msg.delete()
                    await alpha_dm.send(
                        "Awesome! I'll let the opposing captain know that you're down, and I'll set up a room in the scrim server!"
                    )
                    async with scrimctl(self.client, scrim_id):
                        pass
                    return
            except TimeoutError:
                await player_msg.delete()
                await team_msg.delete()
                return


class scrimctl(object):

    def __init__(self, client: commands.Bot, scrim_id: int):
        self.client = client
        self.scrim: dict = self.client.dbh.get_scrim(scrim_id)

    scrim_channel: discord.TextChannel = None
    alpha_voice: discord.VoiceChannel = None
    bravo_voice: discord.VoiceChannel = None
    alpha_role: discord.Role = None
    bravo_role: discord.Role = None

    async def __aenter__(self):
        self.alpha_role = await self.client.scrim_server.create_role(f"Scrim {self.scrim['id']} - Team Alpha")
        self.bravo_role = await self.client.scrim_server.create_role(f"Scrim {self.scrim['id']} - Team Bravo")

        perms = {
            "add_reactions": True,
            "read_messages": True,
            "send_messages": True,
            "read_message_history": True,
            "external_emojis": True,
            "connect": True,
            "speak": True,
            "use_voice_activation": True
        }

        self.scrim_channel = self.client.scrim_category.create_text_channel(f"scrim-{self.scrim['id']}",
                                                                            overwrites={
                                                                                self.alpha_role: discord.PermissionOverwrite(
                                                                                    **perms),
                                                                                self.bravo_role: discord.PermissionOverwrite(
                                                                                    **perms)
                                                                            })
        self.alpha_voice = self.client.scrim_category.create_voice_channel(f"Scrim {self.scrim['id']} - Team Alpha",
                                                                           overwrites={
                                                                               self.alpha_role: discord.PermissionOverwrite(
                                                                                   **{"connect": True, "speak": True}),
                                                                               self.bravo_role: discord.PermissionOverwrite(
                                                                                   **{"connect": False, "speak": False})
                                                                           })
        self.bravo_voice = self.client.scrim_category.create_voice_channel(f"Scrim {self.scrim['id']} - Team Bravo",
                                                                           overwrites={
                                                                               self.alpha_role: discord.PermissionOverwrite(
                                                                                   **{"connect": False,
                                                                                      "speak": False}),
                                                                               self.bravo_role: discord.PermissionOverwrite(
                                                                                   **{"connect": True, "speak": True})
                                                                           })

        await self.scrim_channel.send(f"""
        ⚔ *__Welcome to the scrim channel!__* ⚔
        
        Two voice channels have been provided for you. One for Team Alpha ({self.scrim['team_alpha']['team']['name']}), and one for Team Bravo ({self.scrim['team_bravo']['team']['name']}). Upon arrival, you should have been assigned a role with your scrim ID and team. These channels will exist for as long as you need them, although they will be closed automatically after 20 minutes of inactivity.
        
        And that's all I have to say for now. Good luck, and godspeed! ^^)
        """)

        return self.scrim_channel.create_invite(reason=f"Scrim created! Scrim ID:{self.scrim['id']}")

    async def __aexit__(self, exc_type, exc_val, exc_tb):

        while True:
            try:
                await self.client.wait_for('message', check=lambda m: m.author != self.client.user, timeout=900)
            except TimeoutError:
                await self.scrim_channel.send(
                    "*WARNING* - Channel has been inactive for 15 minutes. This channel will be deleted in 5 minutes if this channel continues to be inactive.")
                while True:
                    try:
                        await self.client.wait_for('message', check=lambda m: m.author != self.client.user, timeout=300)
                        break
                    except TimeoutError:
                        await self.scrim_channel.send(
                            "*WARNING* - Channel has been inactive for 20 minutes. Deleting channels and associated roles.")
                        await self.bravo_role.delete(reason="Scrim finished!")
                        await self.alpha_role.delete(reason="Scrim finished!")
                        await self.alpha_voice.delete(reason="Scrim finished!")
                        await self.bravo_voice.delete(reason="Scrim finished!")
                        await self.scrim_channel.delete(reason="Scrim finished!")


def setup(client):
    client.add_cog(ScrimOrganization(client))
