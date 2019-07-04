"""Script to make dealing with loadouts in cogs easier."""
from sqlalchemy import select, and_
from PIL import Image
from core import DBHandler
from bin.decoder import decode


class Loadout(DBHandler):
    """Module containing all loadout-related functionality of the bot."""

    def generate_loadout_image(self, loadout):
        """Generate an image from provided loadout data."""
        image = Image.open("assets/img/loadout_template.png")

        image = self.generate_headgear(image, loadout)
        image = self.generate_clothing(image, loadout)
        image = self.generate_shoes(image, loadout)
        image = self.generate_weapon(image, loadout)

        return image

    def convert_loadout(self, raw_loadout):
        """Convert and return the raw_loadout to a database queried loadout, using a beautiful dictionary comprehension."""
        weapon_value = {
            "main": self.get_row(
                "weapons", raw_loadout["class"], raw_loadout["weapon"]
            ),
            "sub": self.get_db("assets"). \
                execute(
                    select([self.get_meta("assets").tables["subs"]]). \
                    where(self.get_meta("assets").tables["subs"].columns["name"] == self.get_row("weapons", raw_loadout["class"], raw_loadout["weapon"])["sub"])
                ).fetchone(),
            "special": self.get_db("assets"). \
                execute(
                    select([self.get_meta("assets").tables["specials"]]). \
                    where(self.get_meta("assets").tables["specials"].columns["name"] == self.get_row("weapons", raw_loadout["class"], raw_loadout["weapon"])["special"])
                ).fetchone(),
        }

        loadout = {
            key: (
                {
                    v_key: (
                        (self.get_row(key, v_value) if v_key == "gear" else self.get_row("abilities", v_value))
                        if v_key != "subs"
                        else [self.get_row("abilities", s_value) for s_value in v_value]
                    )
                    for v_key, v_value in value.items()
                }
                if key not in ("weapon", "class")
                else (weapon_value if key == "weapon" else None)
            )
            for key, value in raw_loadout.items()
        }  # yapf: disable

        return loadout

    @staticmethod
    def generate_headgear(image, loadout):
        """Help method to generate the headgear part of the image."""
        try:
            path = loadout["headgear"]["main"]["image"]
        except TypeError:
            path = "assets/img/abilities/Unknown.png"
        finally:
            image.paste(
                Image.open(path).convert("RGBA").resize(
                    (32, 32), Image.ANTIALIAS
                ),
                box=(154, 117),
                mask=Image.open(path).convert("RGBA").resize(
                    (32, 32), Image.ANTIALIAS
                ),
            )

        try:
            path = loadout["headgear"]["subs"][0]["image"]
        except TypeError:
            path = "assets/img/abilities/Unknown.png"
        finally:
            image.paste(
                Image.open(path).convert("RGBA").resize(
                    (24, 24), Image.ANTIALIAS
                ),
                box=(190, 126),
                mask=Image.open(path).convert("RGBA").resize(
                    (24, 24), Image.ANTIALIAS
                ),
            )

        try:
            path = loadout["headgear"]["subs"][1]["image"]
        except TypeError:
            path = "assets/img/abilities/Unknown.png"
        finally:
            image.paste(
                Image.open(path).convert("RGBA").resize(
                    (24, 24), Image.ANTIALIAS
                ),
                box=(219, 126),
                mask=Image.open(path).convert("RGBA").resize(
                    (24, 24), Image.ANTIALIAS
                ),
            )

        try:
            path = loadout["headgear"]["subs"][2]["image"]
        except TypeError:
            path = "assets/img/abilities/Unknown.png"
        finally:
            image.paste(
                Image.open(path).convert("RGBA").resize(
                    (24, 24), Image.ANTIALIAS
                ),
                box=(247, 126),
                mask=Image.open(path).convert("RGBA").resize(
                    (24, 24), Image.ANTIALIAS
                ),
            )

        path = loadout["headgear"]["gear"]["image"]
        image.paste(
            Image.open(path).convert("RGBA").resize((90, 90), Image.ANTIALIAS),
            box=(170, 29),
            mask=Image.open(path).convert("RGBA").resize(
                (90, 90), Image.ANTIALIAS
            ),
        )
        return image

    @staticmethod
    def generate_clothing(image, loadout):
        """Help method to generate the clothing part of the image."""
        try:
            path = loadout["clothing"]["main"]["image"]
        except TypeError:
            path = "assets/img/abilities/Unknown.png"
        finally:
            image.paste(
                Image.open(path).convert("RGBA").resize(
                    (32, 32), Image.ANTIALIAS
                ),
                box=(299, 117),
                mask=Image.open(path).convert("RGBA").resize(
                    (32, 32), Image.ANTIALIAS
                ),
            )
        try:
            path = loadout["clothing"]["subs"][0]["image"]
        except TypeError:
            path = "assets/img/abilities/Unknown.png"
        finally:
            image.paste(
                Image.open(path).convert("RGBA").resize(
                    (24, 24), Image.ANTIALIAS
                ),
                box=(335, 126),
                mask=Image.open(path).convert("RGBA").resize(
                    (24, 24), Image.ANTIALIAS
                ),
            )
        try:
            path = loadout["clothing"]["subs"][1]["image"]
        except TypeError:
            path = "assets/img/abilities/Unknown.png"
        finally:
            image.paste(
                Image.open(path).convert("RGBA").resize(
                    (24, 24), Image.ANTIALIAS
                ),
                box=(364, 126),
                mask=Image.open(path).convert("RGBA").resize(
                    (24, 24), Image.ANTIALIAS
                ),
            )
        try:
            path = loadout["clothing"]["subs"][2]["image"]
        except TypeError:
            path = "assets/img/abilities/Unknown.png"
        finally:
            image.paste(
                Image.open(path).convert("RGBA").resize(
                    (24, 24), Image.ANTIALIAS
                ),
                box=(392, 126),
                mask=Image.open(path).convert("RGBA").resize(
                    (24, 24), Image.ANTIALIAS
                ),
            )

        path = loadout["clothing"]["gear"]["image"]
        image.paste(
            Image.open(path).convert("RGBA").resize((90, 90), Image.ANTIALIAS),
            box=(315, 29),
            mask=Image.open(path).convert("RGBA").resize(
                (90, 90), Image.ANTIALIAS
            ),
        )
        return image

    @staticmethod
    def generate_shoes(image, loadout):
        """Help method to generate the shoes part of the image."""
        try:
            path = loadout["shoes"]["main"]["image"]
        except TypeError:
            path = "assets/img/abilities/Unknown.png"
        finally:
            image.paste(
                Image.open(path).convert("RGBA").resize(
                    (32, 32), Image.ANTIALIAS
                ),
                box=(444, 117),
                mask=Image.open(path).convert("RGBA").resize(
                    (32, 32), Image.ANTIALIAS
                ),
            )
        try:
            path = loadout["shoes"]["subs"][0]["image"]
        except TypeError:
            path = "assets/img/abilities/Unknown.png"
        finally:
            image.paste(
                Image.open(path).convert("RGBA").resize(
                    (24, 24), Image.ANTIALIAS
                ),
                box=(480, 126),
                mask=Image.open(path).convert("RGBA").resize(
                    (24, 24), Image.ANTIALIAS
                ),
            )
        try:
            path = loadout["shoes"]["subs"][1]["image"]
        except TypeError:
            path = "assets/img/abilities/Unknown.png"
        finally:
            image.paste(
                Image.open(path).convert("RGBA").resize(
                    (24, 24), Image.ANTIALIAS
                ),
                box=(508, 126),
                mask=Image.open(path).convert("RGBA").resize(
                    (24, 24), Image.ANTIALIAS
                ),
            )
        try:
            path = loadout["shoes"]["subs"][2]["image"]
        except TypeError:
            path = "assets/img/abilities/Unknown.png"
        finally:
            image.paste(
                Image.open(path).convert("RGBA").resize(
                    (24, 24), Image.ANTIALIAS
                ),
                box=(537, 126),
                mask=Image.open(path).convert("RGBA").resize(
                    (24, 24), Image.ANTIALIAS
                ),
            )
        path = loadout["shoes"]["gear"]["image"]
        image.paste(
            Image.open(path).convert("RGBA").resize((90, 90), Image.ANTIALIAS),
            box=(460, 29),
            mask=Image.open(path).convert("RGBA").resize(
                (90, 90), Image.ANTIALIAS
            ),
        )
        return image

    @staticmethod
    def generate_weapon(image, loadout):
        """Help method to generate the weapon part of the image."""
        path = loadout["weapon"]["main"]["image"]
        image.paste(
            Image.open(path).convert("RGBA").resize((90, 90), Image.ANTIALIAS),
            box=(23, 29),
            mask=Image.open(path).convert("RGBA").resize(
                (90, 90), Image.ANTIALIAS
            ),
        )
        path = loadout["weapon"]["sub"]["image"]
        image.paste(
            Image.open(path).convert("RGBA").resize((32, 32), Image.ANTIALIAS),
            box=(28, 117),
            mask=Image.open(path).convert("RGBA").resize(
                (32, 32), Image.ANTIALIAS
            ),
        )
        path = loadout["weapon"]["special"]["image"]
        image.paste(
            Image.open(path).convert("RGBA").resize((32, 32), Image.ANTIALIAS),
            box=(78, 117),
            mask=Image.open(path).convert("RGBA").resize(
                (32, 32), Image.ANTIALIAS
            ),
        )
        return image

    def get_row(self, table, loadout_id, weapon_id=None):
        """Return row in database given table and the id."""
        if weapon_id is None:
            return self.get_db("assets").execute(
                select([self.get_meta("assets").tables[table]]). \
                where(self.get_meta("assets").tables[table].columns["id"] == loadout_id)
            ).fetchone()

        return self.get_db("assets").execute(
            select([self.get_meta("assets").tables[table]]). \
            where(
                and_(
                    self.get_meta("assets").tables[table].columns["class_id"] == loadout_id,
                    self.get_meta("assets").tables[table].columns["loadout_ink_id"] == weapon_id))
        ).fetchone()


def main():
    """Generate loadout image."""
    Loadout().generate_loadout_image(
        Loadout().convert_loadout(decode("0007004a529004a4000000000"))
    )


if __name__ == "__main__":
    main()
