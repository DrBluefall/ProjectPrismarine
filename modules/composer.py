"""Module handling weapon and team compositions."""

import logging
import asyncio
import discord
from discord.ext import commands
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, select


class TeamComposer(commands.Cog):
    """Module handling weapon and team compositions."""

    # ... The order of methods in these classes are:
    # ... - Command groups
    # ... - Subcommands (in same order as command groups)
    # ... - Help subcommand
    # ... - Module commands
    # ... - Other discord.ext methods
    # ... - Normal methods
    # ... - Class methods
    # ... - Static methods

    def __init__(self, client):
        """Init the MyModule cog."""
        self.client = client
        self.db = create_engine("sqlite:///main.db")
        self.metadata = MetaData(self.db)

        self.team_profiler = Table(
            "team_profile",
            self.metadata,
            Column("captain", Integer, nullable=False),
            Column("player_2", Integer, nullable=False),
            Column("player_3", Integer, nullable=False),
            Column("player_4", Integer, nullable=False),
            Column("player_5", Integer),
            Column("player_6", Integer),
            Column("player_7", Integer),
            Column("name", String),
            Column("team_id", Integer, primary_key=True)

        )

        self.team_comps = Table(
            "team_comp",
            self.metadata,
            Column("comp_id", Integer, primary_key=True),
            Column("name", String),
            Column("desc", String),
            Column("weapon_1", String, server_default="0000000000000000000000000"),
            Column("weapon_1_role", String),
            Column("weapon_1_desc", String),
            Column("weapon_2", String, server_default="0000000000000000000000000"),
            Column("weapon_2_role", String),
            Column("weapon_2_desc", String),
            Column("weapon_3", String, server_default="0000000000000000000000000"),
            Column("weapon_3_role", String),
            Column("weapon_3_desc", String),
            Column("weapon_4", String, server_default="0000000000000000000000000"),
            Column("weapon_4_role", String),
            Column("weapon_4_desc", String)
        )
        self.metadata.create_all(tables=[self.team_profiler, self.team_comps])

        self.c = self.db.connect()

    @commands.group(case_insensitive=True, ignore_extra=False, invoke_without_command=True)
    async def comp(self, ctx, team_id: int = None):
        """Team Composition command group. If invoked with a team ID, it will return the team that has a matching ID."""
        if ctx.invoked_subcommand is not None:
            return
        
        if team_id is not None:
            team_profile = self.c.execute(
                select([self.team_profiler]).where(self.team_profiler.columns.team_id == team_id) #pylint: disable=no-member
            ).fetchone()

            embed = discord.Embed(
                title=f"Team Profile - {team_profile['name']}",
                color=discord.Color.orange()
            )
            cap = self.client.get_user(team_profile["captain"])
            p_2 = self.client.get_user(team_profile["player_2"]).mention
            p_3 = self.client.get_user(team_profile["player_3"]).mention
            p_4 = self.client.get_user(team_profile["player_4"]).mention
            p_5 = self.client.get_user(team_profile["player_5"])
            if p_5 is not None:
                p_5 = p_5.mention
            p_6 = self.client.get_user(team_profile["player_6"])
            if p_6 is not None:
                p_6 = p_6.mention
            p_7 = self.client.get_user(team_profile["player_7"])
            if p_7 is not None:
                p_7 = p_7.mention
            embed.add_field(name="Team Roster:", value=f"{p_2}\n{p_3}\n{p_4}\n{p_5}\n{p_6}\n{p_7}")
            embed.add_field(name="Team Captain", value=cap.mention)
            embed.add_field(name="Team ID:", value=team_profile["team_id"])
            
            

            await ctx.send(embed=embed)
            
        else:
            await ctx.send("Command failed - Team ID not provided.")


    @comp.command()
    async def create(self, ctx, type):
        """Create a team or team composition in the bot. A team can have 4-6 players."""

        def check(m):
            return m.author == ctx.message.author

        try:
            if type.lower() == "team":
                players = []
                await ctx.send("Team Creation process initialized. Am I to assume that you are the captain of this new team? `[y/n]`")
                while True:
                    msg = await self.client.wait_for("message", timeout=60, check=check)

                    if msg.content.lower() == "y":
                        cap = ctx.message.author.id
                        players.append(cap)
                        break
                    elif msg.content.lower() == "n":
                        await ctx.send("Alright. Who is the captain? Please provide an @ mention or user ID.")
                        msg = await self.client.wait_for("message", timeout=120, check=check)
                        try:
                            cap = self.client.get_user(int(msg.content))
                            if cap is None:
                                raise ValueError
                            else:
                                players.append(cap.id)
                        except ValueError:
                            try:
                                cap = msg.mentions[0].id
                                players.append(cap)
                                break
                            except IndexError:
                                await ctx.send("No captain specified - Aborting creation...")
                                return
                    else:
                        await ctx.send("Invalid response - please reply `y` or `n` to continue.")
                
                for i in range(6):
                    await ctx.send(f"Alright, who's player {i + 2}? Provide an @ mention or user ID.")
                    if i + 1 >= 4:
                        await ctx.send("`Note: More than 4 players is optional. Respond with 'none' in order to set no player.`")
                    msg = await self.client.wait_for("message", timeout=120, check=check)
                    if i + 2 <= 4:
                        try:
                            player = self.client.get_user(int(msg.content))
                            if player is None:
                                raise ValueError
                            else:
                                players.append(player.id)
                                continue
                        except ValueError:
                            try:
                                player = msg.mentions[0].id
                                players.append(player)
                                continue
                            except IndexError:
                                await ctx.send("No player specified - Aborting creation...")
                                return
                    elif i + 2 >= 4 and msg.content.lower() != "none":
                        try:
                            player = self.client.get_user(int(msg.content))
                            if player is None:
                                raise ValueError
                            else:
                                players.append(player.id)
                                continue
                        except ValueError:
                            try:
                                player = msg.mentions[0].id
                                players.append(player)
                                continue
                            except IndexError:
                                await ctx.send("No player specified - Assuming none...")
                                player = None
                                players.append(player)
                                continue
                    else:
                        players.append(None)
                
                await ctx.send("Alright, that's your roster set up! Now, what will be your team name?")

                name = await self.client.wait_for("message", timeout=60, check=check)
                name = name.content

                print(players)

                await ctx.send(f"Registering {name} into the database...")

                ex = self.c.execute(
                    self.team_profiler.insert(None).values(
                        captain=players[0],
                        player_2=players[1],
                        player_3=players[2],
                        player_4=players[3],
                        player_5=players[4],
                        player_6=players[5],
                        player_7=players[6],
                        name=name     
                    )
                )

                await ctx.send(f"Alright! You're all set up! Your team ID is {ex.inserted_primary_key}. Good luck, godspeed, and take care out there.")
                         
        except asyncio.TimeoutError:
            await ctx.send("Command timed out - Process aborted.")

    @comp.command()
    async def help(self, ctx):
        """Team Composer command documentation."""
        embed = discord.Embed(
            title=f"Project Prismarine - {__class__.__name__} Documentation",
            color=discord.Color.dark_red()
        )
        for command in self.walk_commands():
            embed.add_field(
                name=ctx.prefix + command.qualified_name, value=command.help
            )
        await ctx.send(embed=embed)

    @commands.command()
    async def mycommand(self, ctx, name_user, *, nickname: str):
        """... Write module command docstring."""
        # ... Write module command


def setup(client):
    """Add the module to the bot."""
    client.add_cog(TeamComposer(client))
    logging.info("Team Composer Module Online.")