# Core Language Imports

import logging
import re
import json
from pprint import pprint

# Third-Party Imports

import pg8000 as pg


class DatabaseHandler:
    """Class related to global database management."""

    def __init__(self):
        self.main_db = pg.connect(user='prismarine-core', database="main", host="localhost")
        self.mc = self.main_db.cursor()
    
    def get_profile(self, user: int):

        res = self.mc.execute("""
        SELECT row_to_json(player_profiles) FROM player_profiles WHERE id = %s;
        """, (user,)).fetchone()
        if res is None:
            return None
        else:
            return res[0]
    
    def gen_tables(self):
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
            free_agent BOOLEAN DEFAULT FALSE,
            is_private BOOLEAN DEFAULT FALSE
        );
        """)
        self.mc.execute("""
        CREATE TABLE IF NOT EXISTS team_profiles (
            captain BIGINT PRIMARY KEY REFERENCES player_profiles(id) ON DELETE CASCADE,
            name TEXT DEFAULT $$The Default Team$$,
            deletion_time TIMESTAMP DEFAULT NULL,
            description TEXT DEFAULT $$This team is a mystery...$$,
            thumbnail TEXT,
            timezone TIMESTAMP DEFAULT NOW(),
            recruiting BOOLEAN DEFAULT FALSE,
            recent_tournaments JSON
        );
        """)
        self.mc.execute("""
        DO $$
        BEGIN
        BEGIN
        ALTER TABLE player_profiles
            ADD CONSTRAINT team_profile_id_fkey FOREIGN KEY (team_id) REFERENCES team_profiles(captain)
            ON DELETE SET NULL;
        EXCEPTION WHEN duplicate_object THEN NULL;
        END;
        END $$;
        """)
        self.main_db.commit()
        logging.info("Database tables generated!")
    
    def add_profile(self, user_id: int):
        self.mc.execute("""
        INSERT INTO player_profiles(id) VALUES (%s)
        ON CONFLICT DO NOTHING;
        """,(user_id,))
        self.main_db.commit()
    
    def update_level(self, id: int, level: int):
        self.mc.execute("""
        UPDATE player_profiles SET level = %s WHERE id = %s;
        """, (level, id))
        self.main_db.commit()
    
    def update_position(self, id: int, position: int):
        if position is not None:
            self.mc.execute("""
            UPDATE player_profiles SET position = %s WHERE id = %s;
            """, (position, id))
            self.main_db.commit()
        else:
            raise ValueError

    def update_fc(self, id: int, friend_code: str):
        friend_code = re.sub(r"\D", "", friend_code)
        if len(friend_code) != 12:
            return False
        self.mc.execute("""
        UPDATE player_profiles SET friend_code = %s WHERE id = %s;
        """, (friend_code, id))
        self.main_db.commit()
        return True
    
    def update_ign(self, id: str, name: str):
        self.mc.execute("""
        UPDATE player_profiles SET ign = %s WHERE id = %s;
        """, (name, id))
        self.main_db.commit()
    
    def toggle_private(self, id: int):
        private = not self.mc.execute("""
        SELECT is_private FROM player_profiles WHERE id = %s;
        """, (id,)).fetchone()[0]
        self.mc.execute("""
        UPDATE player_profiles SET is_private = %s WHERE id = %s;
        """, (private, id))
        self.main_db.commit()
        return private

    def toggle_free_agent(self, id: int):
        free_agent = not self.mc.execute("""
        SELECT free_agent FROM player_profiles WHERE id = %s;
        """, (id,)).fetchone()[0]
        self.mc.execute("""
        UPDATE player_profiles SET free_agent = %s WHERE id = %s;
        """, (free_agent, id))
        self.main_db.commit()
        return free_agent

    def toggle_captain(self, id: int):
        is_captain = not self.mc.execute("""
        SELECT is_captain FROM player_profiles WHERE id = %s;
        """, (id,)).fetchone()[0]
        self.mc.execute("""
        UPDATE player_profiles SET is_captain = %s WHERE id = %s;
        """, (is_captain, id))
        self.main_db.commit()
        return is_captain

    def update_rank(self, id: int, mode: str, rank: str):
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
            if mode in modes[key]["aliases"] and rank.capitalize() in modes[key]["rlist"]:
                self.mc.execute(f"""
                UPDATE player_profiles SET {modes[key]["db_alias"]} = %s WHERE id = %s;
                """, ((rank.capitalize() +" "+ power), id))
                self.main_db.commit()
                return True
        return False
    
    def update_loadout(self, user: int, loadout: dict):
        self.mc.execute("""
        UPDATE player_profiles SET loadout = %s WHERE id = %s;
        """, (json.dumps(loadout), user))
        self.main_db.commit()

    def new_team(self, captain: int, name: str):
        """Enter a new team into the database."""
        return self.mc.execute("""
        INSERT INTO team_profiles(captain, name) VALUES (%s, %s)
            ON CONFLICT DO NOTHING
            RETURNING captain;
        """, (captain, name)).fetchone()
        self.main_db.commit()
    
    def get_team(self, captain: int):
        team = self.mc.execute("""
        SELECT row_to_json(team_profiles) FROM team_profiles WHERE captain = %s;
        """, (captain,)).fetchone()
        if team is None:
            return None
        else:
            team = team[0]
        players = self.mc.execute("""
        SELECT row_to_json(player_profiles) FROM player_profiles WHERE team_id = %s; 
        """, (captain,)).fetchall()
        return {
            "team": team,
            "players": players
        }
    
    def add_player(self, captain: int, player: int):
        team = self.get_team(captain)
        player = self.mc.execute("""
        UPDATE player_profiles SET team_id = %s, team_name = %s WHERE id = %s;
        """, (team['captain'], team['name'], player))
        
    @staticmethod
    def get_position(pos_int = 0) -> str:
        pos_map = {
            0: "Not Set",
            1: "Frontline",
            2: "Midline",
            3: "Backline",
            4: "Flex"
        }
        return pos_map[pos_int] if pos_int in pos_map.keys() else None

if __name__ == "__main__":
    dbh = DatabaseHandler()
    dbh.new_team(1, "foo")
    pprint(dbh.get_team(1))