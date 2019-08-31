# Core Language Imports

import logging
import re
import json
from pprint import pprint
from datetime import datetime, timedelta

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
            position SMALLINT DEFAULT 0,
            loadout JSON,
            team_id BIGINT,
            team_name TEXT DEFAULT $$N/A$$,
            free_agent BOOLEAN DEFAULT FALSE,
            is_private BOOLEAN DEFAULT FALSE
        );
        """)
        self.mc.execute("""
        CREATE TABLE IF NOT EXISTS team_profiles (
            captain BIGINT PRIMARY KEY REFERENCES player_profiles(id) ON DELETE CASCADE,
            name TEXT DEFAULT $$The Default Team$$,
            deletion_time BIGINT DEFAULT NULL,
            description TEXT DEFAULT $$This team is a mystery...$$,
            thumbnail TEXT,
            creation_time TEXT,
            recruiting BOOLEAN DEFAULT FALSE,
            recent_tournaments JSON
        );
        """)
        self.mc.execute("""
        CREATE TABLE IF NOT EXISTS scrims (
            id SERIAL PRIMARY KEY, --self-explanatory.
            team_alpha JSON NOT NULL, --stores data for the team requesting a scrim.
            captain_alpha BIGINT UNIQUE NOT NULL, -- Captain for team alpha.
            team_bravo JSON, --stores data for a respondent team.
            captain_bravo BIGINT UNIQUE, -- Captain for team bravo.
            status SMALLINT DEFAULT 0, -- Status for the scrim. Corresponds to 'Open', 'In-Progress', and 'Finishing'.
            register_time BIGINT, -- time the scrim was registered in the database.
            expire_time BIGINT, -- the time an invite is set to expire. Set to a day after the scrim is registered.
            details TEXT -- details that an invite can contain (division, maps/modes to play, etc.)
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
        """, (user_id,))
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
                """, ((rank.capitalize() + " " + power), id))
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
        ret = self.mc.execute("""
        INSERT INTO team_profiles(captain, name, creation_time) VALUES (%s, %s, %s)
            ON CONFLICT DO NOTHING
            RETURNING captain;
        """, (captain, name, datetime.now().strftime("Time: %I:%M:%S %p Date: %d %B %Y"))).fetchone()
        self.main_db.commit()
        if ret is not None:
            self.mc.execute("""
            UPDATE player_profiles SET team_id = %s, team_name = %s WHERE id = %s;
            """, (captain, name, captain))
            self.main_db.commit()
        return ret

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
            "players": [item for sublist in players for item in sublist]
        }

    def add_player(self, captain: int, player: int):
        team = self.get_team(captain)
        self.mc.execute("""
        UPDATE player_profiles SET team_id = %s, team_name = %s WHERE id = %s;
        """, (team['team']['captain'], team['team']['name'], player))
        self.main_db.commit()

    def update_desc(self, captain: int, desc: str):
        self.mc.execute("""
        UPDATE team_profiles SET description = %s WHERE captain = %s;
        """, (desc, captain))
        self.main_db.commit()

    def toggle_recruit(self, captain):
        rc = not self.mc.execute("""
        SELECT recruiting FROM team_profiles WHERE captain = %s;
        """, (captain,)).fetchone()[0]
        self.mc.execute("""
        UPDATE team_profiles SET recruiting = %s WHERE captain = %s;
        """, (rc, captain))
        self.main_db.commit()
        return rc

    def add_tourney(self, captain: int, tourney_name: str, place: int):
        tourney_list = self.mc.execute("""
        SELECT recent_tournaments FROM team_profiles WHERE captain = %s;
        """, (captain,)).fetchone()[0]
        if tourney_list is None:
            tourney_list = []
        tourney_dict = {
            "place": place,
            "tourney": tourney_name,
            "date": datetime.now().timestamp()
        }
        tourney_list.insert(0, tourney_dict)
        if len(tourney_list) > 3:
            tourney_list.pop(3)
        self.mc.execute("""
        UPDATE team_profiles SET recent_tournaments = %s WHERE captain = %s;
        """, (json.dumps(tourney_list), captain))
        self.main_db.commit()

    def update_thumbnail(self, captain: int, url: str):
        self.mc.execute("""
        UPDATE team_profiles SET thumbnail = %s WHERE captain = %s;
        """, (url, captain))
        self.main_db.commit()

    def delete_team(self, captain):
        self.mc.execute("""
        UPDATE team_profiles SET deletion_time = %s WHERE captain = %s;
        """, ((datetime.now() + timedelta(days=3)).timestamp(), captain))
        self.main_db.commit()

    def recover_team(self, captain):
        self.mc.execute("""
        UPDATE team_profiles SET deletion_time = NULL WHERE captain = %s;
        """, (captain,))
        self.main_db.commit()

    def clear_teams(self):
        teams = self.mc.execute("""
        SELECT deletion_time, captain FROM team_profiles WHERE deletion_time IS NOT NULL;
        """).fetchall()
        for team in teams:
            if datetime.fromtimestamp(team[0]) < datetime.now():
                self.mc.execute("""
                DELETE FROM team_profiles WHERE captain = %s;
                """, team[1])
                self.main_db.commit()

    def get_scrims(self, captain):
        ret = self.mc.execute("""
        SELECT row_to_json(scrims) FROM scrims WHERE captain_alpha != %s AND status = 0;
        """, (captain,)).fetchall()
        return tuple([item for sublist in ret for item in sublist])

    def add_scrim(self, captain: int, details: str) -> int:
        team = self.get_team(captain)
        if team is None:
            return 1
        elif team['team']['deletion_time'] is not None:
            return 3

        ret = self.mc.execute("""
        INSERT INTO scrims(team_alpha, captain_alpha, register_time, expire_time, details)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
        RETURNING team_alpha;
        """, (
            json.dumps(team),
            captain,
            datetime.now().timestamp(),
            (datetime.now() + timedelta(hours=24)).timestamp(),
            details
        )).fetchone()
        self.main_db.commit()
        return 0 if ret is not None else 2

    def get_scrim(self, scrim_id):
        return self.mc.execute("""
        SELECT row_to_json(scrims) FROM scrims WHERE id = %s;
        """, (scrim_id,)).fetchone()[0]

    @staticmethod
    def get_position(pos_int=0) -> str:
        pos_map = {
            0: "Not Set",
            1: "Frontline",
            2: "Midline",
            3: "Backline",
            4: "Flex"
        }
        return pos_map[pos_int] if pos_int in pos_map.keys() else None

    @staticmethod
    def get_status(stat: int = 0) -> str:
        stat_map = {
            0: "Open!",
            1: "Scrim In Progress!",
            2: "Finished!"
        }
        return stat_map[stat] if stat in stat_map.keys() else None


if __name__ == "__main__":
    dbh = DatabaseHandler()
    dbh.get_scrims(1)
