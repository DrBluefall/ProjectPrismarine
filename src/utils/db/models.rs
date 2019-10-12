use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use postgres::Connection;
use postgres::rows::{Row, Rows};
use postgres::Result as PgResult;
use postgres::Error;
#[macro_use]
use log;
use crate::utils::misc;
use serde_json;
use regex::Regex;

lazy_static! {
    static ref FCRE: Regex = Regex::new(r"\D").unwrap();
    static ref RANKRE: Regex = Regex::new(r"(([ABC][-+ ]?)|(S\+[0-9]?)|S|(X [0-9]{0,4}))").unwrap();
}


// Thank god for answers on the internet...
use std::ops::{Bound, RangeBounds};
use crate::utils::misc::hex_to_bin;

trait StringUtils {
    fn substring(&self, start: usize, len: usize) -> &str;
    fn slice(&self, range: impl RangeBounds<usize>) -> &str;
}
impl StringUtils for str {
    fn substring(&self, start: usize, len: usize) -> &str {
        let mut char_pos = 0;
        let mut byte_start = 0;
        let mut it = self.chars();
        loop {
            if char_pos == start { break; }
            if let Some(c) = it.next() {
                char_pos += 1;
                byte_start += c.len_utf8();
            }
            else { break; }
        }
        char_pos = 0;
        let mut byte_end = byte_start;
        loop {
            if char_pos == len { break; }
            if let Some(c) = it.next() {
                char_pos += 1;
                byte_end += c.len_utf8();
            }
            else { break; }
        }
        &self[byte_start..byte_end]
    }
    fn slice(&self, range: impl RangeBounds<usize>) -> &str {
        let start = match range.start_bound() {
            Bound::Included(bound) | Bound::Excluded(bound) => *bound,
            Bound::Unbounded => 0,
        };
        let len = match range.end_bound() {
            Bound::Included(bound) => *bound + 1,
            Bound::Excluded(bound) => *bound,
            Bound::Unbounded => self.len(),
        } - start;
        self.substring(start, len)
    }
}

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
    loadout: Option<Loadout>,
    team_id: Option<i64>,
    free_agent: Option<bool>,
    is_private: Option<bool>,
}

#[derive(Debug)]
pub struct RankSetErr(String);

