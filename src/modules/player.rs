use crate::utils::db::models::Player;
use crate::utils::db::models::{ModelError, NFKind};
use crate::utils::misc::pos_map;
use serenity::{
    framework::standard::{macros::command, Args, CommandResult},
    model::prelude::*,
    prelude::*,
};

#[command]
fn new(ctx: &mut Context, msg: &Message) -> CommandResult {
    let _ = match Player::add_to_db(*msg.author.id.as_u64()) {
        Ok(_) => {
            let _ = msg.reply(&ctx, "Added you to the database! ^^)");
        }
        Err(e) => {
            error!("Failed to add player to database\n\nError: {:?}", e);
            let _ = msg.reply(&ctx, "There was an issue with adding you to the database. Please contact the development team immediately.");
        }
    };

    Ok(())
}

#[command]
fn name(ctx: &mut Context, msg: &Message, args: Args) -> CommandResult {
    let mut player = match Player::from_db(*msg.author.id.as_u64()) {
        Ok(v) => v,
        Err(e) => {
            match e.as_ref() {
                ModelError::NotFound(kind, trace) => match kind {
                    NFKind::Player(_) => {
                        let _ = msg.reply(&ctx, "Command Failed - You're not in the database! Add yourself with `player new`.");
                        return Ok(());
                    }
                    _ => {
                        let _ = msg.reply(&ctx, "Command Failed - An error occured! Contact the developers immediately!");
                        error!(
                            "Something went sideways!\n\nError: {:?}\n\nBacktrace: {:#?}",
                            e, trace
                        );
                        return Ok(());
                    }
                },
                _ => {
                    let _ = msg.reply(
                        &ctx,
                        "Command Failed - An error occured! Contact the developers immediately!",
                    );
                    error!("Something went sideways!\n\nError: {:#?}", e);
                    return Ok(());
                }
            }
        }
    };

    match player.set_name(args.rest().to_string()) {
        Ok(_) => (),
        Err(_) => {
            let _ = msg.reply(&ctx, "Command Failed - Invalid name passed.");
        }
    }

    match player.update() {
        Ok(_) => {
            let _ = msg
                .channel_id
                .say(&ctx, "Name successfully updated! :smiley:");
        }
        Err(e) => {
            let _ = msg.reply(&ctx, "Command Failed - Could not update database data. Contact the developers immediately.");
            error!("Could not update name: {:#?}", e);
            return Ok(());
        }
    }

    Ok(())
}

#[command]
fn level(ctx: &mut Context, msg: &Message, mut args: Args) -> CommandResult {
    let mut player = match Player::from_db(*msg.author.id.as_u64()) {
        Ok(v) => v,
        Err(e) => {
            match e.as_ref() {
                ModelError::NotFound(kind, trace) => match kind {
                    NFKind::Player(_) => {
                        let _ = msg.reply(&ctx, "Command Failed - You're not in the database! Add yourself with `player new`.");
                        return Ok(());
                    }
                    _ => {
                        let _ = msg.reply(&ctx, "Command Failed - An error occured! Contact the developers immediately!");
                        error!(
                            "Something went sideways!\n\nError: {:?}\n\nBacktrace: {:#?}",
                            e, trace
                        );
                        return Ok(());
                    }
                },
                _ => {
                    let _ = msg.reply(
                        &ctx,
                        "Command Failed - An error occured! Contact the developers immediately!",
                    );
                    error!("Something went sideways!\n\nError: {:#?}", e);
                    return Ok(());
                }
            }
        }
    };

    let level = match args.single::<i32>() {
        Ok(v) => v,
        Err(_) => {
            let _ = msg.reply(&ctx, "Command Failed - Invalid argument passed.");
            return Ok(());
        }
    };

    player.level = level;
    if let Err(e) = player.update() {
        let _ = msg.reply(
            &ctx,
            "Command Failed - An unexpected error occurred! Contact the developers immediately!",
        );
        error!("Something went sideways!\n\nError: {:#?}", e);
    } else {
        let _ = msg.reply(&ctx, "Level set! :smiley:");
    }

    Ok(())
}

