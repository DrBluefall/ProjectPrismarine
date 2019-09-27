use crate::ShardManagerContainer;
use serenity::{
    prelude::*,
    model::prelude::*,
    framework::standard::{
        CommandResult, Args,
        macros::command
    }
};
use serenity::utils::Colour as Color;
use log::*;
use chrono::offset::Utc;


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
    for (_id, runner) in &*runners {
        res.push(format!("`{:#?}`", runner.latency.unwrap_or_default()));
    }
    msg.channel_id.send_message(&ctx, |m| {
        m.embed(|e| {
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

#[command]
#[owners_only]
fn user(ctx: &mut Context, msg: &Message, mut args: Args) -> CommandResult {
    let user: Option<User>;

    if !args.is_empty() {

    user = match args.parse::<u64>() {
        Ok(id) => match ctx.http.get_user(id) {
            Ok(v) => {
                args.advance();
                Some(v)
            },
            Err(_) => {
                let _ = msg.reply(&ctx, "Command Failed - Invalid User ID passed.");
                return Ok(());
            },
        },
        Err(_) => {
            if msg.mentions.is_empty() {
                let _ = msg.reply(&ctx, "Command Failed - User not specified.");
                return Ok(());
            } else {
                Some(match ctx.http.get_user(*msg.mentions[0].id.as_u64()) {
                    Ok(v) => v,
                    Err(e) => {
                        error!("Could not retrieve user data: {:#?}", e);
                        let _ = msg.reply(&ctx, "Command Failed - Could not retrieve user data.");
                        return Ok(());
                    }
                })
            }
        },
    };
    } else {
        user = match ctx.http.get_user(*msg.author.id.as_u64()) {
            Ok(v) => Some(v),
            Err(e) => {
                error!("Could not retrieve user data: {:#?}", e);
                let _ = msg.reply(&ctx, "Command Failed - Could not retrieve user data.");
                return Ok(());
            } 
        };
    }
    
    let user: User = user.unwrap();

    let _ = msg.channel_id.send_message(&ctx, |m| {
       m.embed(|e| {
            e.title(format!("User Report - {}#{}", user.name, user.discriminator));
            e.field("Discord ID:", format!("`{}`", user.id.as_u64()), true);
            e.field("Creation Date:", format!("`{}`", user.created_at().to_rfc2822()), true);
            e.field("Account Type:", if user.bot {"`Bot`"} else {"`Standard`"}, true);
            e.thumbnail(user.face());
            e.footer(|f| {
                f.text(format!("Report Generated at {}", Utc::now().to_rfc2822()))
            })
       })
    });
    
    Ok(())
}
