use crate::utils::db::models::Player;
use crate::utils::db::models::{ModelError, NFKind};
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
        Err(e) => match e.as_ref() {
            ModelError::Database(message, bt) => {
                let _ = msg.reply(&ctx,
                                  format!(
                                      "Command Failed - Database Error encountered! Alert the developers immediately!\n\n Message: `{}`",
                                      message
                                  )
                );
                error!("Issue in database interaction - source: `player update name` - Message: {} \n\n Traceback: {:#?}", message, bt);
                return Ok(());
            }
            ModelError::NotFound(kind, trace) => match kind {
                NFKind::Player(_) => {
                    let _ = msg.reply(&ctx, "Command Failed - You're not in the database! Add yourself with `player new`.");
                    return Ok(());
                }
                _ => {
                    let _ = msg.reply(&ctx, "Command Failed - Error in database retrieval! Contact the developers immediately!");
                    error!("Database item not found! \n\nError: {:#?}\n\nBacktrace: {:#?}", e, trace);
                    return Ok(());
                }
            },
            ModelError::InvalidParameter(p) => {
                let _ = msg.reply(
                    &ctx,
                    format!("Command Failed - Invalid parameter detected: `{}`", p),
                );
                return Ok(());
            }
            ModelError::Unknown(s, trace) => {
                let _ = msg.reply(&ctx, "Command Failed - An unknown error has occured! Contact the developers immediately!");
                error!(
                    "An unknown error has occurred! \n Message: {}\n\n Backtrace: \n{:#?}",
                    s, trace
                );
                return Ok(());
            }
        },
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
    unimplemented!()
}

#[command]
fn rank(ctx: &mut Context, msg: &Message, mut args: Args) -> CommandResult {
    unimplemented!()
}

#[command]
fn position(ctx: &mut Context, msg: &Message, mut args: Args) -> CommandResult {
    unimplemented!()
}

#[command]
fn loadout(ctx: &mut Context, msg: &Message, mut args: Args) -> CommandResult {
    unimplemented!()
}

#[command]
fn free_agent(ctx: &mut Context, msg: &Message, mut args: Args) -> CommandResult {
    unimplemented!()
}

#[command]
fn set_private(ctx: &mut Context, msg: &Message, mut args: Args) -> CommandResult {
    unimplemented!()
}
