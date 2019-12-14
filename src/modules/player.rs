use crate::utils::db::Player;
use crate::utils::misc::pos_map;
use crate::utils::misc::{ModelError, NFKind};
use image::png::PNGEncoder;
use image::ColorType;
use serenity::{
    framework::standard::{macros::command, Args, CommandResult},
    http::AttachmentType,
    model::prelude::*,
    prelude::*,
    utils::Colour as Color,
};

/// Macro to assist in retrieving players.
macro_rules! get_player {
    ($ctx:expr, $msg:expr, $id:expr) => {{
        let ctx: &mut Context = $ctx;
        let msg: &Message = $msg;
        let id: u64 = $id;
        #[allow(unused_mut)]
        let mut plr = match Player::from_db(id) {
            Ok(v) => v,
            Err(e) => match e.as_ref() {
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
        };
        plr
    }}
}

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
    let mut player = get_player!(ctx, msg, *msg.author.id.as_u64());

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
    let mut player = get_player!(ctx, msg, *msg.author.id.as_u64());

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
    let mut player =  get_player!(ctx, msg, *msg.author.id.as_u64());

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
    let mut player = get_player!(ctx, msg, *msg.author.id.as_u64());

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
    let mut player = get_player!(ctx, msg, *msg.author.id.as_u64());
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
            ModelError::NotFound(item, _) => {
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
    let mut player = get_player!(ctx, msg, *msg.author.id.as_u64());
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
    let mut player = get_player!(ctx, msg, *msg.author.id.as_u64());

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

#[command]
fn fc(ctx: &mut Context, msg: &Message, args: Args) -> CommandResult {
    let mut player = get_player!(ctx, msg, *msg.author.id.as_u64());

    let fcin = args.rest();
    if let Err(_) = player.set_fc(fcin) {
        msg.reply(&ctx, "Command Failed - Invaild friend code passed in.")
            .unwrap();
    } else {
        msg.reply(&ctx, "Friend code updated! :smiley:").unwrap();
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
fn show(ctx: &mut Context, msg: &Message, mut args: Args) -> CommandResult {
    let mut self_retrieve: bool = false;
    let player_id: u64 = if args.len() == 0 {
        self_retrieve = true;
        *msg.author.id.as_u64()
    } else {
        if msg.mentions.len() != 1 {
            match args.single::<u64>() {
                Ok(v) => v,
                Err(_) => {
                    let _ = msg.reply(&ctx, "Command Failed - Invalid argument passed.");
                    return Ok(());
                }
            }
        } else {
            *msg.mentions[0].id.as_u64()
        }
    };
    let player = match Player::from_db(player_id) {
        Ok(v) => v,
        Err(e) => {
            match e.as_ref() {
                ModelError::NotFound(kind, trace) => match kind {
                    NFKind::Player(_) => {
                        let notif = if self_retrieve {
                            "Command Failed - You're not in the database! Add yourself with `player new`.".to_string()
                        } else {
                            format!(
                                "Command Failed - Player ID {} is not in the database!",
                                player_id
                            )
                        };

                        let _ = msg.reply(&ctx, notif);
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

    let i = player.loadout().to_img().unwrap().to_rgba();
    let w = i.width();
    let h = i.height();

    let mut buf: Vec<u8> = Vec::new();

    let encoder = PNGEncoder::new(&mut buf);
    encoder
        .encode(&i.into_raw(), w, h, ColorType::RGBA(8))
        .unwrap();

    let usr = if let Ok(v) = ctx.http.get_user(player_id) {
        v
    } else {
        msg.reply(
            &ctx,
            format!("Command Failed - Discord User `{}` not found.", player_id),
        )
        .unwrap();
        return Ok(());
    };

    msg.channel_id.send_message(&ctx, |m| {
        m.embed(|e| {
            e.title(format!("Player Profile - {}", usr.name));
            e.field("In-Game Name", player.name(), true);
            e.field("Friend Code", if *player.is_private() {
                if *msg.author.id.as_u64() == *player.id() as u64 {
                    player.fc()
                } else {
                    "SW-////-////-////"
                }
            } else {
                player.fc()
            }, true);
            e.field("Level", player.level, true);
            e.field("Position", player.pos(), true);

            for (mode, rank) in player.ranks().iter() {
                e.field(mode, rank, true);
            }
            e.image("attachment://ld.png");
            if let Some(link) = usr.avatar_url() {
                e.thumbnail(link);
            }
            if *player.is_free_agent() {
                e.color(Color::from_rgb(0xFF, 0x4F, 0x00));
                e.footer(|f| {
                    f.text("This user is a free agent! Spread the word and help this person get a team!");
                    f.icon_url(ctx.http.as_ref()
                    .get_current_user().unwrap()
                    .avatar_url().unwrap_or(
                        "https://cdn.discordapp.com/attachments/637014853386764338/646812631130177546/JPEG_20190504_150808.png"
                        .to_string()
                    ))
                });
            } else {
                e.color(Color::from_rgb(0xFF, 0x00, 0x00));
            }
            e
        });
        m.add_file(AttachmentType::Bytes((&buf,"ld.png")));
        m
    }).unwrap();

    Ok(())
}
