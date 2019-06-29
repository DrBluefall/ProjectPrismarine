"""Module dealing with all SplatNet 2-related functions."""
import logging
from datetime import datetime
import requests
import discord
from discord.ext import commands, tasks
from sqlalchemy import create_engine, MetaData, select


class Splatnet(commands.Cog):
    """Contains all SplatNet 2-related functions."""

    def __init__(self, client):
        """Init the class."""
        self.client = client
        self.request_data_loop.start()  # pylint: disable=no-member
        self.request_data()

    @commands.group(case_insensitive=True)
    async def rotation(self, ctx):
        """List all the current rotation for all modes, including Salmon Run when it's open. If a mode is specified, it will only display that mode."""
        if ctx.invoked_subcommand is not None:
            return

        async with ctx.typing():

            await ctx.send(embed=SplatnetEmbeds.regular(self.data["regular"]))
            await ctx.send(embed=SplatnetEmbeds.ranked(self.data["ranked"]))
            await ctx.send(embed=SplatnetEmbeds.league(self.data["league"]))

            if datetime.now() > self.data["grizzco"]["time"]["start"]:
                await ctx.send(
                    embed=SplatnetEmbeds.salmon(self.data["grizzco"])
                )

    @rotation.command()
    async def turf(self, ctx):
        """List the current Turf War rotation."""
        await ctx.send(embed=SplatnetEmbeds.regular(self.data["regular"]))

    @rotation.command()
    async def ranked(self, ctx):
        """List the current Ranked Battle rotation."""
        await ctx.send(embed=SplatnetEmbeds.ranked(self.data["ranked"]))

    @rotation.command()
    async def league(self, ctx):
        """List the current League Battle rotation."""
        await ctx.send(embed=SplatnetEmbeds.league(self.data["league"]))

    @rotation.command()
    async def salmon(self, ctx):
        """List the current Salmon Run rotation."""
        await ctx.send(embed=SplatnetEmbeds.salmon(self.data["grizzco"]))

    @rotation.command()
    async def help(self, ctx):
        """Splatnet command documentation."""
        embed = discord.Embed(
            title=f"Project Prismarine - {__class__.__name__} Documentation",
            color=discord.Color.dark_red()
        )
        for command in self.walk_commands():
            embed.add_field(
                name=ctx.prefix + command.qualified_name, value=command.help
            )
        await ctx.send(embed=embed)

    @rotation.command()
    async def splatnet(self, ctx, index: int = 6):
        """
        List the currently available number of items on the SplatNet Shop.

        Parameters:
            -Index (Integer): The number of items to list. This must be a value between 1 and 6. Defaults to 6.

        Returns:
            - A list of embeds with each Splatnet item and info about it.

        """
        if index < 1 or index > 6:
            await ctx.send(
                "Command failed - Number of items listed must be a value between 1 and 6."
            )
            return
        async with ctx.typing():
            for i in range(index):
                embed, file = SplatnetEmbeds.splatnet(
                    self.data["splatnet"][i - 1]
                )
                embed.set_thumbnail(url=f"attachment://{file.filename}")
                await ctx.send(embed=embed, file=file)

    @tasks.loop(minutes=30)
    async def request_data_loop(self):
        """Loop over requesting data function."""
        await self.client.wait_until_ready()
        logging.info("Retrieving data from Splatoon2.ink...")
        self.request_data()

    def request_data(self):
        """Request and cache info from Splatoon2.ink."""
        header = {'User-Agent': 'Project Prismarine#6634'}
        schedules = requests.get(
            "https://splatoon2.ink/data/schedules.json", headers=header
        )
        coop_schedules = requests.get(
            "https://splatoon2.ink/data/coop-schedules.json", headers=header
        )
        merchandises = requests.get(
            "https://splatoon2.ink/data/merchandises.json", headers=header
        )

        try:
            schedules.raise_for_status()
            coop_schedules.raise_for_status()
            merchandises.raise_for_status()
        except requests.exceptions.HTTPError:
            logging.error("Retrieving data failed.")
        else:
            self.data = create_json_data(
                schedules.json(), coop_schedules.json(), merchandises.json()
            )
            logging.info("Retrieved data successfully.")


