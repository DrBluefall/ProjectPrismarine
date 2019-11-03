use postgres::Connection;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::convert::AsRef;
use crate::utils::misc;
use image::imageops::overlay as paste;
use image::{DynamicImage, ImageResult};
use postgres::Error;
use regex::Regex;
use serde_json;
use std::backtrace::Backtrace;
use crate::utils::misc::hex_to_bin;

lazy_static! {
    static ref FCRE: Regex = Regex::new(r"\D").unwrap();
    static ref RANKRE: Regex = Regex::new(r"(([ABC][-+ ]?)|(S\+[0-9]?)|S|(X [0-9]{0,4}))").unwrap();
}

static LOADOUT_BASE_PATH: &str = "assets/img/loadout_base.png";

// Thank god for answers on the internet...
use std::ops::{Bound, RangeBounds};

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
            if char_pos == start {
                break;
            }
            if let Some(c) = it.next() {
                char_pos += 1;
                byte_start += c.len_utf8();
            } else {
                break;
            }
        }
        char_pos = 0;
        let mut byte_end = byte_start;
        loop {
            if char_pos == len {
                break;
            }
            if let Some(c) = it.next() {
                char_pos += 1;
                byte_end += c.len_utf8();
            } else {
                break;
            }
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
    loadout: Loadout,
    team_id: Option<i64>,
    free_agent: Option<bool>,
    is_private: Option<bool>,
}

#[derive(Debug)]
pub enum ModelError {
    Database(String, Backtrace),
    NotFound(NFKind, Backtrace),
    InvalidParameter(String),
    Unknown(String, Backtrace),
}

impl AsRef<Self> for ModelError {
    fn as_ref(&self) -> &Self {
        self
    }
}

#[derive(Debug)]
pub enum NFKind {
    Player(u64),
    Loadout,
    GearItem(String),
    Ability,
    MainWeapon { id: u32, set: u32 },
    SubWeapon(String),
    SpecialWeapon(String),
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
        let row = rows.get(0);
        let ldink_hex: String = row.get("loadout");
        let ld = RawLoadout::parse(ldink_hex.as_str());
        let mut ld_fin: Option<Loadout> = None;
        if ld.is_ok() {
            ld_fin = match Loadout::from_raw(ld.unwrap()) {
                Ok(v) => Some(v),
                Err(e) => return Err(e),
            }
        } else {
            return Err(ld.unwrap_err());
        }

