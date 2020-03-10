use crate::get_player;
use crate::utils::db::{Player, Team};
use crate::utils::misc::{ModelError, NFKind};
use serenity::{
    framework::standard::{macros::command, Args, CommandResult},
    model::prelude::*,
    prelude::*,
};

#[command("new")]
pub fn team_new(ctx: &mut Context, msg: &Message, args: Args) -> CommandResult {
    let new_cap = get_player!(ctx, msg, *msg.author.id.as_u64());
    let name = args.rest().to_string();
    match Team::add_to_db(&new_cap, &name) {
        Ok(_) => {
            let _ = msg.reply(
                &ctx,
                "Team registered into the database! Godspeed, new captain!",
            );
        }
        Err(e) => {
            let _ = msg.reply(
                &ctx,
                "Command failed - An error occurred! Contact the developers immediately!",
            );
            error!("Something went sideways!\n\nError: {:#?}", e);
        }
    }

    Ok(())
}
