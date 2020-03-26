//! The core of Project Prismarine. This is the entry point of the bot and where the boilerplate of Serenity goes.
#![feature(backtrace)]
#![warn(clippy::pedantic)]
#![allow(clippy::cast_possible_wrap)]
#![allow(clippy::cast_sign_loss)]
#![allow(clippy::cast_possible_truncation)]
extern crate chrono;
extern crate discord_bots_org; // DBL API Wrapper. Used with Reqwest.
extern crate reqwest; // Used with discord_bots_org for dispatching to DBL
extern crate serde; // Serialization and deserialization of JSON from DB into structs
extern crate serde_json; // JSON support of serde // Time keeping library.
#[macro_use]
extern crate log; // logging crate
extern crate mysql; // MySQL API bindings.
extern crate pretty_env_logger; // nicer logging
extern crate regex;
#[macro_use]
extern crate lazy_static; // Set static variables at runtime.
extern crate better_panic;
extern crate heck; // Case conversion crate.
extern crate image; // Image editing library.
extern crate time; // used with chrono.
extern crate tokio;
extern crate toml; // TOML parsing, for the new config.

use discord_bots_org::ReqwestSyncClient as APIClient; // Used to update discordbots.org
use reqwest::Client as ReqwestClient;
use serenity::{
    // Library for Discord. The central library for this bot.
    client::bridge::gateway::ShardManager,
    framework::{standard::macros::group, StandardFramework},
    model::{event::ResumedEvent, gateway::Ready},
    prelude::*,
};
use std::{collections::HashSet, io::Read, sync::Arc};

// Declare modules for use
mod modules;
mod utils;
// Import the commands to put them into their groups
use modules::meta::*;
use modules::player::*;
use modules::sudo::*;
use modules::team::*;

// Various holders to be carried across modules.
struct ShardManagerContainer;
struct APIClientContainer;
struct TokenHolder;
impl TypeMapKey for ShardManagerContainer {
    type Value = Arc<Mutex<ShardManager>>;
}
impl TypeMapKey for APIClientContainer {
    type Value = APIClient;
}
impl TypeMapKey for TokenHolder {
    type Value = String;
}

struct Handler;

#[serenity::async_trait]
impl EventHandler for Handler {
    async fn ready(&self, _: Context, ready: Ready) {
        info!(
            "\x1b[1m{}#{} is \x1b[38;5;082monline!\x1b[0m",
            ready.user.name, ready.user.discriminator
        );
    }
    async fn resume(&self, _: Context, _: ResumedEvent) {
        info!("Reconnected to discord!");
    }
}

// Configuration structure
#[derive(serde::Deserialize)]
struct Prisbot {
    prisbot: Config,
}

#[derive(serde::Deserialize)]
struct Config {
    discord: DiscordCfg,
    database: Database,
    log: Option<String>,
}
#[derive(serde::Deserialize)]
struct DiscordCfg {
    bot_token: String,
    dbl_api_token: Option<String>,
    owners: Vec<u64>,
    prefix: String,
}
#[derive(serde::Deserialize)]
struct Database {
    url: Option<String>,
    user: Option<String>,
    password: Option<String>,
    host: Option<String>,
    port: Option<u16>,
    database_name: Option<String>,
}

///Commands & Command Groups

//Commands for this group:
//sudo info
//     logout
//     latency
//     user
//     update_stats
#[group]
#[commands(info, logout, latency, user, update_stats)]
#[prefix("sudo")]
#[owners_only]
struct SudoMod;

//Commands for this group:
//player update name
//              level
//              rank
//              position
//              loadout
//              free_agent
//              set_private
//              fc
#[group]
#[commands(name, level, rank, position, loadout, free_agent, set_private, fc)]
#[prefixes("u", "update")]
struct PlayerUpdateMod;

//Commands for this group:
//player new
//       show
#[group]
#[commands(new, show)]
#[sub_groups(playerupdatemod)]
#[prefixes("p", "player")]
struct PlayerMod;

/*
//Commands for this group:
//team update description
#[group]
#[commands(description)]
#[prefixes ("u", "update")]
struct TeamUpdateMod;
*/

