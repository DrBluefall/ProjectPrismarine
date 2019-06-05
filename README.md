PrismarineCo. Ltd. Presents...
# Project Prismarine!
An experimental moderation and Splatoon 2 discord bot!

## Dependencies:
- discord.py (1.1.0 or later)
- SQLAlchemy (1.3.4 or later)

## Running:
1. Create a `config.json` file in the project root directory.
2. Add the key `token` with your bot token string.
3. Add the key `owner` with your user ID integer.
4. Add the key `prefix` with the prefix of your choice.
5. Initialize the bot by running `core.py`.
6. Profit!

## TODO:
### Top Priority:
- [ ] Fix load, unload, and reload commands so that they actually work

### Planned for the Future:
- [ ] Implement loadout System
    - [ ] Decide on a means of getting loadouts into the bot (loadout.ink, through discord, or standalone app)
    - [ ] Design a way of how that info is to be displayed (probably using PIL in some way)
