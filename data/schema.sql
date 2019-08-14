-- Main Database Tables:

CREATE TABLE player_profiles (
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
    team_id INTEGER,
    team_name TEXT DEFAULT $$N/A$$,
    is_captain BOOLEAN DEFAULT FALSE,
    free_agent BOOLEAN DEFAULT FALSE,
    is_private BOOLEAN DEFAULT FALSE
);

-- Asset Database Tables:

CREATE TABLE headgear (
    name TEXT,
    image TEXT,
    localized_name JSON,
    main TEXT,
    stars INTEGER,
    id INTEGER,
    splatnet INTEGER PRIMARY KEY
);

CREATE TABLE clothing (
    name TEXT,
    image TEXT,
    localized_name JSON,
    main TEXT,
    stars INTEGER,
    id INTEGER,
    splatnet INTEGER PRIMARY KEY
);

CREATE TABLE shoes (
    name TEXT,
    image TEXT,
    localized_name JSON,
    main TEXT,
    stars INTEGER,
    id INTEGER,
    splatnet INTEGER PRIMARY KEY
);

CREATE TABLE abilities (
    name TEXT,
    localized_name JSON,
    image TEXT,
    id INTEGER PRIMARY KEY
);

CREATE TABLE sub_weapons (
    name TEXT PRIMARY KEY,
    localized_name JSON,
    image TEXT
);

CREATE TABLE special_weapons (
    name TEXT PRIMARY KEY,
    localized_name JSON,
    image TEXT
);

CREATE TABLE main_weapons (
    id SERIAL PRIMARY KEY,
    name TEXT,
    class INTEGER,
    localized_name JSON,
    sub TEXT REFERENCES sub_weapons(name),
    special TEXT REFERENCES special_weapons(name),
    site_id INTEGER
);