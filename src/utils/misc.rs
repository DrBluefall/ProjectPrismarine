use std::collections::HashMap;

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