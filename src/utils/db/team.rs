#![allow(dead_code, unused_variables)]

use crate::utils::db::Player;
use crate::utils::misc;
use chrono::{DateTime, TimeZone, Utc};
use regex::Regex;
use std::backtrace::Backtrace;
use std::convert::TryInto;
use unicode_segmentation::UnicodeSegmentation;

type URL = String;

lazy_static! {
    static ref HTTPRE: Regex = Regex::new(
        "https://cdn.discordapp.com/attachments/605171465943253002/653361049776422922/image0.png"
    )
    .unwrap();
}

#[derive(Debug)]
pub struct Team {
    /// Name of the team.
    name: String,
    /// List of the team's players.
    players: Vec<Player>,
    /// This is the *only* person allowed to modify the team. *ALWAYS
    /// MAKE SURE THAT TEAM MODIFICATION COMMANDS VALIDATE FOR CAPTAIN
    /// STATUS!*
    captain: Player,

    /// Discord embeds have a cap, so we'll need to make sure that we
    /// don't get ridiculously long descriptions. If someone *wants*
    /// to have a ridiculously long description, use a Google Doc and
    /// link it in this field.
    description: String,

    /// This is meant to be a URL, may need to find a way to make sure
    /// passed in URLs are valid
    thumbnail: URL,

    /// Time when team was registered into the bot. This is immutable
    /// and set upon creation.
    creation_time: DateTime<Utc>,

    /// Time (if a team is going to be deleted) when a team is going to
    /// be deleted.
    deletion_time: Option<DateTime<Utc>>,

    /// Whether or not a team is recruiting.
    recruiting: bool,

    /// The tournaments a team has participated. Only the most recent
    /// 3 will be shown, but any registered in the bot will be stored.
    tournaments: Vec<Tournament>,
}

#[derive(Debug)]
pub struct Tournament {
    /// The name of the tournament.
    name: String,
    /// How the team registering this tourney result placed.
    place: i16,
    /// When this result was registered into the bot. This
    /// is stored in the db as a UNIX timestamp.
    time: DateTime<Utc>,
}

#[derive(Debug)]
pub struct Invite {
    /// The player that the invite was sent to
    recipient: Player,
    /// The team that sent it
    sender: Team,
    /// whatever message the team included
    message: Option<String>,
    /// time this invite expires. Set to 3 days after sending
    deletion_time: DateTime<Utc>,
}

impl Tournament {
    pub fn new(name: String, place: i16, time: DateTime<Utc>) -> Self {
        Tournament { name, place, time }
    }
}

impl Invite {
    pub fn add_to_db(
        recipient: &Player,
        sender: &Team,
        message: &Option<String>,
        deletion_time: DateTime<Utc>,
    ) -> Result<u64, postgres::Error> {
        misc::get_db_connection().execute(
            "
            INSERT INTO public.invites(recipient, sender, invite_text, deletion_time) 
            VALUES ($1, $2, $3, $4);
            ",
            &[
                &recipient.id(),
                &sender.captain.id(),
                &message,
                &deletion_time.timestamp(),
            ],
        )
    }

    pub fn from_db(recipient_id: i64) -> Result<Vec<Self>, misc::ModelError> {
        let c = misc::get_db_connection();

        let res = match c.query(
            "
            SELECT recipient, sender, invite_text, deletion_time FROM public.invites WHERE recipient = $1;
            ",
            &[&recipient_id],
        ) {
            Ok(v) => v,
            Err(e) => {
                return Err(misc::ModelError::Database(
                    format!("{:?}", e),
                    Backtrace::capture(),
                ))
            }
        };

        if res.is_empty() {
            return Err(misc::ModelError::Database(
                format!("No invite found with recipient ID {}.", recipient_id),
                Backtrace::capture(),
            ));
        }

        let mut invites: Vec<Self> = Vec::new();
        for row in &res {
            let player_id: i64 = row.get(0);
            let recipient = Player::from_db(player_id.try_into().unwrap())?;
            let team_id: i64 = row.get(1);
            let sender = Team::from_db(team_id.try_into().unwrap())?;
            let message: Option<String> = row.get(2);
            let deletion_time = {
                let stamp: i64 = row.get(3);
                Utc.timestamp(stamp, 0)
            };

            invites.push(Self {
                recipient,
                sender,
                message,
                deletion_time,
            });
        }
        Ok(invites)
    }
}

