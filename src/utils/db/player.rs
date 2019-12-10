use crate::impl_string_utils;
use crate::utils::db::{loadout::RawLoadout, Loadout};
use crate::utils::misc;
use crate::utils::misc::{ModelError, NFKind};
use postgres::Error;
use regex::Regex;
use std::backtrace::Backtrace;
use std::collections::HashMap;
use unicode_segmentation::UnicodeSegmentation;

impl_string_utils!();

lazy_static! {
    static ref FCRE: Regex = Regex::new(r"\D").unwrap();
    static ref RANKRE: Regex = Regex::new(r"(([ABC][-+ ]?)|(S\+[0-9]?)|S|(X [0-9]{0,4}))").unwrap();
}

static SR_RANK_ARRAY: [&str; 6] = [
    "intern",
    "apprentice",
    "part-timer",
    "go-getter",
    "overachiever",
    "profreshional",
];

#[derive(Debug)]
pub struct Player {
    id: i64,
    friend_code: String,
    ign: String,
    pub level: i32,
    sz: String,
    tc: String,
    rm: String,
    cb: String,
    sr: String,
    position: i16,
    loadout: Loadout,
    team_id: Option<i64>,
    free_agent: bool,
    is_private: bool,
}

impl Player {
    pub fn add_to_db(user_id: u64) -> Result<u64, Error> {
        misc::get_db_connection().execute(
            "
        INSERT INTO public.player_profiles(id) VALUES ($1)
        ON CONFLICT DO NOTHING;
        ",
            &[&(user_id as i64)],
        )
    }
    pub fn from_db(user_id: u64) -> Result<Player, ModelError> {
        let rows = match misc::get_db_connection().query(
            "SELECT * FROM public.player_profiles WHERE id = $1",
            &[&(user_id as i64)],
        ) {
            Ok(v) => Some(v),
            Err(e) => {
                return Err(ModelError::Database(
                    format!("Error in player data retrieval: {:#?}", e),
                    Backtrace::capture(),
                ))
            }
        };
        if rows.is_none() {
            return Err(ModelError::NotFound(
                NFKind::Player(user_id),
                Backtrace::capture(),
            ));
        }
        let rows = rows.unwrap();
        if rows.len() == 0 {
            return Err(ModelError::NotFound(
                NFKind::Player(user_id),
                Backtrace::capture(),
            ));
        }
        let row = rows.get(0);
        let lv: i32 = row.get("level");
        let dt: String = row.get("loadout");
        let loadout = match Loadout::from_raw(match RawLoadout::parse(dt.as_str()) {
            Ok(v) => v,
            Err(e) => return Err(e),
        }) {
            Ok(v) => v,
            Err(e) => return Err(e),
        };

        Ok(Player {
            id: row.get("id"),
            friend_code: row.get("friend_code"),
            ign: row.get("ign"),
            level: lv,
            sz: row.get("sz"),
            tc: row.get("tc"),
            rm: row.get("rm"),
            cb: row.get("cb"),
            sr: row.get("sr"),
            position: row.get("position"),
            loadout,
            team_id: row.get("team_id"),
            free_agent: row.get("free_agent"),
            is_private: row.get("is_private"),
        })
    }
    pub fn id(&self) -> &i64 {
        &self.id
    }
    pub fn fc(&self) -> &String {
        &self.friend_code
    }
    pub fn set_fc(&mut self, fc_string: &str) -> Result<(), ()> {
        let regexed = FCRE.replace_all(fc_string, "");

        if regexed.len() == 12 {
            let f1 = regexed.substring(0, 4);
            let f2 = regexed.substring(4, 4);
            let f3 = regexed.substring(8, 4);
            self.friend_code = format!("SW-{}-{}-{}", f1, f2, f3);
        } else {
            return Err(());
        }

        Ok(())
    }
    pub fn name(&self) -> &String {
        &self.ign
    }
    pub fn set_name(&mut self, name: String) -> Result<(), ()> {
        let __name__ = UnicodeSegmentation::graphemes(name.as_str(), true).collect::<Vec<&str>>();

        if __name__.len() > 10 || __name__.len() < 1 {
            return Err(());
        } else {
            self.ign = name;
        }
        Ok(())
    }
    pub fn ranks(&self) -> HashMap<&'static str, &String> {
        let mut hm = HashMap::new();
        hm.insert("Splat Zones", &self.sz);
        hm.insert("Tower Control", &self.tc);
        hm.insert("Rainmaker", &self.rm);
        hm.insert("Clam Blitz", &self.cb);
        hm.insert("Salmon Run", &self.sr);
        hm
    }
    pub fn set_rank(&mut self, mode: String, rank: String) -> Result<(), ModelError> {
        match mode.as_str() {
            "sz" | "splat_zones" | "sz_rank" => {
                if !RANKRE.is_match(rank.as_str()) {
                    return Err(ModelError::InvalidParameter(format!(
                        "Invalid Rank: {}",
                        rank.as_str()
                    )));
                }
                self.sz = rank.as_str().to_ascii_uppercase().to_string()
            }
            "tc" | "tower_control" | "tc_rank" => {
                if !RANKRE.is_match(rank.as_str()) {
                    return Err(ModelError::InvalidParameter(format!(
                        "Invalid Rank: {}",
                        rank.as_str()
                    )));
                }
                self.tc = rank.as_str().to_ascii_uppercase().to_string()
            }
            "rm" | "rainmaker" | "rm_rank" => {
                if !RANKRE.is_match(rank.as_str()) {
                    return Err(ModelError::InvalidParameter(format!(
                        "Invalid Rank: {}",
                        rank.as_str()
                    )));
                }
                self.rm = rank.as_str().to_ascii_uppercase().to_string()
            }
            "cb" | "clam_blitz" | "cb_rank" => {
                if !RANKRE.is_match(rank.as_str()) {
                    return Err(ModelError::InvalidParameter(format!(
                        "Invalid Rank: {}",
                        rank.as_str()
                    )));
                }
                self.cb = rank.as_str().to_ascii_uppercase().to_string()
            }
            "sr" | "salmon_run" | "sr_rank" => {
                for static_rank in SR_RANK_ARRAY.iter() {
                    if &(rank.as_str().to_ascii_lowercase()) == static_rank {
                        use heck::TitleCase;

                        self.sr = rank.as_str().to_title_case().replace(' ', "-").to_string();
                        return Ok(());
                    }
                }
                return Err(ModelError::InvalidParameter(format!(
                    "Invalid Salmon Run Rank: {}",
                    rank.as_str()
                )));
            }
            _ => {
                return Err(ModelError::InvalidParameter(format!(
                    "Invalid Mode: {}",
                    mode.as_str()
                )))
            }
        }
        Ok(())
    }

    pub fn pos(&self) -> &'static str {
        misc::pos_map().get(&self.position).unwrap()
    }
    pub fn set_pos(&mut self, pos_int: i16) -> Result<(), ()> {
        let pos_map = misc::pos_map();
        for key in pos_map.keys() {
            if key == &pos_int {
                self.position = pos_int;
                return Ok(());
            }
        }
        Err(())
    }

    pub fn loadout(&self) -> &Loadout {
        &self.loadout
    }
    pub fn set_loadout(&mut self, hex: &str) -> Result<(), ModelError> {
        let raw = match RawLoadout::parse(hex) {
            Ok(v) => v,
            Err(e) => return Err(e),
        };
        match Loadout::from_raw(raw) {
            Ok(v) => self.loadout = v,
            Err(e) => return Err(e),
        }
        Ok(())
    }
    #[allow(dead_code)] // Only for now, while teams are still being implemented.
    pub fn team_id(&self) -> &Option<i64> {
        &self.team_id
    }
    pub fn set_team_id(&mut self, team_id: Option<i64>) {
        self.team_id = team_id;
    }
    pub fn is_free_agent(&self) -> &bool {
        &self.free_agent
    }
    pub fn set_free_agent(&mut self, response: String) -> Result<&bool, ModelError> {
        let tmp = response.as_str().to_ascii_lowercase();
        let r = tmp.as_str();

        match r {
            "ok" | "yes" | "true" | "1" => self.free_agent = true,
            "no" | "false" | "0" => self.free_agent = false,
            _ => {
                return Err(ModelError::InvalidParameter(format!(
                    "Invalid response: `{}`",
                    response
                )))
            }
        }

        Ok(&self.free_agent)
    }

    pub fn is_private(&self) -> &bool {
        &self.is_private
    }
    pub fn set_private(&mut self, response: String) -> Result<&bool, ModelError> {
        let tmp = response.as_str().to_ascii_lowercase();
        let r = tmp.as_str();

        match r {
            "ok" | "yes" | "true" | "1" => self.is_private = true,
            "no" | "false" | "0" => self.is_private = false,
            _ => {
                return Err(ModelError::InvalidParameter(format!(
                    "Invalid response: `{}`",
                    response
                )))
            }
        }

        Ok(&self.is_private)
    }
    pub fn update(&self) -> Result<u64, Error> {
        misc::get_db_connection().execute(
            "
UPDATE public.player_profiles
SET
    friend_code = $1,
    ign = $2,
    level = $3,
    sz = $4, tc = $5, rm = $6, cb = $7, sr = $8,
    position = $9,
    loadout = $10,
    team_id = $11,
    is_private = $12,
    free_agent = $13,
    team_id = $14
WHERE id = $15;
                    ",
            &[
                &self.friend_code,
                &self.ign,
                &self.level,
                &self.sz,
                &self.tc,
                &self.rm,
                &self.cb,
                &self.sr,
                &self.position,
                &self.loadout.raw().hex(),
                &self.team_id,
                &self.is_private,
                &self.free_agent,
                &self.team_id,
                &self.id,
            ],
        )
    }
}
