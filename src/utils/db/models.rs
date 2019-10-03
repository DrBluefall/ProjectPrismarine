use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Serialize, Deserialize, Debug)]
pub struct Player<'a> {
    pub id: u64,
    in_game_name: String,
    friend_code: String,
    pub level: u32,
    sz: String,
    tc: String,
    rm: String,
    cb: String,
    sr: String,
    position: &'a str,
    team_id: Option<u64>,
    free_agent: Option<bool>,
    is_private: Option<bool>,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct Loadout {
    raw: RawLoadout,
    head: GearItem,
    clothes: GearItem,
    shoes: GearItem,
    main_wep: MainWeapon,
    sub_wep: SubSpecial,
    special_wep: SubSpecial,
}

#[derive(Serialize, Deserialize, Debug)]
struct RawLoadout {
    id: u32,
    set: u32,
    head: RawGearItem,
    clothes: RawGearItem,
    shoes: RawGearItem,
}

#[derive(Serialize, Deserialize, Debug)]
enum RawGearItem {
    Head {
        gear_id: u32,
        main: u32,
        subs: Vec<u32>,
    },
    Clothes {
        gear_id: u32,
        main: u32,
        subs: Vec<u32>,
    },
    Shoes {
        gear_id: u32,
        main: u32,
        subs: Vec<u32>,
    },
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
    special: SubSpecial,
    sub: SubSpecial,
}

#[derive(Serialize, Deserialize, Debug)]
enum SubSpecial {
    SubWeapon {
        image: String,
        localized_name: HashMap<String, String>,
        name: String,
    },
    SpecialWeapon {
        image: String,
        localized_name: HashMap<String, String>,
        name: String,
    },
}
