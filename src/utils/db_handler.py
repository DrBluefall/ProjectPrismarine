# Core Language Imports

import logging

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
            id INTEGER PRIMARY KEY,
            friend_code CHARACTER(17) DEFAULT $$SW-XXXX-XXXX-XXXX$$,
            ign CHARACTER VARYING(10) DEFAULT $$Unset!$$,
            level INTEGER DEFAULT $$1$$,
            sz CHARACTER VARYING(5) DEFAULT $$C-$$,
            tc CHARACTER VARYING(5) DEFAULT $$C-$$,
            rm CHARACTER VARYING(5) DEFAULT $$C-$$,
            cb CHARACTER VARYING(5) DEFAULT $$C-$$,
            sr CHARACTER VARYING(13) DEFAULT $$Intern$$,
            position INTEGER DEFAULT 0,
            loadout JSON,
            team_id INTEGER DEFAULT NULL,
            team_name TEXT DEFAULT $$N/A$$,
            is_captain BOOLEAN DEFAULT FALSE,
            free_agent BOOLEAN DEFAULT FALSE,
            is_private BOOLEAN DEFAULT FALSE
        );
        """)
        self.main_db.commit()
        logging.info("Player Profile database table generated!")
    
    @staticmethod
    def get_position(pos_int = 0):
        pos_map = {
            0: "Not Set",
            1: "Frontline",
            2: "Midline",
            3: "Backline",
            4: "Flex"
        }
        return pos_map[pos_int]
