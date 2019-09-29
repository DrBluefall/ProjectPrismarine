#[macro_use]
extern crate dotenv_codegen;
extern crate discord_bots_org;
extern crate dotenv;
extern crate pretty_env_logger;
extern crate reqwest;
#[macro_use]
extern crate log;
mod modules;
use discord_bots_org::ReqwestSyncClient as APIClient;
use dotenv::dotenv;
use modules::sudo::*;
use reqwest::Client as ReqwestClient;
use serenity::{
    client::bridge::gateway::ShardManager,
    framework::{standard::macros::group, StandardFramework},
    model::{event::ResumedEvent, gateway::Ready},
    prelude::*,
};
use std::{collections::HashSet, sync::Arc};

struct ShardManagerContainer;
struct APIClientContainer;

impl TypeMapKey for ShardManagerContainer {
    type Value = Arc<Mutex<ShardManager>>;
}
impl TypeMapKey for APIClientContainer {
    type Value = APIClient;
}

struct TokenHolder;

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
    fn resume(&self, _ctx: Context, _: ResumedEvent) {}
}

group!({
    name: "sudo",
    options: {
        prefix: "sudo",
        owners_only: true
    },
    commands: [info, logout, latency, user, update_stats]
});

fn main() {
    dotenv().ok();
    pretty_env_logger::init_timed();

    let token = dotenv!("PRISBOT_TOKEN");
    let dbl_token = dotenv!("PRISBOT_API_TOKEN");
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
            .group(&SUDO_GROUP),
    );
    info!("Framework prepared!");

    if let Err(why) = client.start() {
        error!("Uncaught Exception: {:#?}", why);
    }
}
