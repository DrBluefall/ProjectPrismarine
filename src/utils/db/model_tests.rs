#[cfg(test)]
mod tests {
    use chrono::Utc;
    use crate::utils::db::Player;
    use crate::utils::db::{Team, team::Tournament};
    use crate::utils::db::{loadout::RawLoadout, Loadout};
    use crate::utils::misc::ModelError;
    #[test]
    fn player_add() {
        Player::add_to_db(1).unwrap();
    }

    #[test]
    fn player_from() {
        Player::from_db(1).unwrap();
    }

    #[test]
    fn player_update() {
        let mut player = Player::from_db(1).unwrap();
        player.level = 42;
        player.update().unwrap();
    }

    #[test]
    fn player_raw_deserialize() {
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
    fn player_re_fc() {
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
    fn player_pos_setting() {
        let mut player = Player::from_db(1).unwrap();
        player.set_pos(0i16).unwrap();
        player.set_pos(1i16).unwrap();
        player.set_pos(2i16).unwrap();
        player.set_pos(3i16).unwrap();
        player.set_pos(4i16).unwrap();
        player.set_pos(5i16).unwrap_err();
    }

    #[test]
    fn player_rank_setting() {
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
    fn loadout_full_deserial() {
        let test_ld = "0000000000000000000000000";
        let raw = RawLoadout::parse(test_ld).unwrap();
        println!("{:#?}", Loadout::from_raw(raw).unwrap());
    }

    #[test]
    fn loadout_image_gen() {
        let test_ld = "080311694ac62098ce6e214e5";
        let raw = RawLoadout::parse(test_ld).unwrap();
        let ld = Loadout::from_raw(raw).unwrap();
        ld.to_img().unwrap().save("ld_test.png").unwrap();
    }

    #[test]
    #[ignore]
    fn team_add() {
        Team::add_to_db(Player::from_db(1).unwrap(), "foobar".to_string()).unwrap();
    }

    #[test]
    fn team_from() {
        Team::from_db(1).unwrap();
    }

    #[test]
    fn team_update() {
        let mut team = Team::from_db(1).unwrap();
        team.mod_desc("baz bah bur".to_string()).unwrap();
        team.add_tournament(
            Tournament::new("footourney".to_string(), 5_i16, Utc::now())
        );

        team.update().unwrap();
    }

}
