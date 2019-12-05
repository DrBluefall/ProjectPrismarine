### TOP PRIORTY:
- Implement Team Module
    - interactive model w/ old PP not viable, takes up valuable threads + requires immense boilerplate
    - Need to find way to implement teams in non-interactive environment
    - IMPLEMENTATION:
        - Teams are bound to their captain. One team per player.
        - Team Data to be stored:
        ```sql
          CREATE TABLE team_profiles (
              captain BIGINT PRIMARY KEY REFERENCES player_profiles, -- A way of restrictng teams to one player each.
              name TEXT DEFAULT 'The Default Team',
              description TEXT DEFAULT 'This team is a mystery...',
              thumbnail TEXT, -- URL of the team's icon/logo/whatever
              creation_time BIGINT, -- stored as unix timestamp
              recruiting BOOLEAN DEFAULT FALSE
          );

        ```
        - tournaments will be stored in their own db table:
        ```sql
        CREATE TABLE tournaments (
            id SERIAL PRIMARY KEY, -- guard against dupes breaking the bot
            tourney_name TEXT, -- name of the tournament competed in
            team_id BIGINT, -- team this result is tied to
            place INTEGER, -- team placement
            register_date BIGINT -- stored as unix timestamp, time result was registered into the bot
        );
        ```
        - Invites will also be stored in their own table:
        ```sql
        CREATE TABLE invites (
            recipient BIGINT REFERENCES player_profiles, -- player recieving an invite
            sender BIGINT REFERENCES team_profiles, -- team sending the invite
            invite_text TEXT, -- message sent with the invite
            PRIMARY KEY (recipient, sender)
        );
        ```
<!-- toc -->



<!-- tocstop -->