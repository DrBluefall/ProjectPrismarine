"""Module storing all weapons from Splatoon 2."""
import os
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, select


class Weapons():
    """Class containing all the weapons of Splatoon 2."""

    engine = create_engine("sqlite:///ProjectPrismarine.db")
    metadata = MetaData(engine)
    weapons = Table(
        "weapons",
        metadata,
        Column('id', Integer),
        Column('set', Integer),
        Column('weapon_id', String),
        Column('weapon_name', String),
        Column('weapon_image', String),
        Column('sub', String),
        Column('special', String),
        Column('special_cost', Integer),
        Column('level', Integer),
        Column('price', Integer)
    )

    metadata.create_all()
    c = engine.connect()

    asset_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets/main_weapons")

    @staticmethod
    def __init__():
        ins_0 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost=160,
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=1,
            weapon_name='Neo Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Neo_Sploosh-o-matic.png',
            sub='Squid Beakon',
            special='Tenta Missiles',
            special_cost=170,
            level=18,
            price=12200
        )
        ins_2 = __class__.weapons.insert(None).values(
            set=0,
            id=2,
            weapon_name='Sploosh-o-matic 7',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic_7.png',
            sub='Splat Bomb',
            special='Ultra Stamp',
            special_cost=180,
            level=23,
            price=14600
        )
        ins_3 = __class__.weapons.insert(None).values(
            set=0,
            id=3,
            weapon_name='Splattershot Jr.',
            weapon_image='S2_Weapon_Main_Splattershot_Jr..png',
            sub='Splat Bomb',
            special='Ink Armor',
            special_cost=180,
            level=1,
            price=0
        )
        ins_4 = __class__.weapons.insert(None).values(
            set=0,
            id=4,
            weapon_name='Custom Splattershot Jr.',
            weapon_image='S2_Weapon_Main_Custom_Splattershot_Jr..png',
            sub='Autobomb',
            special='Ink Storm',
            special_cost=160,
            level=4,
            price=1900
        )
        ins_5 = __class__.weapons.insert(None).values(
            set=0,
            id=5,
            weapon_name='Kensa Splattershot Jr.',
            weapon_image='S2_Weapon_Main_Kensa_Splattershot_Jr..png',
            sub='Torpedo',
            special='Bubble Blower',
            special_cost=200,
            level=9,
            price=8700
        )
        ins_6 = __class__.weapons.insert(None).values(
            set=0,
            id=6,
            weapon_name='Splash-o-matic',
            weapon_image='S2_Weapon_Main_Splash-o-matic.png',
            sub='Toxic Mist',
            special='Inkjet',
            special_cost=170,
            level=25,
            price=11200
        )
        ins_7 = __class__.weapons.insert(None).values(
            set=0,
            id=7,
            weapon_name='Neo Splash-o-matic',
            weapon_image='S2_Weapon_Main_Neo_Splash-o-matic.png',
            sub='Burst Bomb',
            special='Suction-Bomb Launcher',
            special_cost=210,
            level=27,
            price=16800
        )
        ins_8 = __class__.weapons.insert(None).values(
            set=0,
            id=8,
            weapon_name='Aerospray MG',
            weapon_image='S2_Weapon_Main_Aerospray_MG.png',
            sub='Suction Bomb',
            special='Curling-Bomb Launcher',
            special_cost=160,
            level=6,
            price=4900
        )
        ins_9 = __class__.weapons.insert(None).values(
            set=0,
            id=9,
            weapon_name='Aerospray RG',
            weapon_image='S2_Weapon_Main_Aerospray_RG.png',
            sub='Sprinkler',
            special='Baller',
            special_cost=180,
            level=28,
            price=16900
        )
        ins_10 = __class__.weapons.insert(None).values(
            set=0,
            id=10,
            weapon_name='Aerospray PG',
            weapon_image='S2_Weapon_Main_Aerospray_PG.png',
            sub='Burst Bomb',
            special='Booyah Bomb',
            special_cost=190,
            level=29,
            price=19000
        )
        ins_11 = __class__.weapons.insert(None).values(
            set=0,
            id=11,
            weapon_name='Splattershot',
            weapon_image='S2_Weapon_Main_Splattershot.png',
            sub='Burst Bomb',
            special='Splashdown',
            special_cost=180,
            level=2,
            price=900
        )
        ins_12 = __class__.weapons.insert(None).values(
            set=0,
            id=12,
            weapon_name='Tentatek Splattershot',
            weapon_image='S2_Weapon_Main_Tentatek_Splattershot.png',
            sub='Splat Bomb',
            special='Inkjet',
            special_cost=210,
            level=4,
            price=2100
        )
        ins_13 = __class__.weapons.insert(None).values(
            set=0,
            id=13,
            weapon_name='Kensa Splattershot',
            weapon_image='S2_Weapon_Main_Kensa_Splattershot.png',
            sub='Suction Bomb',
            special='Tenta Missiles',
            special_cost=180,
            level=6,
            price=5300
        )
        ins_14 = __class__.weapons.insert(None).values(
            set=0,
            id=14,
            weapon_name='Hero Shot Replica',
            weapon_image='S2_Weapon_Main_Hero_Shot_Replica.png',
            sub='Burst Bomb',
            special='Splashdown',
            special_cost='180',
            level=2,
            price=1500
        )
        ins_15 = __class__.weapons.insert(None).values(
            set=0,
            id=15,
            weapon_name='Octo Shot Replica',
            weapon_image='S2_Weapon_Main_Octo_Shot_Replica.png',
            sub='Splat Bomb',
            special='Inkjet',
            special_cost=210,
            level=1,
            price=0
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )
        ins_1 = __class__.weapons.insert(None).values(
            set=0,
            id=0,
            weapon_name='Sploosh-o-matic',
            weapon_image='S2_Weapon_Main_Sploosh-o-matic.png',
            sub='Curling Bomb',
            special='Splashdown',
            special_cost='160',
            level=10,
            price=9700
        )