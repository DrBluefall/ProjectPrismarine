#[macro_use]
extern crate serde; // Serialization and deserialization of JSON from DB into structs
extern crate serde_json; // JSON support of serde
extern crate dotenv; // Get environment variables from .env files.
extern crate discord_bots_org; // DBL API Wrapper. Used with Reqwest.
extern crate reqwest; // Used with discord_bots_org for dispatching to DBL
#[macro_use]
extern crate log; // logging crate
extern crate pretty_env_logger; // nicer logging
#[macro_use]
extern crate postgres;
#[macro_use]
extern crate postgres_derive;

use discord_bots_org::ReqwestSyncClient as APIClient; // Used to update discordbots.org
use dotenv::dotenv; // used to load .env files from directory.
use reqwest::Client as ReqwestClient;
use serenity::{ // Library for Discord. The central library for this bot.
    client::bridge::gateway::ShardManager,
    framework::{standard::macros::group, StandardFramework},
    model::{event::ResumedEvent, gateway::Ready},
    prelude::*,
};
use std::{collections::HashSet, sync::{Arc, Mutex as STDMutex}};
use std::env;
use postgres::{Connection, TlsMode};


// Declare modules for use
mod modules;
mod utils;
// Import the commands to put them into their groups
use modules::sudo::*;
use modules::player::*;

// Various holders to be carried across modules.
struct ShardManagerContainer;
struct APIClientContainer;
struct TokenHolder;
struct ConnectionHolder;
impl TypeMapKey for ShardManagerContainer { type Value = Arc<Mutex<ShardManager>>; }
impl TypeMapKey for APIClientContainer { type Value = APIClient; }
impl TypeMapKey for TokenHolder { type Value = String; }
impl TypeMapKey for ConnectionHolder { type Value = Arc<STDMutex<Connection>>; }

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
    name: "player",
    options: {
        prefixes: ["p", "player"]
    },
    commands: [new]
});

fn main() {
    dotenv().ok();
    pretty_env_logger::init_timed();

    let token = match env::var("PRISBOT_TOKEN") {
        Ok(v) => v,
        Err(e) => panic!(
            "Could not retrieve environment variable `PRISBOT_TOKEN`: {:#?}", e
        ),
    };
    let dbl_token = match env::var("PRISBOT_API_TOKEN") {
        Ok(v) => v,
        Err(e) => panic!(
            "Could not retrieve environment variable `PRISBOT_API_TOKEN`: {:#?}", e
        ),
    };
    let db_link = match env::var("PRISBOT_DATABASE") {
        Ok(v) => v,
        Err(e) => panic!(
            "Could not retrieve environment variable `PRISBOT_DATABASE`: {:#?}", e
        ),
    };
    info!("Tokens acquired!");

    let mut client = Client::new(&token, Handler)
        .expect("Failed to create client");

    let req_client = Arc::new(ReqwestClient::new());
    let api_client = APIClient::new(Arc::clone(&req_client));
    let conn = Connection::connect(db_link.as_str(), TlsMode::None)
        .unwrap_or_else(|err| {panic!("Failed to connect to database: {:#?}", err)});

    {
        let mut data = client.data.write();
        data.insert::<ShardManagerContainer>(Arc::clone(&client.shard_manager));
        data.insert::<APIClientContainer>(api_client);
        data.insert::<TokenHolder>(dbl_token.to_string());
        data.insert::<ConnectionHolder>(Arc::new(STDMutex::new(conn)));
    }

    let (owners, bot_id) =
        match client.cache_and_http.http.get_current_application_info() {
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
            .configure(|c|
                c.owners(owners)
                .on_mention(Some(bot_id)).prefix("pc.")
            )
            .group(&SUDO_GROUP)
            .group(&PLAYER_GROUP),
    );
    info!("Framework prepared!");

    if let Err(why) = client.start() {
        error!("Uncaught Exception: {:#?}", why);
    }
}
