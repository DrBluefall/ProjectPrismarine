use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use postgres::Connection;
use postgres::rows::{Row, Rows};
use postgres::Result as PgResult;
#[macro_use]
use log;
use crate::utils::misc::pos_map;
use serde_json;

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

impl Player {
    pub fn add_to_db(conn: &Connection, user_id: u64) -> Result<()> {
        let _ = conn.execute("
        INSERT INTO public.player_profiles(id) VALUES ($1)
        ON CONFLICT DO NOTHING;
        ", &[&(user_id as i64)]);
        Ok(())
    }
    pub fn from_db<'a>(conn: &Connection, user_id: u64) -> Option<Player> {
        let mut rows: Option<Rows> = None;
        rows = match conn.query("SELECT * FROM public.player_profiles WHERE id = $1", &[&(user_id as i64)]) {
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
    pub fn ranks(&self) -> HashMap<&'static str, &String> {
        let mut hm = HashMap::new();
        hm.insert("Splat Zones", &self.sz);
        hm.insert("Tower Control", &self.tc);
        hm.insert("Rainmaker", &self.rm);
        hm.insert("Clam Blitz", &self.cb);
        hm.insert("Salmon Run", &self.sr);
        hm
    }
    pub fn pos(&self, pos_int: i8) -> &'static str {
        pos_map().get(&pos_int).unwrap_or(&"Invalid")
    }
    pub fn loadout(&self) -> &Option<Loadout> {&self.loadout}
    pub fn team_id(&self) -> &Option<i64> {&self.team_id}
    pub fn is_free_agent(&self) -> &Option<bool> {&self.free_agent}
    pub fn is_private(&self) -> &Option<bool> {&self.is_private}
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
    pub fn deserialize(dat: &str) -> Result<RawLoadout, serde_json::Error> {
       serde_json::from_str::<RawLoadout>(dat)
    }
}

#[derive(Serialize, Deserialize, Debug)]
struct RawGearItem {
    gear_id: u32,
    main: u32,
    subs: Vec<u32>,
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
}
