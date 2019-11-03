use std::collections::HashMap;
use std::result::Result;
use postgres::Connection;
use postgres::TlsMode;

lazy_static! {
    static ref DATABASE_URL: String = std::env::var("PRISBOT_DATABASE").unwrap();
}

pub fn get_ranks() -> Vec<&'static str> {
    vec![
        "C-", "C", "C+", "B-", "B", "B+", "A-", "A", "A+", "S", "S+0", "S+1", "S+2", "S+3", "S+4",
        "S+5", "S+6", "S+7", "S+8", "S+9", "X",
    ]
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

pub fn hex_to_bin(input: String) -> Result<String, HexError> {
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

pub fn get_db_connection() -> Connection {
    Connection::connect(DATABASE_URL.as_str(), TlsMode::None).unwrap()
}