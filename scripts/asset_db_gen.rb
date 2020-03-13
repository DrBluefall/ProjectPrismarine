#!/usr/bin/ruby
# NOTE: This file must be run from the `scripts/` directory!

require "mysql2"
require "json"

# Just some assert code :3
class AssertionError < RuntimeError
end

def assert &block
    raise AssertionError unless yield
end

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

def read_gear(geartype)
  db = get_db
  itemfile = readjson "#{geartype}.json"
  short_val = nil # Range for the image path to be shortened by, since it's different depending on the gear type.
  case geartype
  when "headgear"
    short_val = 31
  when "clothing"
    short_val = 34
  when "shoes"
    short_val = 32
  end

  assert { short_val != nil }

  begin
    itemfile.each do |item|
      stat "Inserting '#{geartype}'... [On item #{item['name']}]"
      main = "NULL"
      if item['main'] != nil
        main = "\"#{db.escape item['main']}\""
      end
      db.query "
      INSERT IGNORE INTO prismarine_rusted.#{geartype} (
        name,
        image,
        localized_name,
        main,
        stars,
        id,
        splatnet
      ) VALUES (
        \"#{db.escape item['name']}\",
        \"#{db.escape "assets/img/gear/#{item['image']}"}\",
        \"#{db.escape JSON.generate item['localizedName']}\",
        #{main},
        #{item['stars']},
        #{item['id']},
        #{item['splatnet']}
      )
      "
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

def read_abilities
  db = get_db
  abilityfile = readjson "skills.json"
  begin
    abilityfile.each do |ability|
      db.query "
        INSERT IGNORE INTO prismarine_rusted.abilities (
          name,
          localized_name,
          image,
          id
        ) VALUES (
          \"#{db.escape ability['name']}\",
          \"#{db.escape JSON.generate ability['localized_name']}\",
          \"#{db.escape "assets/img/skills/#{ability['image'][28..-1]}"}\",
          #{ability['id']}
        )
      "
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
    stat "All sub weapons read!\n"
    read_specials
    stat "All specials read!\n"
    read_weapons
    stat "All weapons read!\n"
    read_gear "headgear"
    stat "All headgear read!\n"
    read_gear "shoes"
    stat "All shoes read!\n"
    read_gear "clothing"
    stat "All clothes read!\n"
    read_abilities
    stat "All abilites read!\n"
  end
  puts "\033[1;92mAll data read into the database! Cheers!\033[m"
end

main