#[command]
fn rank(ctx: &mut Context, msg: &Message, mut args: Args) -> CommandResult {
    let mut player = match Player::from_db(*msg.author.id.as_u64()) {
        Ok(v) => v,
        Err(e) => {
            match e.as_ref() {
                ModelError::NotFound(kind, trace) => match kind {
                    NFKind::Player(_) => {
                        let _ = msg.reply(&ctx, "Command Failed - You're not in the database! Add yourself with `player new`.");
                        return Ok(());
                    }
                    _ => {
                        let _ = msg.reply(&ctx, "Command Failed - An error occured! Contact the developers immediately!");
                        error!(
                            "Something went sideways!\n\nError: {:?}\n\nBacktrace: {:#?}",
                            e, trace
                        );
                        return Ok(());
                    }
                },
                _ => {
                    let _ = msg.reply(
                        &ctx,
                        "Command Failed - An error occured! Contact the developers immediately!",
                    );
                    error!("Something went sideways!\n\nError: {:#?}", e);
                    return Ok(());
                }
            }
        }
    };

    let mode = if let Ok(v) = args.single::<String>() {
        v
    } else {
        let _ = msg.reply(&ctx, "Command Failed - Invalid parameter passed.");
        return Ok(());
    };
    let rank = args.rest().to_string();
    if let Err(e) = player.set_rank(mode, rank) {
        if let ModelError::InvalidParameter(fault) = e {
            let _ = msg.reply(&ctx, format!("Command Failed - {}", fault));
            return Ok(());
        }
    } else {
        let _ = msg.reply(&ctx, "Rank set! :smiley:");
    }

    if let Err(e) = player.update() {
        let _ = msg.reply(
            &ctx,
            "Command Failed - An unexpected error occurred! Contact the developers immediately!",
        );
        error!("Something went sideways!\n\nError: {:#?}", e);
    }
    Ok(())
}

#[command]
fn position(ctx: &mut Context, msg: &Message, mut args: Args) -> CommandResult {
    let mut player = match Player::from_db(*msg.author.id.as_u64()) {
        Ok(v) => v,
        Err(e) => {
            match e.as_ref() {
                ModelError::NotFound(kind, trace) => match kind {
                    NFKind::Player(_) => {
                        let _ = msg.reply(&ctx, "Command Failed - You're not in the database! Add yourself with `player new`.");
                        return Ok(());
                    }
                    _ => {
                        let _ = msg.reply(&ctx, "Command Failed - An error occured! Contact the developers immediately!");
                        error!(
                            "Something went sideways!\n\nError: {:?}\n\nBacktrace: {:#?}",
                            e, trace
                        );
                        return Ok(());
                    }
                },
                _ => {
                    let _ = msg.reply(
                        &ctx,
                        "Command Failed - An error occured! Contact the developers immediately!",
                    );
                    error!("Something went sideways!\n\nError: {:#?}", e);
                    return Ok(());
                }
            }
        }
    };

    let pos_int = match args.single::<i16>() {
        Ok(v) => v,
        Err(_) => {
            let _ = msg.reply(&ctx, "Command Failed - Invalid argument passed.");
            return Ok(());
        }
    };

    if let Err(_) = player.set_pos(pos_int) {
        let _ = msg.reply(&ctx, "Command Failed - Inavlid position passed.");
        return Ok(());
    } else {
        let pm = pos_map();
        let _ = msg.reply(
            &ctx,
            format!("Position set to `{}`!", pm.get(&pos_int).unwrap()),
        );
    }

    if let Err(e) = player.update() {
        let _ = msg.reply(
            &ctx,
            "Command Failed - An unexpected error occurred! Contact the developers immediately!",
        );
        error!("Something went sideways!\n\nError: {:#?}", e);
    }
    Ok(())
}

#[command]
fn loadout(ctx: &mut Context, msg: &Message, mut args: Args) -> CommandResult {
    let mut player = match Player::from_db(*msg.author.id.as_u64()) {
        Ok(v) => v,
        Err(e) => {
            match e.as_ref() {
                ModelError::NotFound(kind, trace) => match kind {
                    NFKind::Player(_) => {
                        let _ = msg.reply(&ctx, "Command Failed - You're not in the database! Add yourself with `player new`.");
                        return Ok(());
                    }
                    _ => {
                        let _ = msg.reply(&ctx, "Command Failed - An error occured! Contact the developers immediately!");
                        error!(
                            "Something went sideways!\n\nError: {:?}\n\nBacktrace: {:#?}",
                            e, trace
                        );
                        return Ok(());
                    }
                },
                _ => {
                    let _ = msg.reply(
                        &ctx,
                        "Command Failed - An error occured! Contact the developers immediately!",
                    );
                    error!("Something went sideways!\n\nError: {:#?}", e);
                    return Ok(());
                }
            }
        }
    };

    let ldink_link = args.single::<String>().unwrap();
    if !ldink_link.starts_with("https://selicia.github.io/en_US/#") {
        let _ = msg.reply(
            &ctx,
            "Command Failed - Invalid link passed. Please use `https://selicia.github.io/en_US`.",
        );
        return Ok(());
    }

    let ldink_hex = ldink_link
        .as_str()
        .trim_start_matches("https://selicia.github.io/en_US/#");
    if ldink_hex.len() != 25 {
        let _ = msg.reply(
            &ctx,
            "Command Failed - Invalid link passed. Please use `https://selicia.github.io/en_US`.",
        );
        return Ok(());
    }

    if let Err(e) = player.set_loadout(ldink_hex) {
        match e.as_ref() {
            ModelError::NotFound(item, bt) => {
                let _ = msg.reply(
                    &ctx,
                    format!("Command Failed - Item not found: `{:?}`", item),
                );
                return Ok(());
            }
            ModelError::InvalidParameter(s) => {
                let _ = msg.reply(
                    &ctx,
                    format!("Command Failed - Invalid parameter provided: `{}`", s),
                );
                return Ok(());
            }
            ModelError::Database(err, bt) | ModelError::Unknown(err, bt) => {
                let _ = msg.reply(&ctx, "Command Failed - An unexpected error occured! Contact the developers immediately!");
                error!(
                    "Something went sideways!\n\nError: {:?}\n\nBacktrace: {:#?}",
                    err, bt
                );
                return Ok(());
            }
        }
    } else {
        let _ = msg.reply(&ctx, "Loadout set! :smiley:");
    }

    if let Err(e) = player.update() {
        let _ = msg.reply(
            &ctx,
            "Command Failed - An unexpected error occurred! Contact the developers immediately!",
        );
        error!("Something went sideways!\n\nError: {:#?}", e);
    }
    Ok(())
}

