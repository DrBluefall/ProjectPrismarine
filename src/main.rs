#![feature(backtrace)]
extern crate discord_bots_org; // DBL API Wrapper. Used with Reqwest.
extern crate dotenv; // Get environment variables from .env files.
extern crate reqwest;
extern crate serde; // Serialization and deserialization of JSON from DB into structs
extern crate serde_json; // JSON support of serde // Used with discord_bots_org for dispatching to DBL
#[macro_use]
extern crate log; // logging crate
extern crate postgres; // PostgreSQL API bindings.
extern crate postgres_derive;
extern crate pretty_env_logger; // nicer logging
extern crate regex;
#[macro_use]
extern crate lazy_static; // Set static variables at runtime.
extern crate heck;
extern crate image; // Image editing library // Case conversion crate.

use discord_bots_org::ReqwestSyncClient as APIClient; // Used to update discordbots.org
use dotenv::dotenv; // used to load .env files from directory.
use postgres::{Connection, TlsMode};
use reqwest::Client as ReqwestClient;
use serenity::{
    // Library for Discord. The central library for this bot.
    client::bridge::gateway::ShardManager,
    framework::{standard::macros::group, StandardFramework},
    model::{event::ResumedEvent, gateway::Ready},
    prelude::*,
};
use std::env;
use std::{collections::HashSet, sync::Arc};

// Declare modules for use
mod modules;
mod utils;
// Import the commands to put them into their groups
use modules::player::*;
use modules::sudo::*;

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
impl EventHandler for Handler {
    fn ready(&self, _: Context, ready: Ready) {
        info!(
            "\x1b[1m{}#{} is \x1b[38;5;082monline!\x1b[0m",
            ready.user.name, ready.user.discriminator
        );
    }
    fn resume(&self, _ctx: Context, _: ResumedEvent) {
        info!("Reconnected to discord!");
    }
}
// declare groups and their subcommands
group!({
    name: "sudo",
    options: {
        prefix: "sudo",
        owners_only: true
    },
    commands: [info, logout, latency, user, update_stats]
});

group!({
    name: "update",
    options: {
        prefixes: [ "u", "update" ],
    },
    commands: [name, level, rank, position, loadout, free_agent, set_private]
});

group!({
    name: "player",
    options: {
        prefixes: ["p", "player"]
    },
    commands: [new],
    sub_groups: [update]
});

fn main() {
    dotenv().ok();
    pretty_env_logger::init_timed();

    let token = match env::var("PRISBOT_TOKEN") {
        Ok(v) => v,
        Err(e) => panic!(
            "Could not retrieve environment variable `PRISBOT_TOKEN`: {:#?}",
            e
        ),
    };
    let dbl_token = match env::var("PRISBOT_API_TOKEN") {
        Ok(v) => v,
        Err(e) => panic!(
            "Could not retrieve environment variable `PRISBOT_API_TOKEN`: {:#?}",
            e
        ),
    };
    info!("Tokens acquired!");

    let mut client = Client::new(&token, Handler).expect("Failed to create client");

    let req_client = Arc::new(ReqwestClient::new());
    let api_client = APIClient::new(Arc::clone(&req_client));

    {
        let mut data = client.data.write();
        data.insert::<ShardManagerContainer>(Arc::clone(&client.shard_manager));
        data.insert::<APIClientContainer>(api_client);
        data.insert::<TokenHolder>(dbl_token.to_string());
    }

    let (owners, bot_id) = match client.cache_and_http.http.get_current_application_info() {
        Ok(info) => {
            let mut owners = HashSet::new();
            owners.insert(info.owner.id);
            (owners, info.id)
        }
        Err(why) => panic!("Could not access application info: {:?}", why),
    };
    info!("Owner/bot info retrieved!");

    client.with_framework(
        StandardFramework::new()
            .configure(|c| c.owners(owners).on_mention(Some(bot_id)).prefix("pc."))
            .group(&SUDO_GROUP)
            .group(&PLAYER_GROUP),
    );
    info!("Framework prepared!");

    if let Err(why) = client.start() {
        error!("Uncaught Exception: {:#?}", why);
    }
}
