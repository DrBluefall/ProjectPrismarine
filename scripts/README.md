
# IMPORTANT NOTE

Some scripts may need extra setup to be run, in addition to the main bot. They'll be documented below in this file.

- asset_db_gen.rb
  - Environment Variables
    - `ASSET_HOST` -> the host of your database (e.g. `localhost`)
    - `ASSET_PASSWD` -> the password to your database, if it needs one.
    - `ASSET_DB_NAME` -> the name of your database. should be the same one as the main bot.
    - `ASSET_USERNAME` -> The user you want to use to access the database (e.g. `idiot-toaster`, `root`, etc.)
  - Required Gems
    - `mysql2` (version 0.5.3)
