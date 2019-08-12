# Core Language Imports

import logging
import re

# Third-Party Imports

import psycopg2 as pg


class DatabaseHandler:
    """Class related to global database management."""

    def __init__(self):
        self.main_db = pg.connect(database="main", host="localhost")
        self.mc = self.main_db.cursor()
    
    def gen_profile_table(self):
        self.mc.execute("""
        CREATE TABLE IF NOT EXISTS player_profiles (
            id BIGINT PRIMARY KEY,
            friend_code CHARACTER(12) DEFAULT $$XXXXXXXXXXXX$$,
            ign CHARACTER VARYING(10) DEFAULT $$Unset!$$,
            level INTEGER DEFAULT $$1$$,
            sz CHARACTER VARYING(6) DEFAULT $$C-$$,
            tc CHARACTER VARYING(6) DEFAULT $$C-$$,
            rm CHARACTER VARYING(6) DEFAULT $$C-$$,
            cb CHARACTER VARYING(6) DEFAULT $$C-$$,
            sr CHARACTER VARYING(13) DEFAULT $$Intern$$,
            position INTEGER DEFAULT 0,
            loadout JSON,
            team_id INTEGER,
            team_name TEXT DEFAULT $$N/A$$,
            is_captain BOOLEAN DEFAULT FALSE,
            free_agent BOOLEAN DEFAULT FALSE,
            is_private BOOLEAN DEFAULT FALSE
        );
        """)
        self.main_db.commit()
        logging.info("Player Profile database table generated!")
    
    def add_profile(self, user_id: int) -> str:
        self.mc.execute("""
        INSERT INTO player_profiles(id) VALUES (%s)
        ON CONFLICT DO NOTHING;
        """,(user_id,))
        self.main_db.commit()
    
    @staticmethod
    def get_position(pos_int = 0) -> str:
        pos_map = {
            0: "Not Set",
            1: "Frontline",
            2: "Midline",
            3: "Backline",
            4: "Flex"
        }
        return pos_map[pos_int]

    def update_fc(self, id: int, friend_code: str):
        friend_code = re.sub(r"\D", "", friend_code)
        self.mc.execute("""
        UPDATE player_profiles SET friend_code = %s WHERE id = %s;
        """, (friend_code, id))

    def update_rank(self, id: int, mode: str, rank: str) -> str:
        rank_list = (
            "C-", "C", "C+", "B-", "B", "B+", "A-", "A", "A+", "S", "S+0",
            "S+1", "S+2", "S+3", "S+4", "S+5", "S+6", "S+7", "S+8", "S+9", "X"
        )
        modes = {
            "Splat Zones": {
                "aliases": ("sz", "splatzones", "sz_rank"),
                "rlist": rank_list,
                "db_alias": "sz"
            },
            "Rainmaker": {
                "aliases": ("rm", "rainmaker", "rm_rank"),
                "rlist": rank_list,
                "db_alias": "rm"
            },
            "Tower Control": {
                "aliases": ("tc", "towercontrol", "tc_rank"),
                "rlist": rank_list,
                "db_alias": "tc"
            },
            "Clam Blitz": {
                "aliases": ("cb", "clamblitz", "cb_rank"),
                "rlist": rank_list,
                "db_alias": "cb"
            },
            "Salmon Run": {
                "aliases": ("sr", "salmonrun", "sr_rank"),
                "rlist": (
                    "Intern",
                    "Apprentice",
                    "Part-timer",
                    "Go-getter",
                    "Overachiever",
                    "Profreshional",
                ),
                "db_alias": "sr"
            },
        }

        if rank.upper()[:1] == "X":
            power = rank[2:]
            rank = rank[:1]
        else:
            power = ""
        for key, value in modes.items():
            if mode in modes[key]["aliases"] and rank.upper() in modes[key]["rlist"]:
                self.mc.execute(f"""
                UPDATE player_profiles SET {modes[key]["db_alias"]} = %s WHERE id = %s;
                """, ((rank.upper() +" "+ power), id))
                self.main_db.commit()

if __name__ == "__main__":
    dbh = DatabaseHandler()
    dbh.gen_profile_table()
    dbh.add_profile(1)
    dbh.update_rank(1, "tc_rank", "B+")
    dbh.update_rank(1, "sr", "Profreshional")
    dbh.update_fc(1, "edsefe9999eA9999eSZF9999ae")
    dbh.update_rank(1, "sz", "X99999")