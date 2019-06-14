"""Module storing all weapons from Splatoon 2."""
import os
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String


class Weapons:
    """Class containing all the weapons of Splatoon 2."""

    engine = create_engine("sqlite:///ProjectPrismarine.db")
    metadata = MetaData(engine)

    weapons = Table(
        "weapons",
        metadata,
        Column("id", Integer),
        Column("set", Integer),
        Column("weapon_id", String),
        Column("weapon_name", String),
        Column("weapon_image", String),
        Column("sub", String),
        Column("special", String),
        Column("special_cost", Integer),
        Column("level", Integer),
        Column("price", Integer),
    )

    metadata.create_all()
    c = engine.connect()

    asset_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets/main_weapons")

    @staticmethod
    def __init__():
        """Initilize Weapons class."""
        ins_0 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name="Sploosh-o-matic",
            weapon_image="S2_Weapon_Main_Sploosh-o-matic.png",  # [10:]
            sub="Curling Bomb",
            special="Splashdown",
            special_cost=160,
            level=10,
            price=9700,
        )
