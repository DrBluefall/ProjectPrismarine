use mysql::Conn;
use std::backtrace::Backtrace;
use std::collections::HashMap;

lazy_static! {
    static ref DATABASE_URL: String = std::env::var("PRISBOT_DATABASE").unwrap();
}

pub fn pos_map() -> HashMap<i16, &'static str> {
    let mut hm: HashMap<i16, &'static str> = HashMap::new();
    hm.insert(0_i16, "Not Set");
    hm.insert(1_i16, "Frontline");
    hm.insert(2_i16, "Midline");
    hm.insert(3_i16, "Backline");
    hm.insert(4_i16, "Flex");
    hm
}

#[derive(Debug)]
pub struct HexError;

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
    // Loadout, -- Never constructed, will keep though for later use
    GearItem(String),
    // Ability, -- same case as loadout
    MainWeapon { id: u32, set: u32 },
    SubWeapon(String),
    SpecialWeapon(String),
    Team(u64),
    // Invite(i64), -- same case as others
}

pub fn hex_to_bin(input: &str) -> Result<String, HexError> {
    let mut result = String::new();
    let mut map: HashMap<char, &str> = HashMap::new();
    map.insert('0', "0000");
    map.insert('1', "0001");
    map.insert('2', "0010");
    map.insert('3', "0011");
    map.insert('4', "0100");
    map.insert('5', "0101");
    map.insert('6', "0110");
    map.insert('7', "0111");
    map.insert('8', "1000");
    map.insert('9', "1001");
    map.insert('a', "1010");
    map.insert('b', "1011");
    map.insert('c', "1100");
    map.insert('d', "1101");
    map.insert('e', "1110");
    map.insert('f', "1111");
    map.insert('A', "1010");
    map.insert('B', "1011");
    map.insert('C', "1100");
    map.insert('D', "1101");
    map.insert('E', "1110");
    map.insert('F', "1111");

    for value in input.chars() {
        match map.get(&value) {
            None => return Err(HexError),
            Some(v) => result.push_str(v),
        }
    }
    Ok(result)
}

pub struct GearCoords {
    pub gear: (u32, u32),
    pub main: (u32, u32),
    pub subs: [(u32, u32); 3],
}
pub struct WepCoords {
    pub main: (u32, u32),
    pub sub: (u32, u32),
    pub special: (u32, u32),
}

impl GearCoords {
    pub fn get() -> HashMap<&'static str, Self> {
        let mut hm: HashMap<&'static str, Self> = HashMap::new();
        hm.insert(
            "head",
            Self {
                gear: (163, 26),
                main: (153, 118),
                subs: [(189, 127), (217, 127), (246, 127)],
            },
        );
        hm.insert(
            "clothes",
            Self {
                gear: (310, 26),
                main: (298, 118),
                subs: [(334, 127), (363, 127), (391, 127)],
            },
        );
        hm.insert(
            "shoes",
            Self {
                gear: (457, 26),
                main: (443, 118),
                subs: [(479, 127), (508, 127), (536, 127)],
            },
        );
        hm
    }
}

impl WepCoords {
    pub const fn get() -> Self {
        WepCoords {
            main: (24, 24),
            sub: (27, 116),
            special: (78, 116),
        }
    }
}

pub fn get_db_connection() -> Conn {
   Conn::new(DATABASE_URL.as_str()).unwrap()
}

#[macro_export]
macro_rules! impl_string_utils {
    () => {
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
    };
}
