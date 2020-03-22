use crate::{APIClientContainer, ShardManagerContainer, TokenHolder};
use chrono::offset::Utc;
use discord_bots_org::builder::widget::LargeWidget;
use discord_bots_org::model::ShardStats;
use log::*;
use serenity::utils::Colour as Color;
use serenity::{
    framework::standard::{macros::command, Args, CommandResult},
    model::prelude::*,
    prelude::*,
};
use std::{thread::sleep, time::Duration};

#[command]
#[owners_only]
pub async fn logout(ctx: &mut Context, msg: &Message) -> CommandResult {
    let dat = ctx.data.read().await;

    if let Some(manager) = dat.get::<ShardManagerContainer>() {
        let _ = msg
            .channel_id
            .say(&ctx, "*Shutting down Rusted Project Prismarine...*");
        manager.lock().await.shutdown_all().await;
    } else {
        let _ = msg.reply(&ctx, "Command Failed - Could not retrieve shard manager, bot will need to be shutdown manually.");
        error!("Was unable to retrieve shard manager at command invocation");
    }
    Ok(())
}

#[command]
#[owners_only]
pub async fn latency(ctx: &mut Context, msg: &Message) -> CommandResult {
    let dat = ctx.data.read().await;

    let shard_manager = if let Some(v) = dat.get::<ShardManagerContainer>() {
        v
    } else {
        let _ = msg.reply(&ctx, "Command Failed - Could not retrieve shard manager");
        error!("Failed to retrieve shard manager at latency command invoke.");
        return Ok(());
    };
    let manager = shard_manager.lock().await;
    let runners = manager.runners.lock().await;
    let mut res: Vec<String> = Vec::new();
    for runner in (*runners).values() {
        res.push(format!("`{:#?}`", runner.latency.unwrap_or_default()));
    }
    let name = ctx.http.get_current_user().await.unwrap().name;
    msg.channel_id.send_message(&ctx, |m| {
        m.embed(|e| {
            e.title(format!(
                "{} - Latency Report",
                name
            ));
            for (index, string) in res.iter().enumerate() {
                e.field(
                    format!("Shard #{}'s Latency:", index),
                    string.to_string(),
                    true,
                );
            }
            e.color(Color::from_rgb(255, 0, 0));
            e
        });
        m
    }).await?;
    Ok(())
}

#[command]
#[owners_only]
pub async fn user(ctx: &mut Context, msg: &Message, mut args: Args) -> CommandResult {
    let user: Option<User> = if args.is_empty() {
        match ctx.http.get_user(*msg.author.id.as_u64()).await {
            Ok(v) => Some(v),
            Err(e) => {
                error!("Could not retrieve user data: {:#?}", e);
                let _ = msg.reply(&ctx, "Command Failed - Could not retrieve user data.");
                return Ok(());
            }
        }
    } else {
        match args.parse::<u64>().await {
            Ok(id) => {
                if let Ok(v) = ctx.http.get_user(id).await {
                    args.advance();
                    Some(v)
                } else {
                    let _ = msg.reply(&ctx, "Command Failed - Invalid User ID passed.");
                    return Ok(());
                }
            }
            Err(_) => {
                if msg.mentions.is_empty() {
                    let _ = msg.reply(&ctx, "Command Failed - User not specified.");
                    return Ok(());
                } else {
                    Some(match ctx.http.get_user(*msg.mentions[0].id.as_u64()).await {
                        Ok(v) => v,
                        Err(e) => {
                            error!("Could not retrieve user data: {:#?}", e);
                            let _ =
                                msg.reply(&ctx, "Command Failed - Could not retrieve user data.");
                            return Ok(());
                        }
                    })
                }
            }
        }
    };

    let user: User = user.unwrap();

    let _ = msg.channel_id.send_message(&ctx, |m| {
        m.embed(|e| {
            e.title(format!(
                "User Report - {}#{}",
                user.name, user.discriminator
            ));
            e.field("Discord ID:", format!("`{}`", user.id.as_u64()), true);
            e.field(
                "Creation Date:",
                format!("`{}`", user.created_at().to_rfc2822()),
                true,
            );
            e.field(
                "Account Type:",
                if user.bot { "`Bot`" } else { "`Standard`" },
                true,
            );
            e.thumbnail(user.face());
            e.footer(|f| f.text(format!("Report Generated at {}", Utc::now().to_rfc2822())))
        })
    }).await;

    Ok(())
}

#[command]
#[owners_only]
pub async fn update_stats(ctx: &mut Context, msg: &Message) -> CommandResult {
    let dat = ctx.data.read().await;

    let api_client = if let Some(v) = dat.get::<APIClientContainer>() {
        v
    } else {
        let _ = msg.reply(&ctx, "Command Failed - Could not retrieve API client.");
        error!("Could not get API client for DBL updates.");
        return Ok(());
    };

    let token = if let Some(v) = dat.get::<TokenHolder>() {
        v
    } else {
        let _ = msg.reply(&ctx, "Command Failed - Could not retrieve DBL API token.");
        error!("Could not get DBL API token for updates.");
        return Ok(());
    };

    loop {
        let dat = ctx.data.read().await;

        let manager = if let Some(v) = dat.get::<ShardManagerContainer>() {
            v
        } else {
            error!("Could not post stats to discordbots.org - failed to retrieve shard manager.");
            return Ok(());
        }
        .lock().await;

        let runners = manager.runners.lock().await;

        let shard_count = (*runners).len();

        let server_count = ctx.cache.read().await.guilds.len();

        let stats = ShardStats::Cumulative {
            shard_count: Some(shard_count as u64),
            guild_count: server_count as u64,
        };

        match api_client.post_stats(
            token,
            *ctx.http.get_current_user().await.unwrap().id.as_u64(),
            &stats,
        ) {
            Ok(_) => info!("Posted stats to discordbots.org!"),
            Err(e) => error!("Failed to post stats to discordbots.org: {:#?}", e),
        }

        sleep(Duration::from_secs(60));
    }
}

#[command]
pub async fn info(ctx: &mut Context, msg: &Message) -> CommandResult {
    let mut widget = LargeWidget::new(*ctx.http.get_current_user().await.unwrap().id.as_u64());

    (&mut widget).top_color("b30000");

    let widget = widget.build().unwrap().replace(".svg", ".png");
    let _ = msg.channel_id.send_message(&ctx, |m| {
        m.embed(|e| {
            e.image(widget);
            e
        });
        m
    });

    Ok(())
}
