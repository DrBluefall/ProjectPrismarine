"""Module handling weapon and team compositions."""

import logging
import asyncio
import re
import discord
from discord.ext import commands
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, select, and_, exc
from io import BytesIO
from bin.loadout import Loadout
from bin.decoder import decode


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
        """Init the Team Composer cog."""
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
            Column("description", String),
            Column("team_id", Integer, primary_key=True)

        )

        self.team_comps = Table(
            "team_comp",
            self.metadata,
            Column("comp_id", Integer, primary_key=True),
            Column("author_id", Integer),
            Column("name", String),
            Column("description", String),
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
    async def comp(self, ctx, type, id: int = None):
        """Team Composition command group. If invoked with a team ID, it will return the team that has a matching ID."""
        if ctx.invoked_subcommand is not None:
            return
        
        if type.lower() == "team":
            if id is not None:
                team_profile = self.c.execute(
                    select([self.team_profiler]).where(self.team_profiler.columns.team_id == id) #pylint: disable=no-member
                ).fetchone()

                embed = discord.Embed(
                    title=f"Team Profile - {team_profile['name']}",
                    color=discord.Color.orange(),
                    description=team_profile["description"]
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
        elif type.lower() == "loadout":
            if id is not None:
                team_comp = self.c.execute(
                    select([self.team_comps]).where(
                        and_(
                            self.team_comps.columns.author_id == ctx.message.author.id, #pylint: disable=no-member
                            self.team_comps.columns.comp_id == id #pylint: disable=no-member
                        )
                    )
                ).fetchone()

                if team_comp is not None:
                    embed = discord.Embed(
                        title=f"Weapon Composition - {team_comp['name']}",
                        description=team_comp["description"],
                        color=discord.Color.red()
                    )
                    await ctx.send(embed=embed)

                    for i in range(4):
                        embed = discord.Embed(
                            description=team_comp[f"weapon_{i+1}_role"] + " - " + team_comp[f"weapon_{i+1}_desc"],
                            color=discord.Color.dark_blue()
                        )
                        loadout = decode(team_comp[f"weapon_{i+1}"])
                        loadout = Loadout().convert_loadout(loadout)
                        with Loadout().generate_loadout_image(loadout) as _loadout:
                            out_buffer = BytesIO()
                            _loadout.save(out_buffer, "png")
                            out_buffer.seek(0)
                        _loadout = discord.File(fp=out_buffer, filename="loadout.png")
                        embed.set_image(url="attachment://loadout.png")
                        embed.title = f"Weapon #{i+1} - {loadout['weapon']['main']['name']}"

                        await ctx.send(embed=embed, file=_loadout) 
                else:
                    await ctx.send("Command Failed - Composition ID is invalid.")           
            else:
                await ctx.send("Command Failed - Composition ID has not been provided.")
        else:
            await ctx.send(f"Command Failed - `type` parameter must be `team` or `loadout`, not `{type}`.")

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

                await ctx.send("What will be your team's description?")

                desc = await self.client.wait_for("message", timeout=60, check=check)
                desc = desc.content

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
                        name=name,
                        description=desc  
                    )
                )

                await ctx.send(f"Alright! You're all set up! Your team ID is {ex.inserted_primary_key}. Good luck, godspeed, and take care out there.")

            elif type.lower() == "loadout":
                comp = {
                    "name": "",
                    "description": "",
                    "weapon_1": {},
                    "weapon_2": {},
                    "weapon_3": {},
                    "weapon_4": {}
                }

                await ctx.send("Starting composition creation process.")
                for i in range(4):
                    while True:
                        await ctx.send(f"What's loadout #{i + 1}? \n `Please use https://selicia.github.io/en_US/#0000000000000000000000000 to specify a loadout.`")
                        msg = await self.client.wait_for("message", timeout=600, check=check)
                        if len(msg.content) == 58 and msg.content[:33] == "https://selicia.github.io/en_US/#":
                            _loadout = decode(msg.content[33:])
                            _loadout = Loadout().convert_loadout(_loadout)
                            with Loadout().generate_loadout_image(_loadout) as loadout:
                                out_buffer = BytesIO()
                                loadout.save(out_buffer, "png")
                                out_buffer.seek(0)
                            _loadout = discord.File(fp=out_buffer,filename="loadout.png")
                            await ctx.send("Is this correct? `[y/n]`", file=_loadout)
                            con = await self.client.wait_for("message", timeout=30, check=check)
                            if con.content.lower() == "y":
                                comp[f"weapon_{i + 1}"].update(loadout=msg.content[33:])
                                
                                await ctx.send("Loadout registered. What is the weapon's role?")
                                msg = await self.client.wait_for("message", timeout=120, check=check)
                                comp[f"weapon_{i + 1}"].update(role=msg.content)
                                await ctx.send("Role assigned. Are there any extra details you would like to give about the weapon? [Playstyle, usage, viable maps, etc.]")
                                msg = await self.client.wait_for("message", timeout=600, check=check)
                                comp[f"weapon_{i + 1}"].update(description=msg.content)
                                await ctx.send("Alright.")
                                break

                            elif con.content.lower() == "n":
                                await ctx.send("Understood. Starting over...")
                                continue
                            else:
                                await ctx.send("Command Failed - Invalid response.")
                                return
                await ctx.send("Ok, what will be the name of this composition?")
                msg = await self.client.wait_for("message", timeout=300, check=check)
                comp["name"] = msg.content
                await ctx.send("Are there any extra details you would like to provide about this composition? [Map/Mode use, strategies, etc.]")
                msg = await self.client.wait_for("message", timeout=600, check=check)
                comp["description"] = msg.content

                await ctx.send(f"Inserting team composition `{comp['name']}` into the database...")

                ex = self.c.execute(
                    self.team_comps.insert(None).values(
                        author_id=ctx.message.author.id,
                        name=comp["name"],
                        desc=comp["description"],
                        weapon_1=comp["weapon_1"]["loadout"],
                        weapon_1_role=comp["weapon_1"]["role"],
                        weapon_1_desc=comp["weapon_1"]["desc"],
                        weapon_2=comp["weapon_2"]["loadout"],
                        weapon_2_role=comp["weapon_2"]["role"],
                        weapon_2_desc=comp["weapon_2"]["desc"],
                        weapon_3=comp["weapon_3"]["loadout"],
                        weapon_3_role=comp["weapon_3"]["role"],
                        weapon_3_desc=comp["weapon_3"]["desc"],
                        weapon_4=comp["weapon_4"]["loadout"],
                        weapon_4_role=comp["weapon_4"]["role"],
                        weapon_4_desc=comp["weapon_4"]["desc"],
                    )
                )

                await ctx.send(f"Success! Your composition ID is {ex.inserted_primary_key}. Good luck, godspeed, and take care out there.")

            else:
                await ctx.send(f"Command failed - Specified type must be `team` or `loadout`, not {type}")
                         
        except asyncio.TimeoutError:
            await ctx.send("Command timed out - Process aborted.")
        
    @comp.group(case_insensitive=True)
    async def modify(self, ctx):
        pass
    
    @modify.command()
    async def team(self, ctx, field = None,*,value = None):

        team = self.c.execute(
            select([self.team_profiler]).where(self.team_profiler.columns.captain == ctx.message.author.id) #pylint: disable=no-member
        ).fetchone()
        if team is not None:
            if re.search(r"player_.", field) is not None:
                try:
                    value = ctx.message.mentions[0].id
                except IndexError:
                    value = self.client.get_user(int(value)).id
                    if value is None:
                        await ctx.send("Command Failed - Invalid player specified.")
                        return
                try:
                    self.c.execute(
                        self.team_profiler.update(None).where(self.team_profiler.columns.captain == ctx.message.author.id).values(**{field : value}) #pylint: disable=no-member
                    )
                    await ctx.send("Team roster updated!")
                    
                except exc.StatementError as except_:
                    logging.exception(except_)
                    await ctx.send("Command Failed - Internal Exception.")
            elif field == "desc":
                self.c.execute(
                    self.team_profiler.update(None).where(self.team_profiler.columns.captain == ctx.message.author.id).values(description = value)#pylint: disable=no-member
                )
                await ctx.send("Description updated!")
            elif field == "name":
                self.c.execute(
                    self.team_profiler.update(None).where(self.team_profiler.columns.captain == ctx.message.author.id).values(name = value)#pylint: disable=no-member
                )
                await ctx.send("Name updated!")


        else:
            await ctx.send(f"Command Failed - You do not have a team. To create a team, use `{ctx.prefix}comp create team`.")
                

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
