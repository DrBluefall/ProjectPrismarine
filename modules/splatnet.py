"""Module dealing with all SplatNet 2-related functions."""
import logging
import time
import asyncio
import json
from datetime import datetime, timedelta
import requests
import discord
from discord.ext import commands, tasks


def setup(client):
    """Add the module to the bot."""
    client.add_cog(Splatnet(client))
    logging.info("%s Module Online.", Splatnet.__name__)


class Splatnet(commands.Cog):
    """Module dealing with all SplatNet 2-related functions."""

    def __init__(self, client):
        """Initalize the class."""
        self.client = client
        self.data_retrieval.start()
        self.data = create_json_data(
            requests.get("https://splatoon2.ink/data/schedules.json",
                         headers={
                             'User-Agent': 'Project Prismarine#6634'
                         }).json(),
            requests.get("https://splatoon2.ink/data/coop-schedules.json",
                         headers={
                             'User-Agent': 'Project Prismarine#6634'
                         }).json())

    @tasks.loop(minutes=30)
    async def data_retrieval(self):
        """Retrieve and cache info from Splatoon2.ink."""
        await self.client.wait_until_ready()
        while True:
            await asyncio.sleep(60)
            if datetime.now().minute == 1:
                logging.info("Retrieving data from Splatoon2.ink...")
                schedule = requests.get(
                    "https://splatoon2.ink/data/schedules.json",
                    headers={'User-Agent': 'Project Prismarine#6634'})

                grizzco_schedule = requests.get(
                    "https://splatoon2.ink/data/coop-schedules.json",
                    headers={'User-Agent': 'Project Prismarine#6634'})

                # splatnet = requests.get(
                #     "https://splatoon2.ink/data/merchandises.json").json()
                schedule.raise_for_status()
                grizzco_schedule.raise_for_status()

                self.data = create_json_data(schedule.json(),
                                             grizzco_schedule.json())
                logging.info("Retrieved data successfully.")

    @commands.group(case_insensitive=True)
    async def rotation(self, ctx):
        """List all the current rotation for all modes, including Salmon Run when it's open."""
        if ctx.invoked_subcommand is not None:
            return

        async with ctx.typing():

            await ctx.send(embed=SplatnetEmbeds.regular(self.data["regular"]))
            await ctx.send(embed=SplatnetEmbeds.ranked(self.data["ranked"]))
            await ctx.send(embed=SplatnetEmbeds.league(self.data["league"]))

            if datetime.now() > self.data["grizzco"]["time"]["start"]:
                await ctx.send(
                    embed=SplatnetEmbeds.salmon(self.data["grizzco"]))

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


class SplatnetEmbeds:
    """Class handling embed generation for the module."""

    @staticmethod
    def regular(data):
        """Generate a turf war embed."""
        embed = discord.Embed(
            title=
            f'Current Turf War Rotation: {data["time"]["start"].ctime()} - {data["time"]["end"].ctime()}',
            color=discord.Color.from_rgb(199, 207, 32))
        embed.set_thumbnail(
            url=
            "https://cdn.wikimg.net/en/splatoonwiki/images/4/4c/Mode_Icon_Regular_Battle_2.png"
        )
        embed.add_field(name="Map Set:",
                        value=f'{data["maps"][0]}, {data["maps"][1]}')
        embed.add_field(name="Time Left:",
                        value=f'{data["time"]["end"] - datetime.now()}')
        return embed

    @staticmethod
    def ranked(data):
        """Generate a ranked battle embed."""
        embed = discord.Embed(
            title=
            f'Current Ranked Battle Rotation: {data["time"]["start"].ctime()} - {data["time"]["end"].ctime()}',
            color=discord.Color.from_rgb(243, 48, 0))
        embed.set_thumbnail(
            url=
            "https://cdn.wikimg.net/en/splatoonwiki/images/2/2c/Mode_Icon_Ranked_Battle_2.png"
        )
        embed.add_field(name="Current Mode:", value=data["mode"])
        embed.add_field(name="Map Set:",
                        value=f'{data["maps"][0]}, {data["maps"][1]}')
        embed.add_field(name="Time Left:",
                        value=f'{data["time"]["end"] - datetime.now()}')
        return embed

    @staticmethod
    def league(data):
        """Generate a league battle embed."""
        embed = discord.Embed(
            title=
            f'Current League Rotation: {data["time"]["start"].ctime()} - {data["time"]["end"].ctime()}',
            color=discord.Color.from_rgb(234, 0, 107))
        embed.set_thumbnail(
            url=
            "https://cdn.wikimg.net/en/splatoonwiki/images/9/9b/Symbol_LeagueF.png"
        )
        embed.add_field(name="Current Mode:", value=f'{data["mode"]}')
        embed.add_field(name="Map Set:",
                        value=f'{data["maps"][0]}, {data["maps"][1]}')
        embed.add_field(name="Time Left:",
                        value=f'{data["time"]["end"] - datetime.now()}')
        return embed

    @staticmethod
    def salmon(data):
        """Generate a Salmon Run embed."""
        if datetime.now() > data["time"]["start"]:
            embed = discord.Embed(
                title="ADVERTISEMENT: Grizzco Industries is hiring!",
                color=discord.Color.from_rgb(255, 51, 54))
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
                color=discord.Color.from_rgb(255, 51, 54))
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