class SplatnetEmbeds:
    """Class handling embed generation for the module."""

    asset_db = create_engine("sqlite:///assets/assets.db")
    metadata = MetaData(asset_db)
    metadata.reflect()
    c = asset_db.connect()

    @staticmethod
    def regular(data):
        """Generate a turf war embed."""
        embed = discord.Embed(
            title=
            f'Current Turf War Rotation: {data["time"]["start"].ctime()} - {data["time"]["end"].ctime()}',
            color=discord.Color.from_rgb(199, 207, 32)
        )
        embed.set_thumbnail(
            url=
            "https://cdn.wikimg.net/en/splatoonwiki/images/4/4c/Mode_Icon_Regular_Battle_2.png"
        )
        embed.add_field(
            name="Map Set:", value=f'{data["maps"][0]}, {data["maps"][1]}'
        )
        embed.add_field(
            name="Time Left:", value=f'{data["time"]["end"] - datetime.now()}'
        )
        return embed

    @staticmethod
    def ranked(data):
        """Generate a ranked battle embed."""
        embed = discord.Embed(
            title=
            f'Current Ranked Battle Rotation: {data["time"]["start"].ctime()} - {data["time"]["end"].ctime()}',
            color=discord.Color.from_rgb(243, 48, 0)
        )
        embed.set_thumbnail(
            url=
            "https://cdn.wikimg.net/en/splatoonwiki/images/2/2c/Mode_Icon_Ranked_Battle_2.png"
        )
        embed.add_field(name="Current Mode:", value=data["mode"])
        embed.add_field(
            name="Map Set:", value=f'{data["maps"][0]}, {data["maps"][1]}'
        )
        embed.add_field(
            name="Time Left:", value=f'{data["time"]["end"] - datetime.now()}'
        )
        return embed

    @staticmethod
    def league(data):
        """Generate a league battle embed."""
        embed = discord.Embed(
            title=
            f'Current League Rotation: {data["time"]["start"].ctime()} - {data["time"]["end"].ctime()}',
            color=discord.Color.from_rgb(234, 0, 107)
        )
        embed.set_thumbnail(
            url=
            "https://cdn.wikimg.net/en/splatoonwiki/images/9/9b/Symbol_LeagueF.png"
        )
        embed.add_field(name="Current Mode:", value=f'{data["mode"]}')
        embed.add_field(
            name="Map Set:", value=f'{data["maps"][0]}, {data["maps"][1]}'
        )
        embed.add_field(
            name="Time Left:", value=f'{data["time"]["end"] - datetime.now()}'
        )
        return embed

    @staticmethod
    def salmon(data):
        """Generate a Salmon Run embed."""
        if datetime.now() > data["time"]["start"]:
            embed = discord.Embed(
                title="ADVERTISEMENT: Grizzco Industries is hiring!",
                color=discord.Color.from_rgb(255, 51, 54)
            )
            embed.set_thumbnail(
                url=
                "https://cdn.wikimg.net/en/splatoonwiki/images/b/bf/S2_Icon_Grizzco.png"
            )
            embed.add_field(
                name="Current Recruitment Drive Time Window:",
                value=
                f'From {data["time"]["start"].ctime()}, to {data["time"]["end"].ctime()}'
            )
            embed.add_field(name="Current Location:", value=f'{data["map"]}')
            embed.add_field(
                name="Available Weapon Pool:",
                value=
                f'{data["weapons"][0]}, {data["weapons"][1]}, {data["weapons"][2]}, and {data["weapons"][3]}'
            )
        else:
            embed = discord.Embed(
                title=f"ADVERTISEMENT: Grizzco Industries will be hiring soon!",
                color=discord.Color.from_rgb(255, 51, 54)
            )
            embed.add_field(
                name="Future Recruitment Drive Time Window:",
                value=
                f'From {data["time"]["start"].ctime()}, to {data["time"]["end"].ctime()}'
            )
            embed.add_field(name="Future Location:", value=f'{data["map"]}')
            embed.add_field(
                name="Available Weapon Pool:",
                value=
                f'{data["weapons"][0]}, {data["weapons"][1]}, {data["weapons"][2]}, and {data["weapons"][3]}'
            )
        return embed

    @classmethod
    def splatnet(cls, item):
        """Generate a Splatnet feed embed."""
        if item["type"] == "shoes":
            file = cls.c.execute(
                select([cls.metadata.tables["shoes"].c.image])\
                    .where(cls.metadata.tables["shoes"].c.splatnet == item["splatnet"])
            ).fetchone()
            file = discord.File(file["image"], filename=file["image"][17:])
        elif item["type"] == "clothes":
            file = cls.c.execute(
                select([cls.metadata.tables["clothing"].c.image])\
                    .where(cls.metadata.tables["clothing"].c.splatnet == item["splatnet"])
            ).fetchone()
            file = discord.File(file["image"], filename=file["image"][20:])
        elif item["type"] == "head":
            file = cls.c.execute(
                select([cls.metadata.tables["headgear"].c.image])\
                    .where(cls.metadata.tables["headgear"].c.splatnet == item["splatnet"])
            ).fetchone()
            file = discord.File(file["image"], filename=file["image"][20:])
        embed = discord.Embed(
            title=f"SplatNet Gear: {item['name']}",
            color=discord.Color.from_rgb(85, 0, 253)
        )
        embed.add_field(name="Gear Type:", value=item["type"].capitalize())
        embed.add_field(name="Gear Price:", value=item["price"])
        embed.add_field(name="Gear Rarity:", value=item["rarity"])
        embed.add_field(
            name="Gear Ability:",
            value=f"~~{item['original_ability']}~~ {item['ability']}"
        )
        embed.add_field(name="Available Until:", value=item["expiration"])
        return embed, file