        let lv: i32 = row.get("level");
        let dt: String = row.get("loadout");
        let loadout = match Loadout::from_raw(
                match RawLoadout::parse(dt.as_str()) {
                    Ok(v) => v,
                    Err(e) => return Err(e),
                },
            ) {
            Ok(v) => v,
            Err(e) => return Err(e)
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

    pub fn set_rank(&mut self, mode: String, rank: String) -> Result<(), ModelError> {
        if !RANKRE.is_match(rank.as_str()) {
            return Err(ModelError::InvalidParameter(format!(
                "Invalid Rank: {}",
                rank.as_str()
            )));
        }

        match mode.as_str() {
            "sz" | "splat_zones" | "sz_rank" => self.sz = "sz".to_string(),
            "tc" | "tower_control" | "tc_rank" => self.tc = "tc".to_string(),
            "rm" | "rainmaker" | "rm_rank" => self.rm = "rm".to_string(),
            "cb" | "clam_blitz" | "cb_rank" => self.cb = "cb".to_string(),
            "sr" | "salmon_run" | "sr_rank" => self.sr = "sr".to_string(),
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

    pub fn loadout(&self) -> &Loadout {
        &self.loadout
    }
    pub fn team_id(&self) -> &Option<i64> {
        &self.team_id
    }
    pub fn is_free_agent(&self) -> &Option<bool> {
        &self.free_agent
    }
    pub fn is_private(&self) -> &Option<bool> {
        &self.is_private
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
    is_private = $12
WHERE id = $13;
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
                &self.loadout.raw.hex,
                &self.team_id,
                &self.is_private,
                &self.id,
            ],
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

impl Loadout {
    pub fn from_raw(raw: RawLoadout) -> Result<Loadout, ModelError> {
        let head = match GearItem::from_raw(raw.clone().head, "head") {
            Ok(v) => v,
            Err(e) => return Err(e),
        };
        let clothes = match GearItem::from_raw(raw.clone().clothes, "clothes") {
            Ok(v) => v,
            Err(e) => return Err(e),
        };
        let shoes = match GearItem::from_raw(raw.clone().shoes, "shoes") {
            Ok(v) => v,
            Err(e) => return Err(e),
        };

        let kit = match MainWeapon::from_raw(&raw) {
            Ok(v) => v,
            Err(e) => return Err(e),
        };
        let sub = kit.clone().sub;
        let special = kit.clone().special;

        Ok(Loadout {
            raw,
            head,
            clothes,
            shoes,
            main_wep: kit,
            sub_wep: sub,
            special_wep: special,
        })
    }
    pub fn to_img(&self) -> ImageResult<DynamicImage> {
        let mut base = match image::open(LOADOUT_BASE_PATH) {
            Ok(v) => v,
            Err(e) => return Err(e),
        };
        let coords = misc::GearCoords::get();
        {
            // Headgear pasting
            let gear_coords = if let Some(v) = coords.get("head") {
                v
            } else {
                unreachable!()
            };
            let gear_img = image::open(self.head.image.clone().slice(3..))
                .unwrap()
                .resize(96, 96, image::FilterType::Lanczos3);
            let sub_imgs = {
                let mut vec: Vec<DynamicImage> = Vec::new();
                for sub in self.head.subs.iter() {
                    vec.push(match sub {
                        None => image::open("assets/img/skills/Unknown.png")
                            .unwrap()
                            .resize(24, 24, image::FilterType::Lanczos3),
                        Some(v) => image::open(v.image.slice(3..)).unwrap().resize(
                            24,
                            24,
                            image::FilterType::Lanczos3,
                        ),
                    });
                }
                vec
            };
            let sub_imgs = sub_imgs.iter();
            let main_img = match &self.head.main {
                Some(v) => image::open(v.image.slice(3..)).unwrap().resize(
                    32,
                    32,
                    image::FilterType::Lanczos3,
                ),
                &None => image::open("assets/img/skills/Unknown.png")
                    .unwrap()
                    .resize(32, 32, image::FilterType::Lanczos3),
            };
            for sub in sub_imgs.zip(gear_coords.subs.iter()) {
                paste(&mut base, sub.0, (sub.1).0, (sub.1).1);
            }
            paste(&mut base, &main_img, gear_coords.main.0, gear_coords.main.1);
            paste(&mut base, &gear_img, gear_coords.gear.0, gear_coords.gear.1);
        }
        {
            // Clothing pasting
            let gear_coords = if let Some(v) = coords.get("clothes") {
                v
            } else {
                unreachable!()
            };
            let gear_img = image::open(self.clothes.image.clone().slice(3..))
                .unwrap()
                .resize(96, 96, image::FilterType::Lanczos3);
            let sub_imgs = {
                let mut vec: Vec<DynamicImage> = Vec::new();
                for sub in self.clothes.subs.iter() {
                    vec.push(match sub {
                        None => image::open("assets/img/skills/Unknown.png")
                            .unwrap()
                            .resize(24, 24, image::FilterType::Lanczos3),
                        Some(v) => image::open(v.image.slice(3..)).unwrap().resize(
                            24,
                            24,
                            image::FilterType::Lanczos3,
                        ),
                    });
                }
                vec
            };
            let sub_imgs = sub_imgs.iter();
            let main_img = match &self.clothes.main {
                Some(v) => image::open(v.image.slice(3..)).unwrap().resize(
                    32,
                    32,
                    image::FilterType::Lanczos3,
                ),
                &None => image::open("assets/img/skills/Unknown.png")
                    .unwrap()
                    .resize(32, 32, image::FilterType::Lanczos3),
            };
            for sub in sub_imgs.zip(gear_coords.subs.iter()) {
                paste(&mut base, sub.0, (sub.1).0, (sub.1).1);
            }
            paste(&mut base, &main_img, gear_coords.main.0, gear_coords.main.1);
            paste(&mut base, &gear_img, gear_coords.gear.0, gear_coords.gear.1);
        }
        {
            // Shoe pasting
            let gear_coords = if let Some(v) = coords.get("shoes") {
                v
            } else {
                unreachable!()
            };
            let gear_img = image::open(self.shoes.image.clone().slice(3..))
                .unwrap()
                .resize(96, 96, image::FilterType::Lanczos3);
            let sub_imgs = {
                let mut vec: Vec<DynamicImage> = Vec::new();
                for sub in self.shoes.subs.iter() {
                    vec.push(match sub {
                        None => image::open("assets/img/skills/Unknown.png")
                            .unwrap()
                            .resize(24, 24, image::FilterType::Lanczos3),
                        Some(v) => image::open(v.image.slice(3..)).unwrap().resize(
                            24,
                            24,
                            image::FilterType::Lanczos3,
                        ),
                    });
                }
                vec
            };
            let sub_imgs = sub_imgs.iter();
            let main_img = match &self.shoes.main {
                Some(v) => image::open(v.image.slice(3..)).unwrap().resize(
                    32,
                    32,
                    image::FilterType::Lanczos3,
                ),
                &None => image::open("assets/img/skills/Unknown.png")
                    .unwrap()
                    .resize(32, 32, image::FilterType::Lanczos3),
            };
            for sub in sub_imgs.zip(gear_coords.subs.iter()) {
                paste(&mut base, sub.0, (sub.1).0, (sub.1).1);
            }
            paste(&mut base, &main_img, gear_coords.main.0, gear_coords.main.1);
            paste(&mut base, &gear_img, gear_coords.gear.0, gear_coords.gear.1);
        }
        {
            // Weapon pasting
            let wep_coords = misc::WepCoords::get();
            let main_wep_img = image::open(self.main_wep.image.slice(3..)).unwrap().resize(
                96,
                96,
                image::FilterType::Lanczos3,
            );
            let sub_wep_img = image::open(self.sub_wep.image.slice(3..)).unwrap().resize(
                32,
                32,
                image::FilterType::Lanczos3,
            );
            let special_wep_img = image::open(self.special_wep.image.slice(3..))
                .unwrap()
                .resize(32, 32, image::FilterType::Lanczos3);
            paste(
                &mut base,
                &main_wep_img,
                wep_coords.main.0,
                wep_coords.main.1,
            );
            paste(&mut base, &sub_wep_img, wep_coords.sub.0, wep_coords.sub.1);
            paste(
                &mut base,
                &special_wep_img,
                wep_coords.special.0,
                wep_coords.special.1,
            );
        }

        Ok(base)
    }
}

#[derive(Serialize, Deserialize, Debug)]
pub struct GearItem {
    id: i32,
    image: String,
    localized_name: HashMap<String, Option<String>>,
    main: Option<Ability>,
    name: String,
    splatnet: i32,
    stars: i32,
    subs: Vec<Option<Ability>>,
}

impl GearItem {
    pub fn from_raw(
        raw: RawGearItem,
        gear_type: &'static str,
    ) -> Result<GearItem, ModelError> {
        let res = match gear_type {
            "head" => {
                match misc::get_db_connection().query(
                    "SELECT * FROM public.headgear WHERE id = $1 LIMIT 1;",
                    &[&(raw.gear_id as i32)],
                ) {
                    Ok(v) => v,
                    Err(e) => {
                        return Err(ModelError::Database(e.to_string(), Backtrace::capture()))
                    }
                }
            }
            "clothes" => {
                match misc::get_db_connection().query(
                    "SELECT * FROM public.clothing WHERE id = $1 LIMIT 1;",
                    &[&(raw.gear_id as i32)],
                ) {
                    Ok(v) => v,
                    Err(e) => {
                        return Err(ModelError::Database(e.to_string(), Backtrace::capture()))
                    }
                }
            }
            "shoes" => {
                match misc::get_db_connection().query(
                    "SELECT * FROM public.shoes WHERE id = $1 LIMIT 1;",
                    &[&(raw.gear_id as i32)],
                ) {
                    Ok(v) => v,
                    Err(e) => {
                        return Err(ModelError::Database(e.to_string(), Backtrace::capture()))
                    }
                }
            }
            _ => unreachable!(),
        };

        if res.is_empty() {
            return Err(ModelError::NotFound(
                NFKind::GearItem(format!("Item: {:?} / Type: {}", raw, gear_type)),
                Backtrace::capture(),
            ));
        }
        let retrow = res.get(0);

        let mut subs: Vec<Option<Ability>> = Vec::new();
        for sub_id in raw.subs.iter() {
            let sub = match Ability::from_db(*sub_id as i32) {
                Ok(v) => subs.push(v),
                Err(e) => return Err(e),
            };
        }
        let local: String = retrow.get("localized_name");
        let local: HashMap<String, Option<String>> = match serde_json::from_str(local.as_str()) {
            Ok(v) => v,
            Err(e) => return Err(ModelError::Unknown(e.to_string(), Backtrace::capture())),
        };

        Ok(GearItem {
            id: raw.gear_id as i32,
            image: retrow.get("image"),
            localized_name: local,
            main: match Ability::from_db(raw.main as i32) {
                Ok(v) => v,
                Err(e) => return Err(e),
            },
            name: retrow.get("name"),
            splatnet: retrow.get("splatnet"),
            stars: retrow.get("stars"),
            subs,
        })
    }
}

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct RawLoadout {
    hex: String,
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
    /// * `Result<RawLoadout, ModelError>`: A result wrapping either a RawLoadout instance
    /// or the error that resulted.
    pub fn parse(dat: &str) -> Result<RawLoadout, ModelError> {
        if u32::from_str_radix(
            misc::hex_to_bin(String::from(dat.slice(0..1)))
                .unwrap_or(String::from("1"))
                .as_str(),
            2,
        )
        .unwrap()
            != 0
        {
            return Err(ModelError::InvalidParameter(
                "Invalid hex string".to_string(),
            ));
        }
        let set = u32::from_str_radix(
            misc::hex_to_bin(String::from(dat.slice(1..2)))
                .unwrap_or(String::new())
                .as_str(),
            2,
        )
        .unwrap();
        let id = u32::from_str_radix(
            misc::hex_to_bin(String::from(dat.slice(2..4)))
                .unwrap_or(String::new())
                .as_str(),
            2,
        )
        .unwrap();
        let head = RawGearItem::parse(String::from(dat.slice(4..11)).as_str()).unwrap();
        let clothes = RawGearItem::parse(String::from(dat.slice(11..18)).as_str()).unwrap();
        let shoes = RawGearItem::parse(String::from(dat.slice(18..25)).as_str()).unwrap();
        Ok(RawLoadout {
            hex: dat.to_string(),
            id,
            set,
            head,
            clothes,
            shoes,
        })
    }
}

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct RawGearItem {
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
        subs.push(u32::from_str_radix(bin_str.slice(5..10), 2).unwrap());
        subs.push(u32::from_str_radix(bin_str.slice(10..15), 2).unwrap());
        subs.push(u32::from_str_radix(bin_str.slice(15..20), 2).unwrap());

        Some(RawGearItem {
            gear_id,
            main,
            subs,
        })
    }
}

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct Ability {
    id: i32,
    image: String,
    localized_name: HashMap<String, Option<String>>,
    name: String,
}

impl Ability {
    pub fn from_db(id: i32) -> Result<Option<Ability>, ModelError> {
        let r = {
            let res = match misc::get_db_connection().query(
                "SELECT * FROM public.abilities WHERE id = $1 LIMIT 1;",
                &[&id],
            ) {
                Ok(v) => v,
                Err(e) => return Err(ModelError::Database(e.to_string(), Backtrace::capture())),
            };
            if res.is_empty() {
                return Ok(None);
            }
            res
        };
        let row = r.get(0);

        let local: String = row.get("localized_name");
        let local: HashMap<String, Option<String>> = match serde_json::from_str(local.as_str()) {
            Ok(v) => v,
            Err(e) => return Err(ModelError::Unknown(e.to_string(), Backtrace::capture())),
        };

        Ok(Some(Ability {
            id,
            image: row.get("image"),
            localized_name: local,
            name: row.get("name"),
        }))
    }
}

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct MainWeapon {
    class: i8,
    id: i32,
    site_id: i32,
    name: String,
    image: String,
    special: SpecialWeapon,
    sub: SubWeapon,
}

impl MainWeapon {
    pub fn from_raw(raw: &RawLoadout) -> Result<MainWeapon, ModelError> {
        match misc::get_db_connection().query(
            "SELECT * FROM public.main_weapons WHERE site_id = $1 AND class = $2;",
            &[&(raw.id as i32), &(raw.set as i32)],
        ) {
            Ok(v) => {
                if v.is_empty() {
                    return Err(ModelError::NotFound(
                        NFKind::MainWeapon {
                            id: raw.id,
                            set: raw.set,
                        },
                        Backtrace::capture(),
                    ));
                }
                let retrow = v.get(0);
                Ok(MainWeapon {
                    class: raw.set as i8,
                    id: retrow.get("id"),
                    site_id: raw.id as i32,
                    name: retrow.get("name"),
                    image: retrow.get("image"),
                    special: match SpecialWeapon::from_db(retrow.get("special")) {
                        Ok(v) => v,
                        Err(e) => return Err(e),
                    },
                    sub: match SubWeapon::from_db(retrow.get("sub")) {
                        Ok(v) => v,
                        Err(e) => return Err(e),
                    },
                })
            }
            Err(e) => Err(ModelError::Database(e.to_string(), Backtrace::capture())),
        }
    }
}

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct SubWeapon {
    image: String,
    localized_name: HashMap<String, Option<String>>,
    name: String,
}

impl SubWeapon {
    pub fn from_db(name: String) -> Result<SubWeapon, ModelError> {
        match misc::get_db_connection().query(
            "SELECT * FROM public.sub_weapons WHERE name = $1;",
            &[&name],
        ) {
            Ok(v) => {
                if v.is_empty() {
                    return Err(ModelError::NotFound(
                        NFKind::SubWeapon(format!("Sub Weapon: {}", name)),
                        Backtrace::capture(),
                    ));
                }
                let row = v.get(0);

                let local: String = row.get("localized_name");
                let local: HashMap<String, Option<String>> =
                    match serde_json::from_str(local.as_str()) {
                        Ok(v) => v,
                        Err(e) => {
                            return Err(ModelError::Unknown(e.to_string(), Backtrace::capture()))
                        }
                    };

                Ok(SubWeapon {
                    image: row.get("image"),
                    localized_name: local,
                    name,
                })
            }
            Err(e) => Err(ModelError::Database(e.to_string(), Backtrace::capture())),
        }
    }
}

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct SpecialWeapon {
    image: String,
    localized_name: HashMap<String, Option<String>>,
    name: String,
}

impl SpecialWeapon {
    pub fn from_db(name: String) -> Result<SpecialWeapon, ModelError> {
        match misc::get_db_connection().query(
            "SELECT * FROM public.special_weapons WHERE name = $1;",
            &[&name],
        ) {
            Ok(v) => {
                if v.is_empty() {
                    return Err(ModelError::NotFound(
                        NFKind::SpecialWeapon(format!("Special Weapon: {}", name)),
                        Backtrace::capture(),
                    ));
                }
                let row = v.get(0);

                let local: String = row.get("localized_name");
                let local: HashMap<String, Option<String>> =
                    match serde_json::from_str(local.as_str()) {
                        Ok(v) => v,
                        Err(e) => {
                            return Err(ModelError::Unknown(e.to_string(), Backtrace::capture()))
                        }
                    };

                Ok(SpecialWeapon {
                    image: row.get("image"),
                    localized_name: local,
                    name,
                })
            }
            Err(e) => Err(ModelError::Database(e.to_string(), Backtrace::capture())),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use dotenv::dotenv;
    use postgres::{Connection, TlsMode};

    fn get_conn() -> Connection {
        dotenv().ok();
        Connection::connect(
            match std::env::var("PRISBOT_DATABASE") {
                Ok(v) => v,
                Err(e) => panic!("{:#?}", e),
            },
            TlsMode::None,
        )
        .unwrap()
    }

    #[test]
    fn add() {
        Player::add_to_db(1).unwrap();
    }

    #[test]
    fn from() {
        Player::from_db(1).unwrap();
    }

    #[test]
    fn up() {
        let mut player = Player::from_db(1).unwrap();
        player.level = 42;
        player.update().unwrap();
    }

    #[test]
    fn raw_deserialize() {
        // NOTE: Run this test w/ `--nocapture` to see the output
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
        if let Err(e) = out {
            panic!("Deserialization Failed {:?}", e)
        }
        println!(
            "{}",
            serde_json::to_string_pretty(&(out.unwrap()))
                .unwrap()
                .as_str()
        );
    }

    #[test]
    fn re_fc() {
        let mut player = Player::from_db(1).unwrap();
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
        let mut player = Player::from_db(1).unwrap();
        player.set_pos(0i16).unwrap();
        player.set_pos(1i16).unwrap();
        player.set_pos(2i16).unwrap();
        player.set_pos(3i16).unwrap();
        player.set_pos(4i16).unwrap();
        player.set_pos(5i16).unwrap_err();
    }

    #[test]
    fn rank_setting() {
        let mut player = Player::from_db(1).unwrap();
        let test_cases = vec![
            // A set of 'possible' rank test cases.
            "C-", "C", "C+", "b-", "b", "b+", "A-", "A", "A+", "S", "S+", "S+3", "S+7", "X",
            "X 2500", "X 30000", "X2000",
        ];
        let mut failed_cases: Vec<(&&str, ModelError)> = Vec::new();

        for case in test_cases.iter() {
            match player.set_rank("sz".to_string(), case.to_string()) {
                Ok(_) => (),
                Err(e) => failed_cases.push((case, e)),
            }
        }
        println!("{:#?}", failed_cases);
    }

    #[test]
    fn full_deserial() {
        let test_ld = "0000000000000000000000000";
        let raw = RawLoadout::parse(test_ld).unwrap();
        println!("{:#?}", Loadout::from_raw(raw).unwrap());
    }

    #[test]
    fn image_gen() {
        let test_ld = "060314598cc73210846e214e5";
        let raw = RawLoadout::parse(test_ld).unwrap();
        let ld = Loadout::from_raw(raw).unwrap();
        ld.to_img().unwrap().save("ld_test.png").unwrap();
    }
}
