extern crate pretty_env_logger;
#[macro_use]
extern crate log;
mod modules;
use std::{
    collections::HashSet,
    env,
    sync::Arc,
};

use serenity::{
    client::bridge::gateway::ShardManager,
    framework::{
        StandardFramework,
        standard::macros::group,
    },
    model::{event::ResumedEvent, gateway::Ready},
    prelude::*,
};
use modules::{
    sudo::*
};

struct ShardManagerContainer;

impl TypeMapKey for ShardManagerContainer {
    type Value = Arc<Mutex<ShardManager>>;
}

struct Handler;

impl EventHandler for Handler {
    fn ready(&self, _: Context, ready: Ready) {
        info!("\x1b[1m{}#{} is \x1b[38;5;082monline!\x1b[0m", ready.user.name, ready.user.discriminator);
    }
    fn resume(&self, _ctx: Context, _: ResumedEvent) {

    }
}

group!({
    name: "sudo",
    options: {
        prefix: "sudo",
        owners_only: true
    },
    commands: [logout, latency]
});

fn main() {
    println!("Hello, world!");
    
    pretty_env_logger::init_timed();

    let token = env::var("PRISBOT_TOKEN").expect("Expected environment variable `PRISBOT_TOKEN` to be set");
    info!("Token acquired!");

    let mut client = Client::new(&token, Handler).expect("Failed to create client");

    {
        let mut data = client.data.write();
        data.insert::<ShardManagerContainer>(Arc::clone(&client.shard_manager));
    }

    let (owners, bot_id) = match client.cache_and_http.http.get_current_application_info() {
        Ok(info) => {
            let mut owners = HashSet::new();
            owners.insert(info.owner.id);

            (owners, info.id)
        },
        Err(why) => panic!("Could not access application info: {:?}", why),
    };
    info!("Owner/bot info retrieved!");

    client.with_framework(StandardFramework::new()
        .configure(|c| c
            .owners(owners)
            .on_mention(Some(bot_id))
            .prefix("pc."))
        .group(&SUDO_GROUP));
    info!("Framework prepared!");
    
    if let Err(why) = client.start() {
        error!("Uncaught Exception: {:#?}", why);
    }

}