#[command]
fn free_agent(ctx: &mut Context, msg: &Message, mut args: Args) -> CommandResult {
    let mut player = match Player::from_db(*msg.author.id.as_u64()) {
        Ok(v) => v,
        Err(e) => {
            match e.as_ref() {
                ModelError::NotFound(kind, trace) => match kind {
                    NFKind::Player(_) => {
                        let _ = msg.reply(&ctx, "Command Failed - You're not in the database! Add yourself with `player new`.");
                        return Ok(());
                    }
                    _ => {
                        let _ = msg.reply(&ctx, "Command Failed - An error occured! Contact the developers immediately!");
                        error!(
                            "Something went sideways!\n\nError: {:?}\n\nBacktrace: {:#?}",
                            e, trace
                        );
                        return Ok(());
                    }
                },
                _ => {
                    let _ = msg.reply(
                        &ctx,
                        "Command Failed - An error occured! Contact the developers immediately!",
                    );
                    error!("Something went sideways!\n\nError: {:#?}", e);
                    return Ok(());
                }
            }
        }
    };

    let resp = args.single::<String>().unwrap();

    match player.set_free_agent(resp) {
        Err(e) => {
            if let ModelError::InvalidParameter(s) = e {
                let _ = msg.reply(&ctx, format!("Command Failed - {}", s));
            }
        }
        Ok(v) => {
            let _ = msg.reply(&ctx, format!("FA status set to `{}`!", v));
        }
    }

    if let Err(e) = player.update() {
        let _ = msg.reply(
            &ctx,
            "Command Failed - An unexpected error occurred! Contact the developers immediately!",
        );
        error!("Something went sideways!\n\nError: {:#?}", e);
    }
    Ok(())
}

#[command]
fn set_private(ctx: &mut Context, msg: &Message, mut args: Args) -> CommandResult {
    let mut player = match Player::from_db(*msg.author.id.as_u64()) {
        Ok(v) => v,
        Err(e) => {
            match e.as_ref() {
                ModelError::NotFound(kind, trace) => match kind {
                    NFKind::Player(_) => {
                        let _ = msg.reply(&ctx, "Command Failed - You're not in the database! Add yourself with `player new`.");
                        return Ok(());
                    }
                    _ => {
                        let _ = msg.reply(&ctx, "Command Failed - An error occured! Contact the developers immediately!");
                        error!(
                            "Something went sideways!\n\nError: {:?}\n\nBacktrace: {:#?}",
                            e, trace
                        );
                        return Ok(());
                    }
                },
                _ => {
                    let _ = msg.reply(
                        &ctx,
                        "Command Failed - An error occured! Contact the developers immediately!",
                    );
                    error!("Something went sideways!\n\nError: {:#?}", e);
                    return Ok(());
                }
            }
        }
    };

    let resp = args.single::<String>().unwrap();

    match player.set_private(resp) {
        Err(e) => {
            if let ModelError::InvalidParameter(s) = e {
                let _ = msg.reply(&ctx, format!("Command Failed - {}", s));
            }
        }
        Ok(v) => {
            let _ = msg.reply(&ctx, format!("Privacy set to `{}`!", v));
        }
    }

    if let Err(e) = player.update() {
        let _ = msg.reply(
            &ctx,
            "Command Failed - An unexpected error occurred! Contact the developers immediately!",
        );
        error!("Something went sideways!\n\nError: {:#?}", e);
    }
    Ok(())
}