impl Team {
    /// Insert a new team into the database table.
    pub fn add_to_db(new_cap: &Player, name: &str) -> Result<u64, postgres::Error> {
        misc::get_db_connection().execute(
            "
            INSERT INTO public.team_profiles(captain, creation_time, name) VALUES ($1,$2,$3);
            ",
            &[new_cap.id(), &Utc::now().timestamp(), &name],
        )
    }
    /// Get a team's data from the database. If not found, it'll return
    /// `ModelError::Team` with the id of the team that wasn't found. I *may*
    /// add an ability to search for teams by name, but this is easier for now.
    pub fn from_db(team_id: u64) -> Result<Team, misc::ModelError> {
        // TODO: Implement this
        /* NOTE: There are several things that need to be done here.
        First, get the team's data out of the database. This is
        the key to all the other data. Next, get the team's captain
        for display. After which we can assemble the the vector of
        players by calling out to the `Player::from_db` function.
        ( Maybe it would be a good idea to make a macro that can
        reduce the needed boilerplate to get a player... something
        to consider for the future. ) Anyway, the last bit will be
        to query the database for the most recent tournaments the
        team has registered. Because we're storing the register
        times as unix timestamps, we *should* be able to just
        query with the "ORDER BY time DESC LIMIT 3" restriction.
        OH, and we may want to return a special error if a team
        is in the process of being deleted. That or have a special
        marker be displayed on the frontend to indicate that the
         team will be deleted soon. */
        let c = misc::get_db_connection();

        // First thing's first: grab the team's captain. Their ID
        // is the same as their team's ID, so we can just use this.
        let captain = match Player::from_db(team_id) {
            Ok(v) => v,
            Err(e) => return Err(e),
        };
        // Next part is slightly harder. We need to get all the
        // players in a team. Since the team ID is an FK to the
        // captain's user ID, we can just query the player table w/
        // the captain's ID.
        let mut player_ids: Vec<i64> = Vec::new();

        for row in c
            .query(
                "
            SELECT id FROM public.player_profiles WHERE team_id = $1;
            ",
                &[&(team_id as i64)],
            )
            .unwrap()
            .iter()
        {
            let id: i64 = row.get(0);
            player_ids.push(id);
        }

        let mut players: Vec<Player> = Vec::new();

        for id in &player_ids {
            players.push(match Player::from_db(*id as u64) {
                Ok(v) => v,
                Err(e) => return Err(e),
            });
        }

        // Next up, the tournaments. This should be as easy as gathering
        // the data and assembling the structs.

        let mut tournaments: Vec<Tournament> = Vec::new();

        for row in {
            match c.query(
                "
            SELECT name, place, time FROM public.tournaments WHERE team = $1;
            ",
                &[&(team_id as i64)],
            ) {
                Ok(v) => v,
                Err(e) => {
                    return Err(misc::ModelError::Database(
                        format!("{:?}", e),
                        Backtrace::capture(),
                    ))
                }
            }
        }
        .iter()
        {
            tournaments.push(Tournament {
                name: row.get(0),
                place: row.get(1),
                time: Utc.timestamp(row.get(2), 0),
            })
        }

        // Now that we have everything else we need, it's time to get the
        // data for the team itself!

        let res = match c.query(
            "
            SELECT name, description, thumbnail, creation_time, recruiting,
            deletion_time FROM public.team_profiles WHERE captain = $1;
            ",
            &[&(team_id as i64)],
        ) {
            Ok(v) => v,
            Err(e) => {
                return Err(misc::ModelError::Database(
                    format!("{:?}", e),
                    Backtrace::capture(),
                ))
            }
        };
        if res.is_empty() {
            return Err(misc::ModelError::NotFound(
                misc::NFKind::Team(team_id),
                Backtrace::capture(),
            ));
        }
        let dat = res.get(0);

        Ok(Self {
            name: dat.get(0),
            players,
            captain,
            description: dat.get(1),
            thumbnail: dat.get(2),
            creation_time: Utc.timestamp(dat.get(3), 0),
            recruiting: dat.get(4),
            deletion_time: if let Some(v) = dat.get(5) {
                Some(Utc.timestamp(v, 0))
            } else {
                None
            },
            tournaments,
        })
    }
    /// Get a team's name.
    pub fn name(&self) -> &String {
        &self.name
    }
    /// Set a team's name. NOTE: We'll probably have to put
    /// a cap on name lengths if we get any issues. For now,
    /// I'll keep it uncapped, but I'll be sure to monitor
    /// for any issues.
    pub fn set_name(&mut self, new_name: String) {
        self.name = new_name;
    }

