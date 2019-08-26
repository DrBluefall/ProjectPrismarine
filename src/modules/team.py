# Third-Party Imports

import discord
from discord.ext import commands


class Team(commands.Cog):
    """Module for managing teams."""

    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.group()
    async def team(self, ctx):
        pass

    @team.command()
    async def create(self, ctx: commands.Context, name: str = None):
        """Create a brand-new team."""

        if self.client.dbh.get_profile(ctx.message.author.id) is None:
            await ctx.send(f"Command Failed - You need a profile to create a team! Create one with `{ctx.prefix}player create`.")
            return

        await ctx.send("Team creation in progress...")
        if name is None:
            await ctx.send("What will be the name of your new team?")
            name = await self.client.wait_for('message', timeout=60, check=lambda m: m.author == ctx.message.author)
            name = name.content
        
        res = self.client.dbh.new_team(ctx.message.author.id, name)
        if res is None:
            await ctx.send("Command Failed - Every user may only captain one team. If you wish to captain a new team, please delete your current team or assign it a new captain.")
        else:
            await ctx.send(
                f"""Your team is all set! `pc.team profile` will display your team's info, as well as your roster.
                \rThat's all for now. Good luck and godspeed.""")
    
    @team.command()
    async def invite(self, ctx: commands.Context, player = None):

        team = self.client.dbh.get_team(ctx.message.author.id)["team"]
        if team is None:
            await ctx.send(f"Command Failed - You don't have a team! Create one with `{ctx.prefix}team create`.")

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
            await ctx.send("Command Failed - Recipient has set their profile to `private`, and therefore cannot receive invites. Sorry about that :/")
            return
        
        dm_channel = await player.create_dm() if player.dm_channel is None else player.dm_channel
        embed = discord.Embed(
            title="Team Invite Received!",
            description=f"""
            You have been invited to {ctx.message.author.name}'s team, `{team['name']}`! Do you wish to accept the invite?
            """
        )

        msg = await dm_channel.send(embed=embed)
        await msg.add_reaction('✅')
        await msg.add_reaction('❌')
        reaction, _ = await self.client.wait_for(
                            'reaction_add',
                            check=lambda r, u: u == ctx.message.author and (r.emoji == '✅' or r.emoji == '❌')
                            )
        del _

        if reaction.emoji == '❌':
            await msg.delete()
            await dm_channel.send("Understood. I will alert the captain of your response.")
            dm_channel = (await ctx.message.author.create_dm()
                          if ctx.message.author.dm_channel is None else ctx.message.author.dm_channel)
            await dm_channel.send(f"Your invitation sent to {player.name} has been rejected. Sorry about that :/")
            return
        elif reaction.emoji == '✅':
            await msg.delete()
            await dm_channel.send("Understood! I will update your profile and alert your new captain immediately!")
            self.client.dbh.add_player(ctx.message.author.id, player.id)
            dm_channel = (await ctx.message.author.create_dm()
                          if ctx.message.author.dm_channel is None else ctx.message.author.dm_channel)
            await dm_channel.send(f"Your invite sent to {player.name} has been accepted! Cheers! :smiley:")


def setup(client):
    client.add_cog(Team(client))
