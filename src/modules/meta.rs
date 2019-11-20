use serenity::{
    framework::standard::{
        CommandResult,
        CommandGroup,
        HelpOptions,
        Args,
        help_commands,
        macros::help
    },
    model::prelude::*,
    prelude::Context
};
use std::collections::HashSet;

#[help]
fn assist(
    ctx: &mut Context,
    msg: &Message,
    args: Args,
    help_options: &'static HelpOptions,
    groups: &[&'static CommandGroup],
    owners: HashSet<UserId>
) -> CommandResult {
    help_commands::with_embeds(ctx, msg, args, help_options, groups, owners)
}