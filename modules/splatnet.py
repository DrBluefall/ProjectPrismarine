import logging
import requests
import asyncio
import json
import discord
from datetime import datetime
from discord.ext import commands
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, select

def setup(client):
    """Add the module to the bot."""
    client.add_cog(Splatnet(client))
    logging.info("%s Module Online.", Splatnet.__name__)

class Splatnet(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.group(case_insensitive=True)
    async def splatnet(self, ctx):
        if ctx.invoked_suncommand:
            return
        async with self.client.typing():
            schedule = requests.get("https://splatoon2.ink/data/schedules.json").json()

            grizzco_schedule = requests.get("https://splatoon2.ink/data/coop-schedules.json").json()

            splatnet = requests.get("https://splatoon2.ink/data/merchandises.json").json()

            turf_map_1 = schedule["regular"][0]['stage_a']['name']
            turf_map_2 = schedule["regular"][0]['stage_b']['name']
            turf_start = datetime.fromtimestamp(schedule["regular"][0]["start_time"]).ctime()
            turf_end = datetime.fromtimestamp(schedule["regular"][0]["end_time"]).ctime()
            ranked_mode = schedule["gachi"][0]["rule"]["name"]
            ranked_map_1 = schedule["gachi"][0]['stage_a']['name']
            ranked_map_2 = schedule["gachi"][0]['stage_b']['name']
            ranked_start = datetime.fromtimestamp(schedule["gachi"][0]["start_time"]).ctime()
            ranked_end = datetime.fromtimestamp(schedule["gachi"][0]["end_time"]).ctime()
            league_mode = schedule["league"][0]["rule"]["name"]
            league_map_1 = schedule["league"][0]['stage_a']['name']
            league_map_2 = schedule["league"][0]['stage_b']['name']
            league_start = datetime.fromtimestamp(schedule["league"][0]["start_time"]).ctime()
            league_end = datetime.fromtimestamp(schedule["league"][0]["end_time"]).ctime()
            grizzco_map = grizzco_schedule["details"][0]["stage"]["name"]
            grizzco_wep_1 = grizzco_schedule["details"][0]["weapons"][0]["weapon"]["name"]
            grizzco_wep_2 = grizzco_schedule["details"][0]["weapons"][1]["weapon"]["name"]
            grizzco_wep_3 = grizzco_schedule["details"][0]["weapons"][2]["weapon"]["name"]
            grizzco_wep_4 = grizzco_schedule["details"][0]["weapons"][3]["weapon"]["name"]
            grizzco_start = datetime.fromtimestamp(grizzco_schedule["details"][0]["start_time"]).ctime()
            grizzco_end = datetime.fromtimestamp(grizzco_schedule["details"][0]["end_time"]).ctime()

            turf_embed = discord.Embed(
                title=f"Current Turf War Rotation: {turf_start} - {turf_end}",
                color=discord.Color.from_rgb(199, 207, 32)
            )
            turf_embed.add_field(name="Maps:", value=f"{turf_map_1}, {turf_map_2}")
            turf_embed.set_thumbnail("http://images6.fanpop.com/image/photos/40200000/Turf-Wars-Icon-splatoon-40239614-420-460.png")
