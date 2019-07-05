"""Module handling weapon and team compositions."""
# pylint: disable=E0102
import logging
import re
from io import BytesIO
import discord
from discord.ext import commands
from sqlalchemy import select, and_, exc
from bin.loadout import Loadout
from bin.decoder import decode
from core import DBHandler


class TeamComposer(DBHandler, commands.Cog):
    """Module handling weapon and team compositions."""

    def __init__(self, client):
        """Init the Team Composer cog."""
        super().__init__()
        self.client = client

        self.team_profiler = self.get_table("main", "team_profile")
        self.team_comps = self.get_table("main", "team_comp")

        self.get_meta("main").create_all(
            bind=self.get_db("main"),
            tables=[self.team_profiler, self.team_comps]
        )

    @commands.group(case_insensitive=True)
    async def compose(self, ctx):
        """Team Composition command group. Does nothing on it's own."""

    @compose.command()
    async def team(self, ctx, id: int = None):
        """Compose team command."""
        if id is not None:
            team_profile = self.get_db("main").execute(
                select([self.team_profiler]). \
                where(self.team_profiler.columns.team_id == id)  #pylint: disable=no-member
            ).fetchone()

            if team_profile is not None:
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
                embed.add_field(
                    name="Team Roster:",
                    value=f"{p_2}\n{p_3}\n{p_4}\n{p_5}\n{p_6}\n{p_7}"
                )
                embed.add_field(name="Team Captain", value=cap.mention)
                embed.add_field(name="Team ID:", value=team_profile["team_id"])

                await ctx.send(embed=embed)
            else:
                await ctx.send("Command Failed - Team does not exist.")
        else:
            await ctx.send("Command failed - Team ID not provided.")

    @compose.command()
    async def loadout(self, ctx, id: int = None):
        """Compose loadout command."""
        if id is not None:
            team_comp = self.get_db("main").execute(
                select([self.team_comps]). \
                where(and_( \
                        self.team_comps.columns.author_id ==  # pylint: disable=E1101
                        ctx.message.author.id,
                        self.team_comps.columns.comp_id == id  # pylint: disable=E1101
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
                        description=team_comp[f"weapon_{i+1}_role"] + " - " +
                        team_comp[f"weapon_{i+1}_desc"],
                        color=discord.Color.dark_blue()
                    )
                    image, loadout = self.create_image_loadout(
                        team_comp[f"weapon_{i+1}"], decoded=True
                    )
                    embed.set_image(url="attachment://loadout.png")
                    embed.title = f"Weapon #{i+1} - {loadout['weapon']['main']['name']}"

                    await ctx.send(embed=embed, file=image)
            else:
                await ctx.send("Command Failed - Composition ID is invalid.")
        else:
            await ctx.send(
                "Command Failed - Composition ID has not been provided."
            )

    @compose.command()
    async def new_team(self, ctx):
        """Comp create team command."""
        check = lambda m: m.author == ctx.message.author

        players = []
        await ctx.send(
            "Team Creation process initialized. Am I to assume that you are the captain of this new team? `[y/n]`"
        )
        while True:
            msg = await self.client.wait_for(
                "message", timeout=60, check=check
            )

            if msg.content.lower() == "y":
                players.append(ctx.message.author.id)
                break
            elif msg.content.lower() == "n":
                await ctx.send(
                    "Alright. Who is the captain? Please provide an @ mention or user ID."
                )
                msg = self.get_userid(
                    await self.client.wait_for("message", timeout=120, check=check)
                )  # yapf: disable

                if msg is None:
                    await ctx.send(
                        "No captain specified - Aborting creation..."
                    )
                    return
                players.append(msg)
                break
            else:
                await ctx.send(
                    "Invalid response - please reply `y` or `n` to continue."
                )
                continue

        for i in range(2, 8):
            await ctx.send(
                f"Alright, who's player {i}? Provide an @ mention or user ID."
            )
            if i > 4:
                await ctx.send(
                    "`Note: More than 4 players is optional. Respond with 'none' in order to set no player.`"
                )
            msg = self.get_userid(
                await self.client.wait_for("message", timeout=120, check=check)
            )  # yapf: disable

            if msg is None:
                if i <= 4:
                    await ctx.send(
                        "No player specified - Aborting creation..."
                    )
                    return
                await ctx.send("No player specified - Assuming `None`.")
                players.append(None)
            else:
                players.append(msg)

        await ctx.send(
            "Alright, that's your roster set up! Now, what will be your team name?"
        )
        name = await self.client.wait_for("message", timeout=60, check=check)
        name = name.content
        await ctx.send("What will be your team's description?")
        desc = await self.client.wait_for("message", timeout=60, check=check)
        desc = desc.content
        await ctx.send(f"Registering {name} into the database...")
        ex = self.get_db("main").execute(
            self.team_profiler. \
            insert(None). \
            values(
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
        await ctx.send(
            f"Alright! You're all set up! Your team ID is {ex.inserted_primary_key}. Good luck, godspeed, and take care out there."
        )

    @compose.command()
    async def new_loadout(self, ctx):
        """Comp create loadout command."""
        comp = {
            "name": "",
            "description": "",
            "weapon_1": {},
            "weapon_2": {},
            "weapon_3": {},
            "weapon_4": {}
        }

        check = lambda m: m.author == ctx.message.author

        await ctx.send("Starting composition creation process.")
        for i in range(4):
            while True:
                await ctx.send(
                    f"What's loadout #{i + 1}? \n `Please use https://selicia.github.io/en_US/ to specify a loadout.`"
                )
                msg = await self.client.wait_for(
                    "message", timeout=600, check=check
                )
                if len(msg.content) == 58 and \
                msg.content[:33] == "https://selicia.github.io/en_US/#":

                    image = self.create_image_loadout(msg.content[33:])
                    await ctx.send("Is this correct? `[y/n]`", file=image)
                    con = await self.client.wait_for(
                        "message", timeout=30, check=check
                    )
                    if con.content.lower() == "y":
                        comp[f"weapon_{i + 1}"].update(
                            loadout=msg.content[33:]
                        )
                        await ctx.send(
                            "Loadout registered. What is the weapon's role?"
                        )
                        msg = await self.client.wait_for(
                            "message", timeout=120, check=check
                        )
                        comp[f"weapon_{i + 1}"].update(role=msg.content)
                        await ctx.send(
                            "Role assigned. Are there any extra details you would like to give about the weapon? [Playstyle, usage, viable maps, etc.]"
                        )
                        msg = await self.client.wait_for(
                            "message", timeout=600, check=check
                        )
                        comp[f"weapon_{i + 1}"].update(desc=msg.content)
                        await ctx.send("Alright.")
                        break

                    elif con.content.lower() == "n":
                        await ctx.send("Understood. Starting over...")
                        continue
                    else:
                        await ctx.send("Invalid Response - Restarting...")
                        continue

        await ctx.send("Ok, what will be the name of this composition?")
        msg = await self.client.wait_for("message", timeout=300, check=check)
        comp["name"] = msg.content
        await ctx.send(
            "Are there any extra details you would like to provide about this composition? [Map/Mode use, strategies, etc.]"
        )
        msg = await self.client.wait_for("message", timeout=600, check=check)
        comp["description"] = msg.content

        await ctx.send(
            f"Inserting team composition `{comp['name']}` into the database..."
        )
        ex = self.get_db("main").execute(
            self.team_comps.insert(None).values(
                author_id=ctx.message.author.id,
                name=comp["name"],
                description=comp["description"],
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
        await ctx.send(
            f"Success! Your composition ID is {ex.inserted_primary_key}. Good luck, godspeed, and take care out there."
        )

    @compose.command()
    async def edit_team(self, ctx, id, field=None, *, value=None):
        """Comp modify team command."""
        team = self.get_db("main").execute(
            select([self.team_profiler]). \
            where(and_( \
                    self.team_profiler.columns.captain ==  # pylint: disable=E1101
                    ctx.message.author.id,
                    self.team_profiler.columns.team_id == id  # pylint: disable=E1101
                )
            )
        ).fetchone()
        if team is not None:

            try:
                if re.search(r"player_.", field):
                    try:
                        value = ctx.message.mentions[0].id
                    except IndexError:
                        value = self.client.get_user(int(value)).id
                        if value is None:
                            await ctx.send(
                                "Command Failed - Invalid player specified."
                            )
                            return
                self.get_db("main").execute(
                    self.team_profiler. \
                    update(None). \
                    where(and_( \
                            self.team_profiler.columns.captain ==  # pylint: disable=E1101
                            ctx.message.author.id,
                            self.team_profiler.columns.team_id == id  # pylint: disable=E1101
                        )
                    ).values(**{field:value})
                )
            except exc.CompileError as err:
                await ctx.send(
                    "Command Failed - Invalid field, value, column."
                )
                raise exc.CompileError from err
            else:
                await ctx.send(f"{field.title()} updated!")
        else:
            await ctx.send(
                f"Command Failed - You do not have a team. To create a team, use `{ctx.prefix}comp create team`."
            )

    @compose.command()
    async def edit_loadout(self, ctx, id, field=None, *, value=None):
        """Comp modify loadout command."""
        loadout = self.get_db("main").execute(
            select([self.team_comps]). \
            where(and_(
                    self.team_comps.columns.author_id == ctx.message.author.id,  # pylint: disable=E1101
                    self.team_comps.columns.comp_id == id  # pylint: disable=E1101
                )
            )
        ).fetchone()
        if loadout is not None:

            try:
                if re.search(r"weapon_.\b", value) and not (
                    len(value) == 58
                    and value[:33] == 'https://selicia.github.io/en_US/#'
                ):
                    raise exc.CompileError
                self.get_db("main").execute(
                    self.team_comps. \
                    update(None).\
                    where(and_(
                            self.team_comps.columns.author_id ==  # pylint: disable=E1101
                            ctx.message.author.id,
                            self.team_comps.columns.comp_id == id  # pylint: disable=E1101
                        )
                    ).values(**{field: value})
                )
            except exc.CompileError:
                await ctx.send(
                    "Command Failed - Invalid field, value or column."
                )
            else:
                await ctx.send(f"{field.title()} updated!")
        else:
            await ctx.send(
                f"Command Failed - Loadout does not exist. To create a loadout, use `{ctx.prefix}comp create loadout`."
            )

    @compose.command()
    async def delete_team(self, ctx, id: int = None):
        """Delete a loadout."""
        if id is not None:
            team = self.get_db('main').execute(
                select([self.team_profiler]).where(
                    and_(
                        self.team_profiler.columns['captain'] == ctx.message.author.id,
                        self.team_profiler.columns['team_id'] == id
                    )
                )
            ).fetchone()

            if team is not None:
                await ctx.send("This is a destructive operation, are you sure you wish to delete this team? `[y/n]`")
                confirm = await self.client.wait_for("message", timeout=60, check=lambda m: m.author == ctx.message.author)
                if confirm.content.lower() == "y":
                    self.get_db('main').execute(
                        self.team_profiler.delete().where(
                            and_(
                                self.team_profiler.columns['captain'] == ctx.message.author.id,
                                self.team_profiler.columns['team_id'] == id
                            )
                        )
                    )
                    await ctx.send("Understood. Team deleted.")
                else:
                    await ctx.send("Understood. Aborting deletion.")
            else:
                await ctx.send("Command Failed - Team does not exist.")

    @compose.command()
    async def delete_loadout(self, ctx, id: int = None):
        """Delete a composition."""
        if id is not None:
            loadout = self.get_db('main').execute(
                select([self.team_comps]).where(
                    and_(
                        self.team_comps.columns['author_id'] == ctx.message.author.id,
                        self.team_comps.columns['comp_id'] == id
                    )
                )
            ).fetchone()

            if loadout is not None:
                await ctx.send("This is a destructive operation, are you sure you wish to delete this composition? `[y/n]`")
                confirm = await self.client.wait_for("message", timeout=60, check=lambda m: m.author == ctx.message.author)
                if confirm.content.lower() == "y":
                    self.get_db('main').execute(
                        self.team_comps.delete().where(
                            and_(
                                self.team_comps.columns['author_id'] == ctx.message.author.id,
                                self.team_comps.columns['comp_id'] == id
                            )
                        )
                    )
                    await ctx.send("Understood. Loadout deleted.")
                else:
                    await ctx.send("Understood. Aborting deletion.")
            else:
                await ctx.send("Command Failed - Loadout does not exist.")

    @compose.command()
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

    def get_userid(self, msg):
        """Return the user id from a message, returns none if not found."""
        try:
            cap = self.client.get_user(int(msg.content))
            if cap is None:
                raise ValueError
            cap = cap.id
        except ValueError:
            try:
                cap = msg.mentions[0].id
            except IndexError:
                cap = None
        return cap

    @staticmethod
    def create_image_loadout(msg, decoded=False):
        """Create an image loadout from message.content."""
        image_loadout = decode(msg)
        image_loadout = Loadout().convert_loadout(image_loadout)
        with Loadout().generate_loadout_image(image_loadout) as image:
            out_buffer = BytesIO()
            image.save(out_buffer, "png")
            out_buffer.seek(0)
        image_loadout = discord.File(fp=out_buffer, filename="loadout.png")
        if decoded is False:
            return image_loadout
        return image_loadout, Loadout().convert_loadout(decode(msg))


def setup(client):
    """Add the module to the bot."""
    client.add_cog(TeamComposer(client))
    logging.info("Team Composer Module Online.")
