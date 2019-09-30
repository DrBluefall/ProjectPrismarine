CREATE TABLE IF NOT EXISTS player_profiles (
    id BIGINT PRIMARY KEY, -- a user's discord ID.
    friend_code CHARACTER(17) DEFAULT $$SW-XXXX-XXXX-XXXX$$, -- friend code. Hide this if `is_private` is true.
    ign CHARACTER VARYING(10) DEFAULT $$Unset!$$, -- in game name. ez gg.
    level INTEGER DEFAULT $$1$$, -- player level. That's it.
    -- various ranks of a player. SR is included here for the sake of completeness, despite being a separate game mode.
    sz CHARACTER VARYING(6) DEFAULT $$C-$$,
    tc CHARACTER VARYING(6) DEFAULT $$C-$$,
    rm CHARACTER VARYING(6) DEFAULT $$C-$$,
    cb CHARACTER VARYING(6) DEFAULT $$C-$$,
    sr CHARACTER VARYING(13) DEFAULT $$Intern$$,
    position SMALLINT DEFAULT 0, -- int to indicate position. Maps to {0: "Not Set", 1: "Frontline", 2: "Midline", 3: "Backline", 4: "Flex"}
    loadout JSON, -- JSON data detailing the loadout of a player.
    team_id BIGINT, -- if not `NULL`, this will reference a team in `team_profiles`. The constraint is added later on.
    free_agent BOOLEAN DEFAULT FALSE, -- displays a `Free Agent!` marker on a player's profile.
    is_private BOOLEAN DEFAULT FALSE -- hide FC if 'TRUE', and prevent invites from being received for teams.
);
CREATE TABLE IF NOT EXISTS team_profiles (
    captain BIGINT PRIMARY KEY REFERENCES player_profiles(id) ON DELETE CASCADE, -- teams are tied to their captains, and so their ID is the primary key
    name TEXT DEFAULT $$The Default Team$$, -- team name. not much to it.
    deletion_time BIGINT DEFAULT NULL, -- unix UTC timestamp. if this isn't null, then this team is queued to be deleted.
    description TEXT DEFAULT $$This team is a mystery...$$, -- a team's description.
    thumbnail TEXT, -- a link to a team's thumbnail. PNG or JPG only, as per serenity's restrictions.
    creation_time TEXT, -- unix UTC timestamp. Indicates when the team was created.
    recruiting BOOLEAN DEFAULT FALSE, -- display a small message if a team is recruiting, otherwise keep a profile normal.
    recent_tournaments JSON -- hold the three most recent tournaments in a JSON array.
);
CREATE TABLE IF NOT EXISTS scrims (
    id SERIAL PRIMARY KEY, --self-explanatory.
    team_alpha JSON NOT NULL, --stores data for the team requesting a scrim.
    captain_alpha BIGINT UNIQUE NOT NULL, -- Captain for team alpha.
    team_bravo JSON, --stores data for a respondent team.
    captain_bravo BIGINT UNIQUE, -- Captain for team bravo.
    status SMALLINT DEFAULT 0, -- Status for the scrim. Corresponds to 'Open', 'In-Progress', and 'Finishing'.
    register_time BIGINT, -- time the scrim was registered in the database.
    expire_time BIGINT, -- the time an invite is set to expire. Set to a day after the scrim is registered.
    details TEXT, -- details that an invite can contain (division, maps/modes to play, etc.)
    alpha_role_id BIGINT, -- the role generated for Team Alpha in the scrim server.
    bravo_role_id BIGINT, -- the role generated for Team Alpha in the scrim server.
    channel_id BIGINT -- the channel generated for the scrim.
);
DO $$ -- this block exists because you can't have a table be created with a constraint on a table that doesn't exist.
BEGIN -- it's annoying, but whatever.
    BEGIN
        ALTER TABLE player_profiles
            ADD CONSTRAINT team_profile_id_fkey FOREIGN KEY (team_id) REFERENCES team_profiles(captain)
            ON DELETE SET NULL;
        EXCEPTION WHEN duplicate_object THEN NULL;
    END;
END
$$;
