SELECT
       level,
       loadout,
       id,
       friend_code,
       ign,
       sz,
       tc,
       rm,
       cb,
       sr,
       position,
       team_id,
       free_agent,
       is_private
FROM prismarine_rusted.player_profiles WHERE id = ?

