use crate::impl_string_utils;
use crate::utils::misc;
use crate::utils::misc::{ModelError, NFKind};
use image::{imageops::overlay as paste, DynamicImage, ImageResult};
use serde::{Deserialize, Serialize};
use std::backtrace::Backtrace;
use std::collections::HashMap;

impl_string_utils!();

static LOADOUT_BASE_PATH: &str = "assets/img/loadout_base.png";

#[derive(Serialize, Deserialize, Debug)]
pub struct Loadout {
    raw: RawLoadoutData,
    head: GearItem,
    clothes: GearItem,
    shoes: GearItem,
    main_wep: MainWeapon,
    sub_wep: SubWeapon,
    special_wep: SpecialWeapon,
}

impl Loadout {
    pub fn from_raw(raw: RawLoadoutData) -> Result<Loadout, ModelError> {
        let head = match GearItem::from_raw(&raw.head, "head") {
            Ok(v) => v,
            Err(e) => return Err(e),
        };
        let clothes = match GearItem::from_raw(&raw.clothes, "clothes") {
            Ok(v) => v,
            Err(e) => return Err(e),
        };
        let shoes = match GearItem::from_raw(&raw.shoes, "shoes") {
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
    #[allow(clippy::too_many_lines)] // TODO: Deal with this later
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
                for sub in &self.head.subs {
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
                for sub in &self.clothes.subs {
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
                for sub in &self.shoes.subs {
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
    pub fn raw(&self) -> &RawLoadoutData {
        &self.raw
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
    pub fn from_raw(raw: &RawGearItem, gear_type: &'static str) -> Result<GearItem, ModelError> {
        let res = match gear_type {
            "head" => {
                match misc::get_db_connection().first_exec::<_, _, mysql::Row>(
                    include_str!("../../../data/statements/gear/head/select.sql"),
                    (raw.gear_id as i32,),
                ) {
                    Ok(v) => v,
                    Err(e) => {
                        return Err(ModelError::Database(e.to_string(), Backtrace::capture()))
                    }
                }
            }
            "clothes" => {
                match misc::get_db_connection().first_exec::<_, _, mysql::Row>(
                    include_str!("../../../data/statements/gear/clothes/select.sql"),
                    (raw.gear_id as i32,),
                ) {
                    Ok(v) => v,
                    Err(e) => {
                        return Err(ModelError::Database(e.to_string(), Backtrace::capture()))
                    }
                }
            }
            "shoes" => {
                match misc::get_db_connection().first_exec::<_, _, mysql::Row>(
                    include_str!("../../../data/statements/gear/shoes/select.sql"),
                    (raw.gear_id as i32,),
                ) {
                    Ok(v) => v,
                    Err(e) => {
                        return Err(ModelError::Database(e.to_string(), Backtrace::capture()))
                    }
                }
            }
            _ => unreachable!(),
        };
        let retrow = match res {
            None => {
                return Err(ModelError::NotFound(
                    NFKind::GearItem(format!("Item: {:?} / Type: {}", raw, gear_type)),
                    Backtrace::capture(),
                ));
            }
            Some(v) => v,
        };

        let mut subs: Vec<Option<Ability>> = Vec::new();
        for sub_id in &raw.subs {
            match Ability::from_db(*sub_id as i32) {
                Ok(v) => subs.push(v),
                Err(e) => return Err(e),
            };
        }
        let local: String = retrow.get("localized_name").unwrap();
        let local: HashMap<String, Option<String>> = match serde_json::from_str(local.as_str()) {
            Ok(v) => v,
            Err(e) => return Err(ModelError::Unknown(e.to_string(), Backtrace::capture())),
        };

        Ok(GearItem {
            id: raw.gear_id as i32,
            image: retrow.get("image").unwrap(),
            localized_name: local,
            main: match Ability::from_db(raw.main as i32) {
                Ok(v) => v,
                Err(e) => return Err(e),
            },
            name: retrow.get("name").unwrap(),
            splatnet: retrow.get("splatnet").unwrap(),
            stars: retrow.get("stars").unwrap(),
            subs,
        })
    }
}

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct RawLoadoutData {
    hex: String,
    id: u32,
    set: u32,
    head: RawGearItem,
    clothes: RawGearItem,
    shoes: RawGearItem,
}

impl RawLoadoutData {
    /// Deserialize a raw base-16 encoded string into a `RawLoadout` struct
    /// ## Arguments
    /// * `dat`: The base-16 encoded string you want to deserialize. The function will verify if
    /// the string is valid before conversion.
    /// ## Return Value:
    /// * `Result<RawLoadout, ModelError>`: A result wrapping either a `RawLoadout` instance
    /// or the error that resulted.
    pub fn parse(dat: &str) -> Result<Self, ModelError> {
        if u32::from_str_radix(
            misc::hex_to_bin(&String::from(dat.slice(0..1)))
                .unwrap_or_else(|_| String::from("1"))
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
            misc::hex_to_bin(&String::from(dat.slice(1..2)))
                .unwrap_or_default()
                .as_str(),
            2,
        )
        .unwrap();
        let id = u32::from_str_radix(
            misc::hex_to_bin(&String::from(dat.slice(2..4)))
                .unwrap_or_default()
                .as_str(),
            2,
        )
        .unwrap();
        let head = RawGearItem::parse(String::from(dat.slice(4..11)).as_str()).unwrap();
        let clothes = RawGearItem::parse(String::from(dat.slice(11..18)).as_str()).unwrap();
        let shoes = RawGearItem::parse(String::from(dat.slice(18..25)).as_str()).unwrap();
        Ok(Self {
            hex: dat.to_string(),
            id,
            set,
            head,
            clothes,
            shoes,
        })
    }
    pub fn hex(&self) -> &String {
        &self.hex
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
        let bin_str = misc::hex_to_bin(&dat.slice(2..7).to_string()).unwrap();
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
        let row: mysql::Row = {
            let res = match misc::get_db_connection().first_exec(
                include_str!("../../../data/statements/gear/abilities/select.sql"),
                (id,),
            ) {
                Ok(v) => v,
                Err(e) => return Err(ModelError::Database(e.to_string(), Backtrace::capture())),
            };
            match res {
                None => return Ok(None),
                Some(v) => v,
            }
        };

        let local: String = row.get("localized_name").unwrap();
        let local: HashMap<String, Option<String>> = match serde_json::from_str(local.as_str()) {
            Ok(v) => v,
            Err(e) => return Err(ModelError::Unknown(e.to_string(), Backtrace::capture())),
        };

        Ok(Some(Ability {
            id,
            image: row.get("image").unwrap(),
            localized_name: local,
            name: row.get("name").unwrap(),
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
    pub fn from_raw(raw: &RawLoadoutData) -> Result<MainWeapon, ModelError> {
        match misc::get_db_connection().first_exec::<_, _, mysql::Row>(
            include_str!("../../../data/statements/gear/main_weapons/select.sql"),
            (raw.id, raw.set),
        ) {
            Ok(v) => {
                let retrow = match v {
                    Some(v) => v,
                    None => {
                        return Err(ModelError::NotFound(
                            NFKind::MainWeapon {
                                id: raw.id,
                                set: raw.set,
                            },
                            Backtrace::capture(),
                        ));
                    }
                };
                Ok(MainWeapon {
                    class: raw.set as i8,
                    id: retrow.get("id").unwrap(),
                    site_id: raw.id as i32,
                    name: retrow.get("name").unwrap(),
                    image: retrow.get("image").unwrap(),
                    special: match SpecialWeapon::from_db(retrow.get("special").unwrap()) {
                        Ok(v) => v,
                        Err(e) => return Err(e),
                    },
                    sub: match SubWeapon::from_db(retrow.get("sub").unwrap()) {
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
        match misc::get_db_connection().first_exec(
            include_str!("../../../data/statements/gear/sub_weapons/select.sql"),
            (&name,),
        ) {
            Ok(v) => {
                let row: mysql::Row = match v {
                    None => {
                        return Err(ModelError::NotFound(
                            NFKind::SubWeapon(format!("Sub Weapon: {}", name)),
                            Backtrace::capture(),
                        ));
                    }
                    Some(v) => v,
                };

                let local: String = row.get("localized_name").unwrap();
                let local: HashMap<String, Option<String>> =
                    match serde_json::from_str(local.as_str()) {
                        Ok(v) => v,
                        Err(e) => {
                            return Err(ModelError::Unknown(e.to_string(), Backtrace::capture()))
                        }
                    };

                Ok(SubWeapon {
                    image: row.get("image").unwrap(),
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
        match misc::get_db_connection().first_exec(
            include_str!("../../../data/statements/gear/special_weapons/select.sql"),
            (&name,),
        ) {
            Ok(v) => {
                let row: mysql::Row = match v {
                    Some(v) => v,
                    None => {
                        return Err(ModelError::NotFound(
                            NFKind::SpecialWeapon(format!("Special Weapon: {}", name)),
                            Backtrace::capture(),
                        ))
                    }
                };

                let local: String = row.get("localized_name").unwrap();
                let local: HashMap<String, Option<String>> =
                    match serde_json::from_str(local.as_str()) {
                        Ok(v) => v,
                        Err(e) => {
                            return Err(ModelError::Unknown(e.to_string(), Backtrace::capture()))
                        }
                    };

                Ok(SpecialWeapon {
                    image: row.get("image").unwrap(),
                    localized_name: local,
                    name,
                })
            }
            Err(e) => Err(ModelError::Database(e.to_string(), Backtrace::capture())),
        }
    }
}
