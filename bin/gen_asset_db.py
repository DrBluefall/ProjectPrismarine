# Core Language Imports

import json
import logging

# Third-Party Imports

import pg8000 as pg
import coloredlogs

class AssetDatabase:

    def __init__(self):
        self.asset_db = pg.connect(user='prismarine-core', database='assets')
        self.ac = self.asset_db.cursor()
    
    def regen_tables(self):
        self.ac.execute("""
        DROP TABLE IF EXISTS headgear CASCADE;""")
        self.ac.execute("""
        CREATE TABLE headgear (
            name TEXT,
            image TEXT,
            localized_name JSON,
            main TEXT,
            stars INTEGER,
            id INTEGER,
            splatnet INTEGER PRIMARY KEY
        );""")
        self.ac.execute("""
        DROP TABLE IF EXISTS clothing CASCADE;""")
        self.ac.execute("""
        CREATE TABLE clothing (
            name TEXT,
            image TEXT,
            localized_name JSON,
            main TEXT,
            stars INTEGER,
            id INTEGER,
            splatnet INTEGER PRIMARY KEY
        );""")
        self.ac.execute("""
        DROP TABLE IF EXISTS shoes CASCADE;""")
        self.ac.execute("""
        CREATE TABLE shoes (
            name TEXT,
            image TEXT,
            localized_name JSON,
            main TEXT,
            stars INTEGER,
            id INTEGER,
            splatnet INTEGER PRIMARY KEY
        );""")
        self.ac.execute("""
        DROP TABLE IF EXISTS abilities CASCADE;""")
        self.ac.execute("""
        CREATE TABLE abilities (
            name TEXT,
            localized_name JSON,
            image TEXT,
            id INTEGER PRIMARY KEY
        );""")
        self.ac.execute("""
        DROP TABLE IF EXISTS sub_weapons CASCADE;""")
        self.ac.execute("""
        CREATE TABLE sub_weapons (
            name TEXT PRIMARY KEY,
            localized_name JSON,
            image TEXT
        );""")
        self.ac.execute("""
        DROP TABLE IF EXISTS special_weapons CASCADE;""")
        self.ac.execute("""
        CREATE TABLE special_weapons (
            name TEXT PRIMARY KEY,
            localized_name JSON,
            image TEXT
        );""")
        self.ac.execute("""
        DROP TABLE IF EXISTS main_weapons CASCADE;""")
        self.ac.execute("""
        CREATE TABLE main_weapons (
            id SERIAL PRIMARY KEY,
            name TEXT,
            class INTEGER,
            localized_name JSON,
            sub TEXT REFERENCES sub_weapons(name),
            special TEXT REFERENCES special_weapons(name),
            site_id INTEGER
        );""")
        self.asset_db.commit()
    
    def insert_headgear(self):
        with open("../assets/data/headgear.json", "r") as infile:
            headgear = json.load(infile)
        for head in headgear:
            logging.info(f"Inserting {head['name']}...")
            head["image"] = "../assets/img/gear/hats/" + head["image"][31:]
            self.ac.execute("""
            INSERT INTO headgear(
                name, 
                image,
                localized_name,
                main,
                stars,
                id,
                splatnet
            ) VALUES (%s,%s,%s,%s,%s,%s,%s)
            """, (head["name"], head["image"], json.dumps(head["localizedName"]), head["main"], head["stars"], head["id"], head["splatnet"]))
            self.asset_db.commit()
            logging.info("Inserted '%s' into the database!" % head["name"])
        
    
    def insert_clothing(self):
        with open("../assets/data/clothing.json", "r") as infile:
            gear = json.load(infile)
        for item in gear:
            logging.info(f"Inserting {item['name']}...")
            item["image"] = "../assets/img/gear/clothes/" + item["image"][34:]
            self.ac.execute("""
            INSERT INTO clothing(
                name, 
                image,
                localized_name,
                main,
                stars,
                id,
                splatnet
            ) VALUES (%s,%s,%s,%s,%s,%s,%s)
            """, (item["name"], item["image"], json.dumps(item["localizedName"]), item["main"], item["stars"], item["id"], item["splatnet"]))
            self.asset_db.commit()
            logging.info("Inserted %s into the database!" % item["name"])

    def insert_shoes(self):
        with open("../assets/data/shoes.json", "r") as infile:
            gear = json.load(infile)
        for item in gear:
            logging.info(f"Inserting {item['name']}...")
            item["image"] = "../assets/img/gear/shoes/" + item["image"][32:]
            self.ac.execute("""
            INSERT INTO shoes(
                name, 
                image,
                localized_name,
                main,
                stars,
                id,
                splatnet
            ) VALUES (%s,%s,%s,%s,%s,%s,%s)
            """, (item["name"], item["image"], json.dumps(item["localizedName"]), item["main"], item["stars"], item["id"], item["splatnet"]))
            self.asset_db.commit()
            logging.info("Inserted %s into the database!" % item["name"])

    def insert_abilities(self):
        with open("../assets/data/skills.json", "r") as infile:
            abilities = json.load(infile)
        for ability in abilities:
            ability["image"] = "../assets/img/skills/" + ability["image"][28:]
            logging.info(f"Inserting {ability['name']}...")
            self.ac.execute("""
            INSERT INTO abilities(
                name,
                localized_name,
                image,
                id
            ) VALUES (%s,%s,%s,%s);
            """, (ability["name"], json.dumps(ability["localized_name"]), ability["image"], ability["id"]))
            self.asset_db.commit()
            logging.info("Inserted %s into the database!" % ability["name"])
    
    def insert_specials(self):
        with open("../assets/data/specials.json") as infile:
            specials = json.load(infile)
        for special in specials:
            special["image"] = "../assets/img/subs_specials/" + special["image"][28:]
            logging.info(f"Inserting {special['name']}...")
            self.ac.execute("""
            INSERT INTO special_weapons(
                name,
                localized_name,
                image
            ) VALUES (%s, %s, %s);
            """, (special["name"], json.dumps(["localized_name"]), special["image"]))
            self.asset_db.commit()
            logging.info("Inserted %s into the database!" % special["name"])
    
    def insert_subs(self):
        with open("../assets/data/subs.json") as infile:
            subs = json.load(infile)
        for sub in subs:
            logging.info(f"Inserting {sub['name']}...")
            sub["image"] = "../assets/img/subs_specials/" + sub["image"][28:]
            self.ac.execute("""
            INSERT INTO sub_weapons(
                name,
                localized_name,
                image
            ) VALUES (%s,%s,%s);
            """, (sub["name"], json.dumps(sub["localized_name"]), sub["image"]))
            self.asset_db.commit()
            logging.info("Inserted %s into the database!" % sub["name"])
    
    def insert_weapons(self):
        with open("../assets/data/weapons.json") as infile:
            wep_classes = json.load(infile)
        for wep_class in wep_classes:
            for weapon in wep_class["weapons"]:
                weapon["image"] = "../assets/img/weapons/" + weapon["image"][29:]
                logging.info(f"Inserting {weapon['name']}...")
                self.ac.execute("""
                INSERT INTO main_weapons(
                    name,
                    class,
                    localized_name,
                    sub,
                    special,
                    site_id
                ) VALUES (%s,%s,%s,%s,%s,%s)
                """, (weapon["name"], wep_class["id"], json.dumps(weapon["localizedName"]), weapon["sub"], weapon["special"], weapon["id"]))
                self.asset_db.commit()
                logging.info("Inserted %s into the database!" % weapon["name"])

if __name__ == "__main__":
    coloredlogs.DEFAULT_FIELD_STYLES.update({'funcName': {'color': 'cyan'}})
    coloredlogs.DEFAULT_FIELD_STYLES["name"]["color"] = 'yellow'
    coloredlogs.install(
        level="INFO",
        fmt="[%(hostname)s] %(asctime)s %(funcName)s(%(lineno)s) %(name)s[%(process)d] %(levelname)s %(message)s"
    )
    asd = AssetDatabase()
    asd.regen_tables()
    asd.insert_headgear()
    asd.insert_clothing()    
    asd.insert_shoes()
    asd.insert_abilities()
    asd.insert_specials()
    asd.insert_subs()
    asd.insert_weapons()