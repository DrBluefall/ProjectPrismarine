use crate::utils::db::models::Player;
use serenity::{
    framework::standard::{macros::command, Args, CommandResult},
    model::prelude::*,
    prelude::*,
};
use crate::ConnectionHolder;

#[command]
fn new(ctx: &mut Context, msg: &Message) -> CommandResult {
    let dat = ctx.data.read();
    let conn = match dat.get::<ConnectionHolder>() {
        Some(v) => v.lock().unwrap(),
        None => {
            let _ = msg.reply(&ctx, "Command Failed - Could not get connection to database.");
            error!("Could not connection to database for adding new player");
            return Ok(());
        }
    };
    let _ = match Player::add_to_db(&*conn, *msg.author.id.as_u64()) {
        Ok(_) => { let _ = msg.reply(&ctx, "Added you to the database! ^^)");},
        Err(e) => {
            error!("Failed to add player to database");
            let _ = msg.reply(&ctx, "There was an issue with adding you to the database. Please contact the development team immediately.");
        }
    };

    Ok(())
}

#[command]
fn name(ctx: &mut Context, msg: &Message, mut args: Args) -> CommandResult {
    let dat = ctx.data.read();
    let conn = match dat.get::<ConnectionHolder>() {
        Some(v) => v.lock().unwrap(),
        None => {
            let _ = msg.reply(&ctx, "Command Failed - Could not get connection to database.");
            error!("Could not get connection to database for editing player data");
            return Ok(());
        }
    };

    let mut player = match Player::from_db(&*conn, *msg.author.id.as_u64()) {
        Ok(v) => v,
        Err(e) => {
            let _ = msg.reply(&ctx, "Command failed - You aren't in the database! Add yourself with `player new`.");
            return Ok(());
        }
    };

    match player.set_name(args.rest().to_string()) {
        Ok(_) => (),
        Err(_) => {let _ = msg.reply(&ctx, "Command Failed - Invalid name passed.");},
    }

    match player.update(&conn) {
        Ok(_) => {
            let _ = msg.channel_id.say(&ctx, "Name successfully updated! :smiley:");
        },
        Err(e) => {
            let _ = msg.reply(&ctx, "Command Failed - Could not update database data. Contact the developers immediately.");
            error!("Could not update name: {:#?}", e);
            return Ok(());
        }
    }

    Ok(())
}
