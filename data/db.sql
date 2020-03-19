-- MariaDB dump 10.17  Distrib 10.4.12-MariaDB, for Linux (x86_64)
--
-- Host: localhost    Database: prismarine_rusted
-- ------------------------------------------------------
-- Server version: 10.4.12-MariaDB
-- ------------------------------------------------------
-- Command used: mysqldump prismarine_rusted -d -p >! data/db.sql
-- ------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `abilities`
--

DROP TABLE IF EXISTS `abilities`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `abilities` (
  `name` varchar(50) COLLATE utf8_bin DEFAULT NULL,
  `localized_name` varchar(50) COLLATE utf8_bin DEFAULT NULL,
  `image` varchar(150) CHARACTER SET utf8 DEFAULT NULL,
  `id` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `clothing`
--

DROP TABLE IF EXISTS `clothing`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `clothing` (
  `name` varchar(50) COLLATE utf8_bin DEFAULT NULL,
  `image` varchar(150) CHARACTER SET utf8 DEFAULT NULL,
  `localized_name` varchar(50) COLLATE utf8_bin DEFAULT NULL,
  `main` varchar(50) COLLATE utf8_bin DEFAULT NULL,
  `stars` int(11) DEFAULT NULL,
  `id` int(11) DEFAULT NULL,
  `splatnet` int(11) NOT NULL,
  PRIMARY KEY (`splatnet`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `headgear`
--

DROP TABLE IF EXISTS `headgear`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `headgear` (
  `name` varchar(50) COLLATE utf8_bin DEFAULT NULL,
  `image` varchar(150) CHARACTER SET utf8 DEFAULT NULL,
  `localized_name` varchar(50) COLLATE utf8_bin DEFAULT NULL,
  `main` varchar(50) COLLATE utf8_bin DEFAULT NULL,
  `stars` int(11) DEFAULT NULL,
  `id` int(11) DEFAULT NULL,
  `splatnet` int(11) NOT NULL,
  PRIMARY KEY (`splatnet`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `main_weapons`
--

DROP TABLE IF EXISTS `main_weapons`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `main_weapons` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) COLLATE utf8_bin DEFAULT NULL,
  `image` varchar(125) COLLATE utf8_bin DEFAULT NULL,
  `class` int(11) DEFAULT NULL,
  `localized_name` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`localized_name`)),
  `sub` varchar(50) COLLATE utf8_bin DEFAULT NULL,
  `special` varchar(50) COLLATE utf8_bin DEFAULT NULL,
  `site_id` varchar(45) COLLATE utf8_bin DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `main_weapons_special_fkey_idx` (`special`),
  KEY `main_weapons_sub_fkey_idx` (`sub`),
  CONSTRAINT `main_weapons_special_fkey` FOREIGN KEY (`special`) REFERENCES `special_weapons` (`name`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `main_weapons_sub_fkey` FOREIGN KEY (`sub`) REFERENCES `sub_weapons` (`name`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=140 DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `player_profiles`
--

DROP TABLE IF EXISTS `player_profiles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `player_profiles` (
  `id` bigint(20) NOT NULL,
  `friend_code` char(17) COLLATE utf8_bin DEFAULT 'SW-XXXX-XXXX-XXXX',
  `ign` varchar(10) COLLATE utf8_bin DEFAULT 'Unset!',
  `level` int(11) DEFAULT 1,
  `sz` varchar(6) COLLATE utf8_bin DEFAULT 'C-',
  `tc` varchar(6) COLLATE utf8_bin DEFAULT 'C-',
  `rm` varchar(6) COLLATE utf8_bin DEFAULT 'C-',
  `cb` varchar(6) COLLATE utf8_bin DEFAULT 'C-',
  `sr` varchar(13) COLLATE utf8_bin DEFAULT 'Intern',
  `position` smallint(6) DEFAULT 0,
  `loadout` varchar(50) COLLATE utf8_bin DEFAULT '0000000000000000000000000',
  `team_id` bigint(20) DEFAULT NULL,
  `freeagent` tinyint(1) DEFAULT 0,
  `is_private` tinyint(1) DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `player_profile_id_fkey` (`team_id`),
  CONSTRAINT `player_profile_id_fkey` FOREIGN KEY (`team_id`) REFERENCES `team_profiles` (`captain`) ON DELETE SET NULL ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `scrims`
--

DROP TABLE IF EXISTS `scrims`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `scrims` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `team_alpha` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`team_alpha`)),
  `captain_alpha` bigint(20) NOT NULL,
  `team_bravo` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`team_bravo`)),
  `captain_bravo` bigint(20) NOT NULL,
  `status` smallint(6) DEFAULT 0,
  `register_time` bigint(20) DEFAULT NULL,
  `expire_time` bigint(20) DEFAULT NULL,
  `details` varchar(250) COLLATE utf8_bin DEFAULT NULL,
  `alpha_role_id` bigint(20) DEFAULT NULL,
  `bravo_role_id` bigint(20) DEFAULT NULL,
  `channel_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `captain_alpha_UNIQUE` (`captain_alpha`),
  UNIQUE KEY `captain_bravo_UNIQUE` (`captain_bravo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `shoes`
--

DROP TABLE IF EXISTS `shoes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `shoes` (
  `name` varchar(50) COLLATE utf8_bin NOT NULL,
  `image` varchar(150) COLLATE utf8_bin DEFAULT NULL,
  `localized_name` varchar(50) CHARACTER SET utf8 DEFAULT NULL,
  `main` varchar(50) COLLATE utf8_bin DEFAULT NULL,
  `stars` int(11) DEFAULT NULL,
  `id` int(11) DEFAULT NULL,
  `splatnet` int(11) NOT NULL,
  PRIMARY KEY (`name`,`splatnet`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `special_weapons`
--

DROP TABLE IF EXISTS `special_weapons`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `special_weapons` (
  `name` varchar(50) COLLATE utf8_bin NOT NULL,
  `localized_name` varchar(50) COLLATE utf8_bin DEFAULT NULL,
  `image` varchar(150) COLLATE utf8_bin DEFAULT NULL,
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sub_weapons`
--

DROP TABLE IF EXISTS `sub_weapons`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sub_weapons` (
  `name` varchar(50) COLLATE utf8_bin NOT NULL,
  `localized_name` varchar(50) COLLATE utf8_bin DEFAULT NULL,
  `image` varchar(150) COLLATE utf8_bin DEFAULT NULL,
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `team_profiles`
--

DROP TABLE IF EXISTS `team_profiles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `team_profiles` (
  `captain` bigint(20) NOT NULL,
  `name` varchar(100) COLLATE utf8_bin DEFAULT 'The Default Team',
  `deletion_time` bigint(20) DEFAULT NULL,
  `description` varchar(250) COLLATE utf8_bin DEFAULT 'This team is a mystery...',
  `thumbnail` varchar(150) COLLATE utf8_bin DEFAULT NULL,
  `creation_time` varchar(45) COLLATE utf8_bin DEFAULT NULL,
  `recruiting` tinyint(1) DEFAULT 0,
  `recent_tournaments` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`recent_tournaments`)),
  PRIMARY KEY (`captain`),
  CONSTRAINT `team_profile_id_fkey` FOREIGN KEY (`captain`) REFERENCES `player_profiles` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2020-03-19 11:25:47
