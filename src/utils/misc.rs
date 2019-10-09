use std::collections::HashMap;
use std::result::Result;

pub fn get_ranks() -> Vec<&'static str> {
    vec![
    "C-", "C", "C+", "B-", "B", "B+", "A-", "A", "A+", "S", "S+0", "S+1", "S+2", "S+3", "S+4",
    "S+5", "S+6", "S+7", "S+8", "S+9", "X"
    ]
}

pub fn pos_map() -> HashMap<i8, &'static str> {
    let mut hm: HashMap<i8, &'static str> = HashMap::new();
    hm.insert(0, "Not Set");
    hm.insert(1, "Frontline");
    hm.insert(2, "Midline");
    hm.insert(3, "Backline");
    hm.insert(4, "Flex");
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
