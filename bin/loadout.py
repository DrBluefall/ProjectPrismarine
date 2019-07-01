"""Script to make dealing with loadouts in cogs easier."""
from sqlalchemy import create_engine, MetaData, select, and_
from PIL import Image
from . import decoder


class Loadout:
    """Module containing all loadout-related functionality of the bot."""

    def __init__(self):
        """Initialize the class."""
        self.dbs = {
            "assets": {
                "db": create_engine("sqlite:///assets/assets.db"),
                "meta": MetaData(),
            },
            "main": {
                "db": create_engine("sqlite:///main.db"),
                "meta": MetaData()
            },
        }
        self.dbs["assets"]["meta"].reflect(self.dbs["assets"]["db"])
        self.dbs["main"]["meta"].reflect(self.dbs["main"]["db"])

        self.dbs["assets"]["connect"] = self.dbs["assets"]["db"].connect()
        self.dbs["main"]["connect"] = self.dbs["main"]["db"].connect()

    def get_row(self, table, id, weapon_id=None):
        """Return row in database given table and the id."""
        asset_c = self.dbs["assets"]["connect"]
        if weapon_id is None:
            return asset_c.execute(
                select(
                    [self.dbs["assets"]["meta"].tables[table]]
                ).where(self.dbs["assets"]["meta"].tables[table].c.id == id)
            ).fetchone()

        return asset_c.execute(
            select([self.dbs["assets"]["meta"].tables[table]]).where(
                and_(
                    self.dbs["assets"]["meta"].tables[table].c.class_id == id,
                    self.dbs["assets"]["meta"].tables[table].c.loadout_ink_id
                    == weapon_id,
                )
            )
        ).fetchone()

    def convert_loadout(self, raw_loadout):
        """Convert and return the raw_loadout to a database queried loadout, using a beautiful dictionary comprehension."""
        weapon_value = {
            "main": self.get_row(
                "weapons", raw_loadout["class"], raw_loadout["weapon"]
            ),
            "sub": self.dbs["assets"]["connect"].\
                execute(
                    select([self.dbs["assets"]["meta"].tables["subs"]]).\
                    where(self.dbs["assets"]["meta"].tables["subs"].c.name == self.get_row("weapons", raw_loadout["class"], raw_loadout["weapon"])["sub"])
                ).fetchone(),
            "special": self.dbs["assets"]["connect"].\
                execute(
                    select([self.dbs["assets"]["meta"].tables["specials"]]).\
                    where(self.dbs["assets"]["meta"].tables["specials"].c.name == self.get_row("weapons", raw_loadout["class"], raw_loadout["weapon"])["special"])
                ).fetchone(),
        }

        loadout = {
            key: (
                {
                    v_key: (
                        self.get_row(key, v_value) if key != "subs" else [
                            self.get_row("abilities", s_value)
                            for s_value in v_value
                        ]
                    )
                    for v_key, v_value in value
                } if key != "weapon" else weapon_value
            )
            for key, value in raw_loadout.items()
        }

        return loadout

    def generate_loadout_image(self, loadout):
        """Generate an image from provided loadout data."""
        image = Image.open("assets/img/loadout_template.png")

        # Head
        try:
            image.paste(
                Image.open(loadout["headgear"]["main"]["image"]
                           ).convert("RGBA").resize((32, 32), Image.ANTIALIAS),
                box=(154, 117),
                mask=Image.open(
                    loadout["headgear"]["main"]["image"]
                ).convert("RGBA").resize((32, 32), Image.ANTIALIAS),
            )
        except TypeError:
            image.paste(
                Image.open("assets/img/abilities/Unknown.png"
                           ).convert("RGBA").resize((32, 32), Image.ANTIALIAS),
                box=(154, 117),
                mask=Image.open("assets/img/abilities/Unknown.png").
                convert("RGBA").resize((32, 32), Image.ANTIALIAS),
            )
        try:
            image.paste(
                Image.open(loadout["headgear"]["subs"][0]["image"]
                           ).convert("RGBA").resize((24, 24), Image.ANTIALIAS),
                box=(190, 126),
                mask=Image.open(
                    loadout["headgear"]["subs"][0]["image"]
                ).convert("RGBA").resize((24, 24), Image.ANTIALIAS),
            )
        except TypeError:
            image.paste(
                Image.open("assets/img/abilities/Unknown.png"
                           ).convert("RGBA").resize((24, 24), Image.ANTIALIAS),
                box=(190, 126),
                mask=Image.open("assets/img/abilities/Unknown.png").
                convert("RGBA").resize((24, 24), Image.ANTIALIAS),
            )
        try:
            image.paste(
                Image.open(loadout["headgear"]["subs"][1]["image"]
                           ).convert("RGBA").resize((24, 24), Image.ANTIALIAS),
                box=(219, 126),
                mask=Image.open(
                    loadout["headgear"]["subs"][1]["image"]
                ).convert("RGBA").resize((24, 24), Image.ANTIALIAS),
            )
        except TypeError:
            image.paste(
                Image.open("assets/img/abilities/Unknown.png"
                           ).convert("RGBA").resize((24, 24), Image.ANTIALIAS),
                box=(219, 126),
                mask=Image.open("assets/img/abilities/Unknown.png").
                convert("RGBA").resize((24, 24), Image.ANTIALIAS),
            )
        try:
            image.paste(
                Image.open(loadout["headgear"]["subs"][2]["image"]
                           ).convert("RGBA").resize((24, 24), Image.ANTIALIAS),
                box=(247, 126),
                mask=Image.open(
                    loadout["headgear"]["subs"][2]["image"]
                ).convert("RGBA").resize((24, 24), Image.ANTIALIAS),
            )
        except TypeError:
            image.paste(
                Image.open("assets/img/abilities/Unknown.png"
                           ).convert("RGBA").resize((24, 24), Image.ANTIALIAS),
                box=(247, 126),
                mask=Image.open("assets/img/abilities/Unknown.png").
                convert("RGBA").resize((24, 24), Image.ANTIALIAS),
            )
        image.paste(
            Image.open(loadout["headgear"]["gear"]["image"]
                       ).convert("RGBA").resize((90, 90), Image.ANTIALIAS),
            box=(170, 29),
            mask=Image.open(
                loadout["headgear"]["gear"]["image"]
            ).convert("RGBA").resize((90, 90), Image.ANTIALIAS),
        )

        # Shirt
        try:
            image.paste(
                Image.open(loadout["clothing"]["main"]["image"]
                           ).convert("RGBA").resize((32, 32), Image.ANTIALIAS),
                box=(299, 117),
                mask=Image.open(
                    loadout["clothing"]["main"]["image"]
                ).convert("RGBA").resize((32, 32), Image.ANTIALIAS),
            )
        except TypeError:
            image.paste(
                Image.open("assets/img/abilities/Unknown.png"
                           ).convert("RGBA").resize((32, 32), Image.ANTIALIAS),
                box=(299, 117),
                mask=Image.open("assets/img/abilities/Unknown.png").
                convert("RGBA").resize((32, 32), Image.ANTIALIAS),
            )
        try:
            image.paste(
                Image.open(loadout["clothing"]["subs"][0]["image"]
                           ).convert("RGBA").resize((24, 24), Image.ANTIALIAS),
                box=(335, 126),
                mask=Image.open(
                    loadout["clothing"]["subs"][0]["image"]
                ).convert("RGBA").resize((24, 24), Image.ANTIALIAS),
            )
        except TypeError:
            image.paste(
                Image.open("assets/img/abilities/Unknown.png"
                           ).convert("RGBA").resize((24, 24), Image.ANTIALIAS),
                box=(335, 126),
                mask=Image.open("assets/img/abilities/Unknown.png").
                convert("RGBA").resize((24, 24), Image.ANTIALIAS),
            )
        try:
            image.paste(
                Image.open(loadout["clothing"]["subs"][1]["image"]
                           ).convert("RGBA").resize((24, 24), Image.ANTIALIAS),
                box=(364, 126),
                mask=Image.open(
                    loadout["clothing"]["subs"][1]["image"]
                ).convert("RGBA").resize((24, 24), Image.ANTIALIAS),
            )
        except TypeError:
            image.paste(
                Image.open("assets/img/abilities/Unknown.png"
                           ).convert("RGBA").resize((24, 24), Image.ANTIALIAS),
                box=(364, 126),
                mask=Image.open("assets/img/abilities/Unknown.png").
                convert("RGBA").resize((24, 24), Image.ANTIALIAS),
            )
        try:
            image.paste(
                Image.open(loadout["clothing"]["subs"][2]["image"]
                           ).convert("RGBA").resize((24, 24), Image.ANTIALIAS),
                box=(392, 126),
                mask=Image.open(
                    loadout["clothing"]["subs"][2]["image"]
                ).convert("RGBA").resize((24, 24), Image.ANTIALIAS),
            )
        except TypeError:
            image.paste(
                Image.open("assets/img/abilities/Unknown.png"
                           ).convert("RGBA").resize((24, 24), Image.ANTIALIAS),
                box=(392, 126),
                mask=Image.open("assets/img/abilities/Unknown.png").
                convert("RGBA").resize((24, 24), Image.ANTIALIAS),
            )
        image.paste(
            Image.open(loadout["clothing"]["gear"]["image"]
                       ).convert("RGBA").resize((90, 90), Image.ANTIALIAS),
            box=(315, 29),
            mask=Image.open(
                loadout["clothing"]["gear"]["image"]
            ).convert("RGBA").resize((90, 90), Image.ANTIALIAS),
        )

        # Shoes
        try:
            image.paste(
                Image.open(loadout["shoes"]["main"]["image"]
                           ).convert("RGBA").resize((32, 32), Image.ANTIALIAS),
                box=(444, 117),
                mask=Image.open(
                    loadout["shoes"]["main"]["image"]
                ).convert("RGBA").resize((32, 32), Image.ANTIALIAS),
            )
        except TypeError:
            image.paste(
                Image.open("assets/img/abilities/Unknown.png"
                           ).convert("RGBA").resize((32, 32), Image.ANTIALIAS),
                box=(444, 117),
                mask=Image.open("assets/img/abilities/Unknown.png").
                convert("RGBA").resize((32, 32), Image.ANTIALIAS),
            )
        try:
            image.paste(
                Image.open(loadout["shoes"]["subs"][0]["image"]
                           ).convert("RGBA").resize((24, 24), Image.ANTIALIAS),
                box=(480, 126),
                mask=Image.open(
                    loadout["shoes"]["subs"][0]["image"]
                ).convert("RGBA").resize((24, 24), Image.ANTIALIAS),
            )
        except TypeError:
            image.paste(
                Image.open("assets/img/abilities/Unknown.png"
                           ).convert("RGBA").resize((24, 24), Image.ANTIALIAS),
                box=(480, 126),
                mask=Image.open("assets/img/abilities/Unknown.png").
                convert("RGBA").resize((24, 24), Image.ANTIALIAS),
            )
        try:
            image.paste(
                Image.open(loadout["shoes"]["subs"][1]["image"]
                           ).convert("RGBA").resize((24, 24), Image.ANTIALIAS),
                box=(508, 126),
                mask=Image.open(
                    loadout["shoes"]["subs"][1]["image"]
                ).convert("RGBA").resize((24, 24), Image.ANTIALIAS),
            )
        except TypeError:
            image.paste(
                Image.open("assets/img/abilities/Unknown.png"
                           ).convert("RGBA").resize((24, 24), Image.ANTIALIAS),
                box=(508, 126),
                mask=Image.open("assets/img/abilities/Unknown.png").
                convert("RGBA").resize((24, 24), Image.ANTIALIAS),
            )
        try:
            image.paste(
                Image.open(loadout["shoes"]["subs"][2]["image"]
                           ).convert("RGBA").resize((24, 24), Image.ANTIALIAS),
                box=(537, 126),
                mask=Image.open(
                    loadout["shoes"]["subs"][2]["image"]
                ).convert("RGBA").resize((24, 24), Image.ANTIALIAS),
            )
        except TypeError:
            image.paste(
                Image.open("assets/img/abilities/Unknown.png"
                           ).convert("RGBA").resize((24, 24), Image.ANTIALIAS),
                box=(537, 126),
                mask=Image.open("assets/img/abilities/Unknown.png").
                convert("RGBA").resize((24, 24), Image.ANTIALIAS),
            )
        image.paste(
            Image.open(loadout["shoes"]["gear"]["image"]
                       ).convert("RGBA").resize((90, 90), Image.ANTIALIAS),
            box=(460, 29),
            mask=Image.open(
                loadout["shoes"]["gear"]["image"]
            ).convert("RGBA").resize((90, 90), Image.ANTIALIAS),
        )

        # Weapon
        image.paste(
            Image.open(loadout["weapon"]["sub"]["image"]
                       ).convert("RGBA").resize((32, 32), Image.ANTIALIAS),
            box=(28, 117),
            mask=Image.open(
                loadout["weapon"]["sub"]["image"]
            ).convert("RGBA").resize((32, 32), Image.ANTIALIAS),
        )
        image.paste(
            Image.open(loadout["weapon"]["special"]["image"]
                       ).convert("RGBA").resize((32, 32), Image.ANTIALIAS),
            box=(78, 117),
            mask=Image.open(
                loadout["weapon"]["special"]["image"]
            ).convert("RGBA").resize((32, 32), Image.ANTIALIAS),
        )
        image.paste(
            Image.open(loadout["weapon"]["main"]["image"]
                       ).convert("RGBA").resize((90, 90), Image.ANTIALIAS),
            box=(23, 29),
            mask=Image.open(
                loadout["weapon"]["main"]["image"]
            ).convert("RGBA").resize((90, 90), Image.ANTIALIAS),
        )

        return image


def main():
    """Generate loadout image."""
    Loadout().generate_loadout_image(
        Loadout().convert_loadout(decoder.decode("0007004a529004a4000000000"))
    )  # pylint: disable=no-member


if __name__ == "__main__":
    main()
