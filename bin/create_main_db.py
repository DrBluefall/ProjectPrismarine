"""Module that creates main database."""
# yapf: disable

from sqlalchemy import Table, Column, Integer, String
from core import DBHandler

class MainDB(DBHandler):
    """Class containing all main tables for the bot."""

    def __init__(self):
        """Create the main.db."""
        super().__init__()
        self.get_meta("main").drop_all(bind=self.get_db("main"))
        self.reload_meta("main")

        self.prefix_table = Table("prefix", self.get_meta("main"), Column("server_id", Integer, primary_key=True),
            Column("prefix", String))

        self.profile_table = Table("profile", self.get_meta("main"), Column("user_id", Integer, primary_key=True),
            Column("ign", String),
            Column("fc", String),
            Column("level", Integer),
            Column("rm_rank", String),
            Column("tc_rank", String),
            Column("sz_rank", String),
            Column("cb_rank", String),
            Column("sr_rank", String),
            Column("loadout_string", String, server_default="0"*25))

        self.team_profile_table = Table("team_profile", self.get_meta("main"), Column("team_id", Integer, primary_key=True),
            Column("name", String),
            Column("description", String),
            Column("captain", Integer, nullable=False),
            Column("player_2", Integer, nullable=False),
            Column("player_3", Integer, nullable=False),
            Column("player_4", Integer, nullable=False),
            Column("player_5", Integer),
            Column("player_6", Integer),
            Column("player_7", Integer))

        self.team_comps = Table("team_comp", self.get_meta("main"), Column("comp_id", Integer, primary_key=True),
            Column("author_id", Integer),
            Column("name", String),
            Column("description", String),
            Column("weapon_1", String, server_default="0"*25),
            Column("weapon_1_role", String),
            Column("weapon_1_desc", String),
            Column("weapon_2", String, server_default="0"*25),
            Column("weapon_2_role", String),
            Column("weapon_2_desc", String),
            Column("weapon_3", String, server_default="0"*25),
            Column("weapon_3_role", String),
            Column("weapon_3_desc", String),
            Column("weapon_4", String, server_default="0"*25),
            Column("weapon_4_role", String),
            Column("weapon_4_desc", String))

        self.get_meta("main").create_all(bind=self.get_db("main"))

def main():
    """Create main.db."""
    MainDB()
    print("Completed!")

if __name__ == "__main__":
    main()
