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
    pub fn raw(&self) -> &RawLoadout {
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
    pub fn from_raw(raw: RawGearItem, gear_type: &'static str) -> Result<GearItem, ModelError> {
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
            match Ability::from_db(*sub_id as i32) {
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
                .unwrap_or_default()
                .as_str(),
            2,
        )
        .unwrap();
        let id = u32::from_str_radix(
            misc::hex_to_bin(String::from(dat.slice(2..4)))
                .unwrap_or_default()
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
        let bin_str = misc::hex_to_bin(dat.slice(2..7).to_string()).unwrap();
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
