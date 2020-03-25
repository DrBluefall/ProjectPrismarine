UPDATE prismarine_rusted.player_profiles
SET
    friend_code = :fc,
    ign = :name,
    level = :lv,
    sz = :sz,
    tc = :tc,
    rm = :rm,
    cb = :cb,
    sr = :sr,
    position = :pos,
    loadout = :ld,
    team_id = :tid,
    is_private = :isp,
    free_agent = :fa
WHERE id = :id;