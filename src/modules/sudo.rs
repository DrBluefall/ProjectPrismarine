use crate::ShardManagerContainer;
use serenity::{
    prelude::*,
    model::prelude::*,
    framework::standard::{
        CommandResult,
        macros::command
    }
};
use serenity::utils::Colour as Color;
#[macro_use]
use log::*;


#[command]
#[owners_only]
fn logout(ctx: &mut Context, msg: &Message) -> CommandResult {
    
    let dat = ctx.data.read();

    if let Some(manager) = dat.get::<ShardManagerContainer>() {
        let _ = msg.channel_id.say(&ctx, "*Shutting down Rusted Project Prismarine...*");
        manager.lock().shutdown_all();
    } else {
        let _ = msg.reply(&ctx, "Command Failed - Could not retrieve shard manager, bot will need to be shutdown manually.");
        error!("Was unable to retrieve shard manager at command invokation");
    }
    Ok(())
}

#[command]
#[owners_only]
fn latency(ctx: &mut Context, msg: &Message) -> CommandResult {
    let dat = ctx.data.read();

    let shard_manager = match dat.get::<ShardManagerContainer>() {
        Some(v) => v,
        None => {
            let _ = msg.reply(&ctx, "Command Failed - Could not retrieve shard manager");
            error!("Failed to retrieve shard manager at latency command invoke.");
            return Ok(());
        },
    };
    let manager = shard_manager.lock();
    let runners = manager.runners.lock();
    let mut res: Vec<String> = Vec::new();
    for (id, runner) in &*runners {
        res.push(format!("`{:#?}`", runner.latency.unwrap_or_default()));
    }
    msg.channel_id.send_message(&ctx, |m| {
        m.embed(|mut e| {
            e.title(format!("{} - Latency Report", ctx.http.get_current_user().unwrap().name));
            for (index, string) in res.iter().enumerate() {
                e.field(format!("Shard #{}'s Latency:", index), format!("{}", string), true);
            }
            e.color(Color::from_rgb(255, 0, 0));
            e
        });
        m
    })?;
    Ok(())
}