impl Player {
    pub fn add_to_db(conn: &Connection, user_id: u64) -> Result<u64, Error> {
      conn.execute("
        INSERT INTO public.player_profiles(id) VALUES ($1)
        ON CONFLICT DO NOTHING;
        ", &[&(user_id as i64)])
    }
    pub fn from_db(conn: &Connection, user_id: u64) -> Option<Player> {
        
        let rows = match conn.query("SELECT * FROM public.player_profiles WHERE id = $1", &[&(user_id as i64)]) {
            Ok(v) => Some(v),
            Err(e) => {
                error!("Error in player data retrieval: {:#?}", e);
                return None;
            }
        };
        if rows.is_none() {
            return None;
        }
        let rows = rows.unwrap();
        let row = rows.get(0);
        let lv: i32 = row.get("level");
        Some(Player {
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
            loadout: None,
            team_id: row.get("team_id"),
            free_agent: row.get("free_agent"),
            is_private: row.get("is_private")
        })
    }

    pub fn id(&self) -> &i64 {&self.id}
    pub fn fc(&self) -> &String {&self.friend_code}
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
    pub fn name(&self) -> &String {&self.ign}
    pub fn set_name(&mut self, name: String) -> Result<(), ()> {
        if name.len() > 10 || name.len() < 1 {
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

    pub fn set_rank(&mut self, mode: String, rank: String) -> Result<(), RankSetErr> {

        if !RANKRE.is_match(rank.as_str()) {
            return Err(RankSetErr(format!("Invalid Rank: {}", rank.as_str())))
        }

        match mode.as_str() {
            "sz" | "splat_zones" | "sz_rank" => self.sz = "sz".to_string(),
            "tc" | "tower_control" | "tc_rank" => self.tc = "tc".to_string(),
            "rm" | "rainmaker" | "rm_rank" => self.rm = "rm".to_string(),
            "cb" | "clam_blitz" | "cb_rank" => self.cb = "cb".to_string(),
            "sr" | "salmon_run" | "sr_rank" => self.sr = "sr".to_string(),
            _ => return Err(RankSetErr(format!("Invalid Mode: {}", mode.as_str()))),
        }
        Ok(())
    }

    pub fn pos(&self) -> &'static str {
        misc::pos_map().get(&self.position).unwrap_or(&"Invalid")
    }

    pub fn set_pos(&mut self, pos_int: i16) -> Result<(), ()> {
        let pos_map = misc::pos_map();
        let mut in_map = false;
        for key in pos_map.keys() {
            if key == &pos_int {
                self.position = pos_int;
                return Ok(());
            }
        }
        Err(())
    }


    pub fn loadout(&self) -> &Option<Loadout> {&self.loadout}
    pub fn team_id(&self) -> &Option<i64> {&self.team_id}
    pub fn is_free_agent(&self) -> &Option<bool> {&self.free_agent}
    pub fn is_private(&self) -> &Option<bool> {&self.is_private}
    pub fn update(&self, conn: &Connection) -> Result<u64, Error> {
        let ld_raw: Option<&RawLoadout> = match self.loadout() {
            Some(loadout) => Some(&loadout.raw),
            None => None
        };
        conn.execute(
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
    is_private = $12
WHERE id = $13;
                    ",
            &[
                &self.friend_code,
                &self.ign,
                &self.level,
                &self.sz, &self.tc, &self.rm, &self.cb, &self.sr,
                &self.position,
                &serde_json::to_string_pretty(&ld_raw).unwrap_or(String::from("{}")),
                &self.team_id,
                &self.is_private,
                &self.id
            ]
        )
    }
}

#[derive(Serialize, Deserialize, Debug)]
pub struct Loadout {
    raw: RawLoadout,
    head: GearItem,
    clothes: GearItem,
    shoes: GearItem,
    main_wep: MainWeapon,
    sub_wep: SubWeapon,
    special_wep: SpecialWeapon,
}

#[derive(Serialize, Deserialize, Debug)]
struct RawLoadout {
    id: u32,
    set: u32,
    head: RawGearItem,
    clothes: RawGearItem,
    shoes: RawGearItem,
}

impl RawLoadout {
    /// Deserialize a raw base-16 encoded string into a RawLoadout struct
    /// ## Arguments
    /// * `dat`: The base-16 encoded string you want to deserialize. The function will verify if
    /// the string is valid before conversion.
    /// ## Return Value:
    /// * `Result<RawLoadout, serde_json::Error>`: A result wrapping either a RawLoadout instance
    /// or the error that resulted.
    pub fn parse(dat: &str) -> Option<RawLoadout> {
        if u32::from_str_radix(
            misc::hex_to_bin(
                String::from(
                    dat.slice(0..1)
                )
            ).unwrap_or(String::from("1")).as_str(), 2).unwrap() != 0 {
            return None;
        }
        let set = u32::from_str_radix(
            misc::hex_to_bin(
                String::from(
                    dat.slice(1..2)
                )
            ).unwrap_or(String::new()).as_str(), 2).unwrap();
        let id =  u32::from_str_radix(misc::hex_to_bin(String::from(dat.slice(2..4)))
                                               .unwrap_or(String::new()).as_str(), 2).unwrap();
        let head = RawGearItem::parse(String::from(dat.slice(4..11))
                                               .as_str()).unwrap();
        let clothes = RawGearItem::parse(String::from(dat.slice(11..18))
                                               .as_str()).unwrap();
        let shoes = RawGearItem::parse(String::from(dat.slice(18..25))
                                               .as_str()).unwrap();
        Some(RawLoadout { id, set, head, clothes, shoes })
    }
}

#[derive(Serialize, Deserialize, Debug)]
struct RawGearItem {
    gear_id: u32,
    main: u32,
    subs: Vec<u32>,
}

impl RawGearItem {
    pub fn parse(dat: &str) -> Option<RawGearItem> {
        let gear_id = u32::from_str_radix(dat.slice(0..2), 16).unwrap();
        let bin_str = hex_to_bin(dat.slice(2..7).to_string()).unwrap();
        let mut subs: Vec<u32> = Vec::new();
        let main = u32::from_str_radix(bin_str.slice(0..5), 2).unwrap();
        subs.push(
            u32::from_str_radix(bin_str.slice(5..10), 2).unwrap()
        );
        subs.push(
            u32::from_str_radix(bin_str.slice(10..15), 2).unwrap()
        );
        subs.push(
            u32::from_str_radix(bin_str.slice(15..20), 2).unwrap()
        );

        Some(RawGearItem {gear_id, main, subs})
    }
}

#[derive(Serialize, Deserialize, Debug)]
struct Ability {
    id: u32,
    image: String,
    localized_name: HashMap<String, String>,
    name: String,
}

#[derive(Serialize, Deserialize, Debug)]
struct GearItem {
    id: u32,
    image: String,
    localized_name: HashMap<String, String>,
    main: Option<Ability>,
    name: String,
    splatnet: u32,
    stars: u8,
    subs: Vec<Option<Ability>>,
}

#[derive(Serialize, Deserialize, Debug)]
struct MainWeapon {
    class: u8,
    id: u32,
    site_id: u32,
    name: String,
    image: String,
    special: SubWeapon,
    sub: SpecialWeapon,
}

#[derive(Serialize, Deserialize, Debug)]
struct SubWeapon {
    image: String,
    localized_name: HashMap<String, String>,
    name: String,
}
#[derive(Serialize, Deserialize, Debug)]
struct SpecialWeapon {
    image: String,
    localized_name: HashMap<String, String>,
    name: String,
}

#[cfg(test)]
mod tests {
    use super::*;
    use dotenv::dotenv;
    use postgres::{Connection, TlsMode};

    fn get_conn() -> Connection {
        dotenv().ok();
        Connection::connect(match std::env::var("PRISBOT_DATABASE") {
            Ok(v) => v,
            Err(e) => panic!("{:#?}", e),
        }, TlsMode::None).unwrap()
    }

    #[test]
    fn add() {
        Player::add_to_db(&get_conn(), 1).unwrap();
    }

    #[test]
    fn from() {
        Player::from_db(&get_conn(), 1).unwrap();
    }

    #[test]
    fn up() {
        let mut player = Player::from_db(&get_conn(), 1).unwrap();
        player.level = 42;
        player.update(&get_conn()).unwrap();
    }

    #[test]
    fn raw_deserialize() { // NOTE: Run this test w/ `--nocapture` to see the output
        let test_str = "080311694ac62098ce6e214e5";
        let out = RawLoadout::parse(test_str);
        println!("{:#?}", out);
        // Output should look something like this (the JSON from the Python implementation,
        // pretty printed):
        // {'clothes': {'gear_id': 98, 'main': 1, 'subs': [6, 6, 14]},
        // 'head': {'gear_id': 17, 'main': 13, 'subs': [5, 5, 12]},
        // 'id': 3,
        // 'set': 8,
        // 'shoes': {'gear_id': 110, 'main': 4, 'subs': [5, 7, 5]}}
        println!("{}", serde_json::to_string_pretty(&out).unwrap().as_str());
    }

    #[test]
    fn re_fc() {
        let mut player = Player::from_db(&get_conn(), 1).unwrap();
        // Test Cases:
        //a
        //k
        //0000-0000-0000
        //123412341234
        //1234t1234t1234t
        //aoeuaoeuaoeu12348888aaaa888a8
        //1234-1234-122-3
        //12341234123
        //412341299999
        //0 0 0 0 0 0 0 0 0 0 0 9
        //' or 1=1 #
        //1234 1234 4311
        player.set_fc("a").unwrap_err();
        player.set_fc("k").unwrap_err();
        player.set_fc("0000-0000-0000").unwrap();
        player.set_fc("123412341234").unwrap();
        player.set_fc("1234t1234t1234t").unwrap();
        player.set_fc("aoeuaoeuaoeu12348888aaaa888a8").unwrap();
        player.set_fc("1234-1234-122-3").unwrap();
        player.set_fc("12341234123").unwrap_err();
        player.set_fc("412341299999").unwrap();
        player.set_fc("0 0 0 0 0 0 0 0 0 0 0 9").unwrap();
        player.set_fc("' or 1=1 #").unwrap_err();
        player.set_fc("1234 1234 4311").unwrap();
    }

    #[test]
    fn pos_setting() {
        let mut player = Player::from_db(&get_conn(), 1).unwrap();
        player.set_pos(0i16).unwrap();
        player.set_pos(1i16).unwrap();
        player.set_pos(2i16).unwrap();
        player.set_pos(3i16).unwrap();
        player.set_pos(4i16).unwrap();
        player.set_pos(5i16).unwrap_err();
    }

    #[test]
    fn rank_setting() {
        let mut player = Player::from_db(&get_conn(), 1).unwrap();
        let test_cases = vec![ // A set of 'possible' rank test cases.
            "C-", "C", "C+",
            "b-", "b", "b+",
            "A-", "A", "A+",
            "S", "S+", "S+3", "S+7",
            "X", "X 2500", "X 30000", "X2000"
        ];
        let mut failed_cases: Vec<(&&str, RankSetErr)> = Vec::new();

        for case in test_cases.iter() {
            match player.set_rank("sz".to_string(), case.to_string()) {
                Ok(_) => (),
                Err(e) => failed_cases.push((case, e)),
            }
        }
        println!("{:#?}", failed_cases);
    }
}
