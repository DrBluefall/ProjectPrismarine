use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Debug)]
pub struct Player {
    pub id: u64,
    in_game_name: String,
    friend_code: String,
    pub level: u32,
    sz: String,
    tc: String,
    rm: String,
    cb: String,
    sr: String,
    position: &str,
}
