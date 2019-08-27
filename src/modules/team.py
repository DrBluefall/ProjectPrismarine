# Standard Library Imports

from asyncio import TimeoutError
from io import BytesIO

# Third-Party Imports

import discord
from discord.ext import commands
from datetime import datetime

# Local Project Imports

from utils.loadout_gen import generate_image


class Team(commands.Cog):
    """Module for managing teams."""

    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.group()
    async def team(self, ctx):
        pass

    @team.command()
    async def profile(self, ctx: commands.Context, captain=None):
        if captain is None:
            captain = ctx.message.author
        else:
            try:
                captain = await self.client.fetch_user(int(captain))
            except ValueError:
                try:
                    captain = ctx.message.mentions[0]
                except IndexError:
                    await ctx.send("Command Failed - Invalid user specified.")
                    return
            except discord.NotFound:
                await ctx.send("Command Failed - Invalid user specified.")
                return

        team = self.client.dbh.get_team(captain.id)
        if team is None:
            await ctx.send("Command Failed - User does not captain a team.")
            return

        team_embed = discord.Embed(
            title=f"Team Profile - {team['team']['name']}",
            color=(discord.Color.from_rgb(148, 0, 211)
                   if team['team']['recruiting'] is False
                   else discord.Color.from_rgb(0, 255, 0)),
            description=team['team']['description']
        )
        tl = []
        if team['team']['recent_tournaments'] is not None:
            for tourney in team['team']['recent_tournaments']:
                s = f"""Tournament: `{tourney['tourney']}`\nPlace: `{tourney['place']}`\nResult Registered: `{datetime.fromtimestamp(tourney['date']).strftime("%d %B %Y")}`"""
                tl.append(s)
            team_embed.add_field(
                name="Recent Tournaments:",
                value='\n\n'.join(tl),
                inline=True
            )
        team_embed.add_field(
            name='Roster:',
            value='\n'.join([(await self.client.fetch_user(team['players'][i]['id'])).mention for i in range(len(team['players']))])
        )
        team_embed.add_field(
            name="Captain:",
            value=captain.mention
        )
        team_embed.add_field(
            name="Team Created:",
            value=team['team']['creation_time']
        )

        if team['team']['thumbnail'] is not None:
            team_embed.set_thumbnail(url=team['team']['thumbnail'])

        team_msg = await ctx.send(embed=team_embed)

        player_embeds = []

        for profile in team['players']:
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

        player_msg = await ctx.send(**player_embeds[0])
        await player_msg.add_reaction('◀')
        await player_msg.add_reaction('▶')
        await player_msg.add_reaction('❌')
        index = 0
        while True:
            reaction, user = await self.client.wait_for(
                'reaction_add',
                check=lambda r, u: u == ctx.message.author and str(r.emoji) in ['◀', '▶', '❌']
            )
            await reaction.remove(user)
            if str(reaction.emoji) == '❌':
                await player_msg.delete()
                await team_msg.delete()
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

    @team.command()
    async def create(self, ctx: commands.Context, name: str = None):
        """Create a brand-new team."""

        if self.client.dbh.get_profile(ctx.message.author.id) is None:
            await ctx.send(
                f"Command Failed - You need a profile to create a team! Create one with `{ctx.prefix}player create`.")
            return

        await ctx.send("Team creation in progress...")
        if name is None:
            await ctx.send("What will be the name of your new team?")
            name = await self.client.wait_for('message', timeout=60, check=lambda m: m.author == ctx.message.author)
            name = name.content

        res = self.client.dbh.new_team(ctx.message.author.id, name)
        if res is None:
            await ctx.send(
                "Command Failed - Every user may only captain one team. If you wish to captain a new team, please delete your current team or assign it a new captain.")
        else:
            await ctx.send(
                f"""Your team is all set! `pc.team profile` will display your team's info, as well as your roster.
                \rThat's all for now. Good luck and godspeed.""")

    @team.command()
    async def invite(self, ctx: commands.Context, player=None):

        team = self.client.dbh.get_team(ctx.message.author.id)
        if team is None:
            await ctx.send(f"Command Failed - You don't have a team! Create one with `{ctx.prefix}team create`.")
        else:
            team = team["team"]

        if player is None:
            await ctx.send("Command Failed - No player specified.")
            return
        try:
            player = await self.client.fetch_user(int(player))
        except ValueError:
            try:
                player = ctx.message.mentions[0]
            except IndexError:
                await ctx.send("Command Failed - Invalid User specified.")
                return
        except discord.NotFound:
            await ctx.send("Command Failed - Invalid User specified.")
            return

        player_profile = self.client.dbh.get_profile(player.id)
        if player_profile is None:
            await ctx.send("Command Failed - Recipient does not have a profile!")
            return
        elif player_profile['is_private'] is True:
            await ctx.send(
                "Command Failed - Recipient has set their profile to `private`, and therefore cannot receive invites. Sorry about that :/")
            return
        elif player_profile['team_id'] is not None:
            await ctx.send("Command Failed - Recipient is already on a team.")

        dm_channel = await player.create_dm() if player.dm_channel is None else player.dm_channel
        embed = discord.Embed(
            title="Team Invite Received!",
            description=f"""
            You have been invited to {ctx.message.author.name}'s team, `{team['name']}`! Do you wish to accept the invite?
            """
        )
        await ctx.send("Invite Sent!")

        msg = await dm_channel.send(embed=embed)
        await msg.add_reaction('✅')
        await msg.add_reaction('❌')
        while True:
            reaction, _ = await self.client.wait_for(
                'reaction_add',
                check=lambda r, u: u == player and str(r.emoji) in ['✅', '❌']
            )
            del _

            if str(reaction.emoji) == '❌':
                await msg.delete()
                await dm_channel.send("Understood. I will alert the captain of your response.")
                dm_channel = (await ctx.message.author.create_dm()
                              if ctx.message.author.dm_channel is None else ctx.message.author.dm_channel)
                await dm_channel.send(f"Your invitation sent to {player.name} has been rejected. Sorry about that :/")
                return
            elif str(reaction.emoji) == '✅':
                await msg.delete()
                await dm_channel.send("Understood! I will update your profile and alert your new captain immediately!")
                self.client.dbh.add_player(ctx.message.author.id, player.id)
                dm_channel = (await ctx.message.author.create_dm()
                              if ctx.message.author.dm_channel is None else ctx.message.author.dm_channel)
                await dm_channel.send(f"Your invite sent to {player.name} has been accepted! Cheers! :smiley:")
            else:
                continue

    @team.command()
    async def set_desc(self, ctx: commands.Context, *, text):
        self.client.dbh.update_desc(ctx.message.author.id, text)
        await ctx.send("Description updated!")

    @team.command()
    async def recruiting(self, ctx: commands.Context):
        await ctx.send(f"Team recruiting status set to `{self.client.dbh.toggle_recruit(ctx.message.author.id)}`!")

    @team.command()
    async def thumbnail(self, ctx: commands.Context, *, url=None):
        if url is None:
            try:
                url = ctx.message.attachments[0]
                url = url.url
            except IndexError:
                await ctx.send("Command Failed - No URL/Image provided.")
                return
        self.client.dbh.update_thumbnail(ctx.message.author.id, url)
        await ctx.send("Updated thumbnail! :smiley:")

    @team.command()
    async def add_tourney(self, ctx: commands.Context, place: int = None, *, tourney_name: str = None):
        self.client.dbh.add_tourney(ctx.message.author.id, tourney_name, place)
        await ctx.send("Added tournament record to profile! :smiley:")

    @team.command()
    async def delete(self, ctx: commands.Context):
        confirm = await ctx.send(
            "This is a destructive operation, with no means of undoing it. Are you *absolutely* sure that you want to delete your team?"
        )
        await confirm.add_reaction('❌')
        await confirm.add_reaction('✅')
        try:
            reaction, _ = await self.client.wait_for(
                'reaction_add',
                check=lambda r, u: u == ctx.message.author and str(r.emoji) in ['❌', '✅'],
                timeout=60
            )
            del _
            if str(reaction.emoji) == '❌':
                await confirm.delete()
                await ctx.send("Understood. Aborting deletion.")
                return
            elif str(reaction.emoji) == '✅':
                await confirm.delete()
                self.client.dbh.delete_team(ctx.message.author.id)
                await ctx.send(f"""
                Understood. There will be a 3-day buffer between now and when your team is deleted. During this time, you have the ability to recover your team with `{ctx.prefix}team recover`. During this time, you will also not be able to create a new team. Certain commands will also be made unusable during the deletion process.
                
                \rFor now, take care out there.
                """)
        except TimeoutError:
            await ctx.send("Deletion Aborted - Command timed out.")
            return

    @team.command()
    async def recover(self, ctx: commands.Context):
        self.client.dbh.recover_team(ctx.message.author.id)
        await ctx.send("Team recovered!")


def setup(client):
    client.add_cog(Team(client))