    /// Get the players from a team.
    pub fn players(&self) -> &Vec<Player> {
        &self.players
    }
    pub fn add_player(&mut self, player: Player) {
        self.players.push(player);
    }
    /// Get a team's description.
    pub fn desc(&self) -> &String {
        &self.description
    }
    /// Replace a team's description with a brand new one.
    pub fn mod_desc(&mut self, new: String) -> Result<(), ()> {
        if UnicodeSegmentation::graphemes(new.as_str(), true).count() > 2048 {
            return Err(());
        } else {
            self.description = new;
        }
        Ok(())
    }
    /// Get a team's thumbnail.
    pub fn thumbnail(&self) -> &URL {
        &self.thumbnail
    }
    /// Set a team's thumbnail.
    pub fn set_thumbnail(&mut self, url: URL) -> Result<(), ()> {
        // Want to validate urls before we store them, lest we
        // allow the database to hold bad data.
        if HTTPRE.is_match(&url) {
            self.thumbnail = url;
        } else {
            return Err(());
        }
        Ok(())
    }
    pub fn time_created(&self) -> &DateTime<Utc> {
        &self.creation_time
    }
    pub fn del_time(&self) -> &Option<DateTime<Utc>> {
        &self.deletion_time
    }
    pub fn set_del_time(&mut self, should_del: bool, time: Option<i64>) {
        if should_del {
            self.deletion_time =
                Some(Utc::now() + time::Duration::days(if let Some(v) = time { v } else { 7 }));
        } else {
            self.deletion_time = None;
        }
    }
    pub fn add_tournament(&mut self, tournament: Tournament) {
        self.tournaments.push(tournament);
    }

    pub fn update(&mut self) -> Result<(), misc::ModelError> {
        let c = misc::get_db_connection();

        let dt = if let Some(v) = self.deletion_time {
            Some(v.timestamp())
        } else {
            None
        };

        if let Err(e) = c.execute(
            "
            UPDATE public.team_profiles
                SET name = $1,
                deletion_time = $2,
                description = $3,
                thumbnail = $4,
                recruiting = $5
            WHERE captain = $6;
            ",
            &[
                &self.name,
                &dt,
                &self.description,
                &self.thumbnail,
                &self.recruiting,
                &self.captain.id(),
            ],
        ) {
            return Err(misc::ModelError::Database(
                format!("{:?}", e),
                Backtrace::capture(),
            ));
        }

        for player in &mut self.players {
            player.set_team_id(Some(*self.captain.id()));
            if let Err(e) = player.update() {
                error!(
                    "Something went sideways in updating the database!\n\nError: {:?}\n\n{:#?}",
                    e,
                    Backtrace::capture()
                );
                return Err(misc::ModelError::Database(
                    format!("{:?}", e),
                    Backtrace::capture(),
                ));
            }
        }
        let stmt = c
            .prepare_cached(
                "
        INSERT INTO public.tournaments(name, place, time, team)
            VALUES ($1, $2, $3, $4);
            ",
            )
            .unwrap();

        for tourney in &self.tournaments {
            if let Err(e) = stmt.execute(&[
                &tourney.name,
                &tourney.place,
                &tourney.time.timestamp(),
                &self.captain.id(),
            ]) {
                return Err(misc::ModelError::Database(
                    format!("{:?}", e),
                    Backtrace::capture(),
                ));
            }
        }

        Ok(())
    }
}
