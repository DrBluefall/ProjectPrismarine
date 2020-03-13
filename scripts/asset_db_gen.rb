#!/usr/bin/ruby
# NOTE: This file must be run from the `scripts/` directory!

require "mysql2"
require "json"
require "pp"

def get_db
  host = ENV["ASSET_HOST"]
  uname = ENV["ASSET_USERNAME"]
  pwd = ENV["ASSET_PASSWD"]
  database = ENV["ASSET_DB_NAME"]

  return Mysql2::Client.new :host => host, :username => uname, :password => pwd, :database => database
end

def readjson(filename)
  return JSON.parse File.read filename
end

def stat(msg)
  print "\033[2K\r#{msg}"
end

def read_subs
  db = get_db
  subfile = readjson "subs.json"
  begin
    subfile.each do |sub|
      stat "Inserting 'sub weapons... [On sub `#{sub['name']}`]'"
      db.query "
        INSERT IGNORE INTO prismarine_rusted.sub_weapons (
          name,
          localized_name,
          image
        ) VALUES (
          \"#{db.escape sub['name']}\",
          \"#{db.escape JSON.generate sub['localized_name']}\",
          \"#{db.escape "assets/img/subs_specials/#{sub['image'][28..-1]}"}\"
        )
      "
    end
  rescue Mysql2::Error => e
    puts "ERROR while inserting subs..."
    puts "ERRNO: #{e.errno}"
    puts "SQLST: #{e.sql_state}"
    puts "ERMSG: #{e.error}"
  ensure
    db.close if db
  end
end

def read_specials
  db = get_db
  specfile = readjson "specials.json"
  begin
    specfile.each do |spec|
      stat "Inserting 'special weapons... [On special `#{spec['name']}`]'"
      db.query "
        INSERT IGNORE INTO prismarine_rusted.special_weapons (
          name,
          localized_name,
          image
        ) VALUES (
          \"#{db.escape spec['name']}\",
          \"#{db.escape JSON.generate spec['localized_name']}\",
          \"#{db.escape "assets/img/subs_specials/#{spec['image'][28..-1]}"}\"
        )
      "
    end
  rescue Mysql2::Error => e
    puts "ERROR while inserting specials..."
    puts "ERRNO: #{e.errno}"
    puts "SQLST: #{e.sql_state}"
    puts "ERMSG: #{e.error}"
  ensure
    db.close if db
  end
end

def read_weapons
  db = get_db
  weapon_file = readjson "weapons.json"
  begin
    weapon_file.each do |wep_class|
      wep_class['weapons'].each do |wep|
        stat "Inserting 'weapons'... [On class `#{wep['class']}`, wep `#{wep['name']}`]"
        db.query "
          INSERT IGNORE INTO prismarine_rusted.main_weapons 
          (name,
          image,
          class,
          localized_name,
          sub,
          special,
          site_id
          ) VALUES (
            \"#{db.escape wep['name']}\",
            \"#{db.escape "assets/img/weapons/#{wep['image'][29..-1]}"}\",
            \"#{wep_class['id']}\",
            \"#{db.escape JSON.generate wep['localizedName']}\",
            \"#{db.escape wep['sub']}\",
            \"#{db.escape wep['special']}\",
            \"#{wep['id']}\"
          )"
      end
    end
  rescue Mysql2::Error => e
    puts "ERROR while inserting weapons..."
    puts "ERRNO: #{e.errno}"
    puts "SQLST: #{e.sql_state}"
    puts "ERMSG: #{e.error}"
  ensure
    db.close if db
  end
end

def main

  Dir.chdir("../assets/data") do
    read_subs
    read_specials
    read_weapons

  end

end

main
