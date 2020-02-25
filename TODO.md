# Migrate Bot -- PostgreSQL -> MySQL
* The old build used PostgreSQL, and the new server doesn't use it.
* As such, motions will be made to transfer the bot's DBs and code to MySQL.
* Tables and Databases have already been created and data moved over :)

* note to self: REMEMBER TO REFERENCE THE GODDAMN DOCS.

## Source code to be refactored

### MAIN DB MODULE
* [x] misc.rs

### Database Modules
* [ ] loadout.rs
* [ ] player.rs
* [ ] team.rs

### Command Modules
* [ ] player.rs
* [ ] team.rs

---

# Team Module
* Teams are bound to their captain. One team per player.
* Team data should only be able to be modified by the captain.
* Check the user's ID against the DB when commands that modify the team's data are invoked to verify team status.

* Tournaments will be stored in their own db table:
        ```sql
        CREATE TABLE tournaments 
	(
            id			INT	PRIMARY KEY	NOT NULL	UNIQUE, -- guard against dupes breaking the bot
            tourney_name	VARCHAR(45), 					-- name of the tournament competed in
            team_id 		BIGINT, 					-- team this result is tied to
            place 		INT, 						-- team placement
            register_date 	BIGINT 						-- stored as unix timestamp, time result was registered into the bot
        );
        ```
        * Invites will also be stored in their own table:
        ```sql
        CREATE TABLE invites 
	(
            recipient		BIGINT		PRIMARY KEY	NOT NULL	REFERENCES player_profiles, 	-- player recieving an invite
            sender 		BIGINT		PRIMARY KEY	NOT NULL	REFERENCES team_profiles, 	-- team sending the invite
            invite_text		VARCHAR(65), 									-- message sent with invite. Limit to about the length of a twitter tweet (like desc.)
        );
        ```
* Team data:
* Limit the length of descriptions, and possibly names as well (Currently, neither are limited in length.)
* Restrict invite sending to the Captain only as well, and be sure to check that:
	* User is in a team
	* User is a captain
	* `*msg.author.id.as_u64()` -- Will fetch invoker's ID
	* `Team::from_db().is_ok()` -- Is the user in a team, and are they the captain?

* At the moment, the amount of invites that can be sent out in a given time won't be limited, but it may be in the future.
* Duplicate invites (to one user) should be discouraged, however.

<!-- toc -->



<!-- tocstop -->