def create_json_data(schedules, coop_schedules, merchandises):
    """Turn Splatoon2.ink json data into something more usable for the bot."""
    i = 0
    for weapon in coop_schedules["details"][0]["weapons"]:
        if weapon["id"] == '-1':
            coop_schedules["details"][0]["weapons"][i] = {"weapon":{"name":"*a mystery weapon!*"}}
        i += 1

    data = {
        "regular": {
            "mode":
            "Turf War",
            "maps": [
                schedules["regular"][0]['stage_a']['name'],
                schedules["regular"][0]['stage_b']['name']
            ],
            "time": {
                "start":
                datetime.fromtimestamp(schedules["regular"][0]["start_time"]),
                "end":
                datetime.fromtimestamp(schedules["regular"][0]["end_time"])
            }
        },
        "ranked": {
            "mode":
            schedules["gachi"][0]["rule"]["name"],
            "maps": [
                schedules["gachi"][0]['stage_a']['name'],
                schedules["gachi"][0]['stage_b']['name']
            ],
            "time": {
                "start":
                datetime.fromtimestamp(schedules["gachi"][0]["start_time"]),
                "end":
                datetime.fromtimestamp(schedules["gachi"][0]["end_time"]),
            }
        },
        "league": {
            "mode":
            schedules["league"][0]["rule"]["name"],
            "maps": [
                schedules["league"][0]['stage_a']['name'],
                schedules["league"][0]['stage_b']['name']
            ],
            "time": {
                "start":
                datetime.fromtimestamp(schedules["league"][0]["start_time"]),
                "end":
                datetime.fromtimestamp(schedules["league"][0]["end_time"]),
            }
        },
        "grizzco": {
            "mode":
            "Salmon Run",
            "map":
            coop_schedules["details"][0]["stage"]["name"],
            "weapons": [
                coop_schedules["details"][0]["weapons"][0]["weapon"]["name"],
                coop_schedules["details"][0]["weapons"][1]["weapon"]["name"],
                coop_schedules["details"][0]["weapons"][2]["weapon"]["name"],
                coop_schedules["details"][0]["weapons"][3]["weapon"]["name"]
            ],
            "time": {
                "start":
                datetime.fromtimestamp(
                    coop_schedules["details"][0]["start_time"]
                ),
                "end":
                datetime.fromtimestamp(
                    coop_schedules["details"][0]["end_time"]
                ),
            }
        },
        "splatnet": [
            {
                "name": gear["gear"]["name"],
                "type": gear["kind"],
                "price": gear["price"],
                "rarity": gear["gear"]["rarity"],
                "ability": gear["skill"]["name"],
                "original_ability": gear["original_gear"]["skill"]["name"],
                "expiration": datetime.fromtimestamp(gear["end_time"]).ctime(),
                "splatnet": gear["gear"]["id"]
            } for gear in merchandises["merchandises"]
        ]
    }
    return data


def setup(client):
    """Add the module to the bot."""
    client.add_cog(Splatnet(client))
    logging.info("Splatnet Module Online.")