def create_json_data(schedule, grizzco_schedule):
    """Turn Splatoon2.ink json data into something more usable for the bot."""
    data = {
        "regular": {
            "mode":
            "Turf War",
            "maps": [
                schedule["regular"][0]['stage_a']['name'],
                schedule["regular"][0]['stage_b']['name']
            ],
            "time": {
                "start":
                datetime.fromtimestamp(schedule["regular"][0]["start_time"]),
                "end":
                datetime.fromtimestamp(schedule["regular"][0]["end_time"])
            }
        },
        "ranked": {
            "mode":
            schedule["gachi"][0]["rule"]["name"],
            "maps": [
                schedule["gachi"][0]['stage_a']['name'],
                schedule["gachi"][0]['stage_b']['name']
            ],
            "time": {
                "start":
                datetime.fromtimestamp(schedule["gachi"][0]["start_time"]),
                "end":
                datetime.fromtimestamp(schedule["gachi"][0]["end_time"]),
            }
        },
        "league": {
            "mode":
            schedule["league"][0]["rule"]["name"],
            "maps": [
                schedule["league"][0]['stage_a']['name'],
                schedule["league"][0]['stage_b']['name']
            ],
            "time": {
                "start":
                datetime.fromtimestamp(schedule["league"][0]["start_time"]),
                "end":
                datetime.fromtimestamp(schedule["league"][0]["end_time"]),
            }
        },
        "grizzco": {
            "mode":
            "Salmon Run",
            "map":
            grizzco_schedule["details"][0]["stage"]["name"],
            "weapons": [
                grizzco_schedule["details"][0]["weapons"][0]["weapon"]["name"],
                grizzco_schedule["details"][0]["weapons"][1]["weapon"]["name"],
                grizzco_schedule["details"][0]["weapons"][2]["weapon"]["name"],
                grizzco_schedule["details"][0]["weapons"][3]["weapon"]["name"]
            ],
            "time": {
                "start":
                datetime.fromtimestamp(
                    grizzco_schedule["details"][0]["start_time"]),
                "end":
                datetime.fromtimestamp(
                    grizzco_schedule["details"][0]["end_time"]),
            }
        }
    }
    return data

def create_splatnet_json_data(splatnet):
    data = []
    for gear in splatnet["merchandises"]:
        item = {
            "name":gear["gear"]["name"],
            "type":gear["kind"],
            "price":gear["price"],
            "rarity":gear["gear"]["rarity"],
            "ability":gear["skill"]["name"],
            "original_ability":gear["original_gear"]["skill"]["name"],
            "expiration":datetime.fromtimestamp(gear["end_time"]).ctime()
        }
        data.append(item)