//Commands for this group:
//team new
#[group]
#[commands(team_new)]
//#[sub_groups(teamupdatemod)]
#[prefixes("t", "team")]
struct TeamMod;

/* End of commands */

lazy_static! {
    static ref DATABASE_OPTIONS: mysql::Opts = {
        let mut f = String::new();
        std::fs::File::open("prisbot.toml")
            .expect("Expected config file named 'prisbot.toml'")
            .read_to_string(&mut f)
            .unwrap();
        let p: Prisbot = toml::from_str(&f).unwrap();
        let out = if let Some(url) = p.prisbot.database.url {
            mysql::Opts::from_url(&url).unwrap()
        } else {
            mysql::Opts::from({
                let mut o = mysql::OptsBuilder::new();
                o.user(p.prisbot.database.user)
                    .ip_or_hostname(p.prisbot.database.host)
                    .pass(p.prisbot.database.password)
                    .db_name(p.prisbot.database.database_name)
                    .tcp_port(p.prisbot.database.port.unwrap_or(3306_u16));
                o
            })
        };
        out
    };
}

#[tokio::main]
async fn main() {
    let mut f = String::new();
    std::fs::File::open("prisbot.toml")
        .expect("Expected config file named 'prisbot.toml'")
        .read_to_string(&mut f)
        .unwrap();
    let conf = {
        let p: Prisbot = toml::from_str(&f).expect("Invalid TOML config");
        p.prisbot
    };

    std::env::set_var("RUST_LOG", if let Some(s) = &conf.log { s } else { "info" });
    pretty_env_logger::init_timed();
    better_panic::install();

    // Check if the db config was done correctly
    if let Err(e) = mysql::Conn::new(DATABASE_OPTIONS.clone()) {
        error!("Error occured while verifying database connection: {:?}", e);
        std::process::exit(1);
    }

    info!("Config acquired!");

    let mut client = Client::new_with_extras(&conf.discord.bot_token, |ex| {
        ex.event_handler(Handler).framework(
            StandardFramework::new()
                .configure(|c| {
                    c.allow_dm(false)
                        .owners({
                            let mut own = HashSet::new();
                            for id in &conf.discord.owners {
                                own.insert(serenity::model::id::UserId(*id));
                            }
                            own
                        })
                        .prefix(&conf.discord.prefix)
                })
                .group(&SUDOMOD_GROUP)
                .group(&PLAYERMOD_GROUP)
                // .group(&TEAMMOD_GROUP) -- re-enable when teams are stable
                .help(&ASSIST),
        )
    })
    .await
    .expect("Failed to create client");

    let req_client = Arc::new(ReqwestClient::new());
    let api_client = APIClient::new(Arc::clone(&req_client));

    {
        let mut data = client.data.write().await;
        data.insert::<ShardManagerContainer>(Arc::clone(&client.shard_manager));
        data.insert::<APIClientContainer>(api_client);
        data.insert::<TokenHolder>(if let Some(token) = &conf.discord.dbl_api_token {
            token.to_owned()
        } else {
            "".to_string()
        });
    }
    /*
    let (owners, bot_id) = match client.cache_and_http.http.get_current_application_info() {
        Ok(info) => {
            let mut owners = HashSet::new();
            owners.insert(info.owner.id);
            for id in &conf.discord.owners {
                owners.insert(serenity::model::id::UserId::from(*id));
            }
            (owners, info.id)
        }
        Err(why) => panic!("Could not access application info: {:?}", why),
    };
    info!("Owner/bot info retrieved!");

    client.with_framework(
        StandardFramework::new()
            .configure(|c| {
                c.owners(owners)
                    .on_mention(Some(bot_id))
                    .prefix(conf.discord.prefix.as_str())
            })
            .group(&SUDOMOD_GROUP)
            .group(&PLAYERMOD_GROUP)
            .group(&TEAMMOD_GROUP)
            .help(&ASSIST),
    );
    info!("Framework prepared!");
    */
    if let Err(why) = client.start().await {
        error!("Uncaught Exception: {:#?}", why);
    }
}
