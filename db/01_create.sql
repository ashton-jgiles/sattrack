-- MySQL dump 10.13  Distrib 8.0.19, for Win64 (x86_64)
--
-- Host: localhost    Database: sattrack
-- ------------------------------------------------------
-- Server version	8.0.45

CREATE DATABASE IF NOT EXISTS sattrack;

USE sattrack;

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `administrator`
--

DROP TABLE IF EXISTS `administrator`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `administrator` (
  `username` varchar(50) NOT NULL,
  `employee_id` int NOT NULL,
  PRIMARY KEY (`username`),
  CONSTRAINT `administrator_ibfk_1` FOREIGN KEY (`username`) REFERENCES `user` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `amateur`
--

DROP TABLE IF EXISTS `amateur`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `amateur` (
  `username` varchar(50) NOT NULL,
  `interests` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`username`),
  CONSTRAINT `amateur_ibfk_1` FOREIGN KEY (`username`) REFERENCES `user` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `communicates_with`
--

DROP TABLE IF EXISTS `communicates_with`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `communicates_with` (
  `location` varchar(100) NOT NULL,
  `satellite_id` int NOT NULL,
  PRIMARY KEY (`location`,`satellite_id`),
  KEY `satellite_id` (`satellite_id`),
  CONSTRAINT `communicates_with_ibfk_1` FOREIGN KEY (`location`) REFERENCES `communication_station` (`location`),
  CONSTRAINT `communicates_with_ibfk_2` FOREIGN KEY (`satellite_id`) REFERENCES `satellite` (`satellite_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `communication_station`
--

DROP TABLE IF EXISTS `communication_station`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `communication_station` (
  `location` varchar(100) NOT NULL,
  `name` varchar(100) NOT NULL,
  `communication_frequency` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`location`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `data_analyst`
--

DROP TABLE IF EXISTS `data_analyst`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `data_analyst` (
  `username` varchar(50) NOT NULL,
  `employee_id` int NOT NULL,
  PRIMARY KEY (`username`),
  CONSTRAINT `data_analyst_ibfk_1` FOREIGN KEY (`username`) REFERENCES `user` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dataset`
--

DROP TABLE IF EXISTS `dataset`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dataset` (
  `dataset_id` int NOT NULL AUTO_INCREMENT,
  `dataset_name` varchar(150) NOT NULL,
  `description` text,
  `creation_date` date NOT NULL,
  `file_size` varchar(20) DEFAULT NULL,
  `source` varchar(50) NOT NULL,
  `source_url` varchar(500) NOT NULL,
  `pull_frequency` varchar(20) DEFAULT NULL,
  `last_pulled` datetime DEFAULT NULL,
  `review_status` varchar(10) NOT NULL DEFAULT 'pending',
  PRIMARY KEY (`dataset_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `deploys_payload`
--

DROP TABLE IF EXISTS `deploys_payload`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `deploys_payload` (
  `vehicle_id` int NOT NULL,
  `satellite_id` int NOT NULL,
  `deploy_date_time` datetime NOT NULL,
  PRIMARY KEY (`vehicle_id`,`satellite_id`),
  KEY `satellite_id` (`satellite_id`),
  CONSTRAINT `deploys_payload_ibfk_1` FOREIGN KEY (`vehicle_id`) REFERENCES `launch_vehicle` (`vehicle_id`),
  CONSTRAINT `deploys_payload_ibfk_2` FOREIGN KEY (`satellite_id`) REFERENCES `satellite` (`satellite_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `earth_science`
--

DROP TABLE IF EXISTS `earth_science`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `earth_science` (
  `satellite_id` int NOT NULL,
  `timestamp` datetime NOT NULL,
  `land_surface_temp` decimal(8,4) NOT NULL,
  `emissivity` decimal(6,4) DEFAULT NULL,
  `quality_flag` varchar(10) DEFAULT NULL,
  `instrument` varchar(50) NOT NULL,
  `lst_unit` varchar(10) NOT NULL DEFAULT 'Kelvin',
  PRIMARY KEY (`satellite_id`,`timestamp`),
  CONSTRAINT `earth_science_ibfk_1` FOREIGN KEY (`satellite_id`) REFERENCES `satellite` (`satellite_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `internet`
--

DROP TABLE IF EXISTS `internet`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `internet` (
  `satellite_id` int NOT NULL,
  `coverage` text,
  `frequency_band` varchar(20) DEFAULT NULL,
  `service_type` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`satellite_id`),
  CONSTRAINT `internet_ibfk_1` FOREIGN KEY (`satellite_id`) REFERENCES `satellite` (`satellite_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `launch_site`
--

DROP TABLE IF EXISTS `launch_site`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `launch_site` (
  `location` varchar(100) NOT NULL,
  `weather` varchar(100) DEFAULT NULL,
  `site_name` varchar(150) DEFAULT NULL,
  `country` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`location`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `launch_vehicle`
--

DROP TABLE IF EXISTS `launch_vehicle`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `launch_vehicle` (
  `vehicle_id` int NOT NULL AUTO_INCREMENT,
  `vehicle_name` varchar(100) NOT NULL,
  `manufacturer` varchar(100) DEFAULT NULL,
  `reusable` tinyint(1) DEFAULT NULL,
  `country` varchar(100) DEFAULT NULL,
  `payload_capacity` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`vehicle_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `launched_from`
--

DROP TABLE IF EXISTS `launched_from`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `launched_from` (
  `vehicle_id` int NOT NULL,
  `location` varchar(100) NOT NULL,
  `launch_date` date NOT NULL,
  PRIMARY KEY (`vehicle_id`,`location`,`launch_date`),
  KEY `location` (`location`),
  CONSTRAINT `launched_from_ibfk_1` FOREIGN KEY (`vehicle_id`) REFERENCES `launch_vehicle` (`vehicle_id`),
  CONSTRAINT `launched_from_ibfk_2` FOREIGN KEY (`location`) REFERENCES `launch_site` (`location`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `navigation`
--

DROP TABLE IF EXISTS `navigation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `navigation` (
  `satellite_id` int NOT NULL,
  `constellation` varchar(50) NOT NULL,
  `signal_type` varchar(50) DEFAULT NULL,
  `accuracy` decimal(8,2) DEFAULT NULL,
  PRIMARY KEY (`satellite_id`),
  CONSTRAINT `navigation_ibfk_1` FOREIGN KEY (`satellite_id`) REFERENCES `satellite` (`satellite_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `oceanic_science`
--

DROP TABLE IF EXISTS `oceanic_science`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oceanic_science` (
  `satellite_id` int NOT NULL,
  `timestamp` datetime NOT NULL,
  `sst` decimal(8,4) NOT NULL,
  `sst_anomaly` decimal(8,4) DEFAULT NULL,
  `instrument` varchar(50) NOT NULL,
  `sst_unit` varchar(10) NOT NULL DEFAULT 'Celsius',
  PRIMARY KEY (`satellite_id`,`timestamp`),
  CONSTRAINT `oceanic_science_ibfk_1` FOREIGN KEY (`satellite_id`) REFERENCES `satellite` (`satellite_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `research`
--

DROP TABLE IF EXISTS `research`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `research` (
  `satellite_id` int NOT NULL,
  `research_field` varchar(100) NOT NULL,
  `instrument` varchar(100) DEFAULT NULL,
  `wavelength_band` varchar(50) DEFAULT NULL,
  `data_archive_url` varchar(500) DEFAULT NULL,
  `mission_status` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`satellite_id`),
  CONSTRAINT `research_ibfk_1` FOREIGN KEY (`satellite_id`) REFERENCES `satellite` (`satellite_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `reviews`
--

DROP TABLE IF EXISTS `reviews`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `reviews` (
  `reviewed_by` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `dataset_id` int NOT NULL,
  `reviewed_at` datetime NOT NULL,
  PRIMARY KEY (`reviewed_by`,`dataset_id`),
  KEY `dataset_id` (`dataset_id`),
  CONSTRAINT `reviews_ibfk_1` FOREIGN KEY (`reviewed_by`) REFERENCES `data_analyst` (`username`),
  CONSTRAINT `reviews_ibfk_2` FOREIGN KEY (`dataset_id`) REFERENCES `dataset` (`dataset_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `satellite`
--

DROP TABLE IF EXISTS `satellite`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `satellite` (
  `satellite_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `description` text,
  `last_contact_time` datetime DEFAULT NULL,
  `owner_id` int DEFAULT NULL,
  `dataset_id` int NOT NULL,
  `username` varchar(50) DEFAULT NULL,
  `orbit_type` varchar(10) NOT NULL,
  `norad_id` varchar(10) DEFAULT NULL,
  `object_id` varchar(20) DEFAULT NULL,
  `classification` varchar(1) NOT NULL DEFAULT 'U',
  PRIMARY KEY (`satellite_id`),
  KEY `owner_id` (`owner_id`),
  KEY `dataset_id` (`dataset_id`),
  KEY `username` (`username`),
  CONSTRAINT `satellite_ibfk_1` FOREIGN KEY (`owner_id`) REFERENCES `satellite_owner` (`owner_id`),
  CONSTRAINT `satellite_ibfk_2` FOREIGN KEY (`dataset_id`) REFERENCES `dataset` (`dataset_id`),
  CONSTRAINT `satellite_ibfk_3` FOREIGN KEY (`username`) REFERENCES `user` (`username`),
  CONSTRAINT `satellite_chk_1` CHECK ((`orbit_type` in (_utf8mb4'LEO',_utf8mb4'MEO',_utf8mb4'GEO',_utf8mb4'HEO')))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `satellite_owner`
--

DROP TABLE IF EXISTS `satellite_owner`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `satellite_owner` (
  `owner_id` int NOT NULL AUTO_INCREMENT,
  `owner_name` varchar(150) NOT NULL,
  `owner_phone` varchar(20) DEFAULT NULL,
  `owner_address` varchar(255) DEFAULT NULL,
  `country` varchar(100) DEFAULT NULL,
  `operator` varchar(150) DEFAULT NULL,
  `owner_type` varchar(15) DEFAULT NULL,
  PRIMARY KEY (`owner_id`),
  CONSTRAINT `satellite_owner_chk_1` CHECK ((`owner_type` in (_utf8mb4'government',_utf8mb4'commercial',_utf8mb4'military',_utf8mb4'academic')))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `scientist`
--

DROP TABLE IF EXISTS `scientist`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `scientist` (
  `username` varchar(50) NOT NULL,
  `profession` varchar(100) NOT NULL,
  PRIMARY KEY (`username`),
  CONSTRAINT `scientist_ibfk_1` FOREIGN KEY (`username`) REFERENCES `user` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `trajectory`
--

DROP TABLE IF EXISTS `trajectory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `trajectory` (
  `dataset_id` int NOT NULL,
  `satellite_id` int NOT NULL,
  `timestamp` datetime NOT NULL,
  `velocity` decimal(10,4) NOT NULL,
  `inclination` decimal(10,4) NOT NULL,
  `eccentricity` decimal(10,7) NOT NULL,
  `ra_of_asc_node` decimal(10,4) NOT NULL,
  `arg_of_pericenter` decimal(10,4) NOT NULL,
  `mean_anomaly` decimal(10,4) NOT NULL,
  `mean_motion` decimal(12,8) NOT NULL,
  `bstar` decimal(12,8) NOT NULL,
  `altitude` decimal(10,4) NOT NULL,
  `latitude` decimal(9,6) NOT NULL,
  `longitude` decimal(9,6) NOT NULL,
  PRIMARY KEY (`dataset_id`,`satellite_id`,`timestamp`),
  KEY `satellite_id` (`satellite_id`),
  CONSTRAINT `trajectory_ibfk_1` FOREIGN KEY (`dataset_id`) REFERENCES `dataset` (`dataset_id`),
  CONSTRAINT `trajectory_ibfk_2` FOREIGN KEY (`satellite_id`) REFERENCES `satellite` (`satellite_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `uploads`
--

DROP TABLE IF EXISTS `uploads`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `uploads` (
  `uploaded_by` varchar(50) NOT NULL,
  `dataset_id` int NOT NULL,
  `uploaded_at` datetime NOT NULL,
  PRIMARY KEY (`uploaded_by`,`dataset_id`),
  KEY `dataset_id` (`dataset_id`),
  CONSTRAINT `uploads_ibfk_1` FOREIGN KEY (`uploaded_by`) REFERENCES `administrator` (`username`),
  CONSTRAINT `uploads_ibfk_2` FOREIGN KEY (`dataset_id`) REFERENCES `dataset` (`dataset_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `full_name` varchar(100) NOT NULL,
  `level_access` int NOT NULL,
  PRIMARY KEY (`username`),
  CONSTRAINT `user_chk_1` CHECK ((`level_access` in (1,2,3,4)))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `views`
--

DROP TABLE IF EXISTS `views`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `views` (
  `username` varchar(50) NOT NULL,
  `dataset_id` int NOT NULL,
  `downloads` int NOT NULL DEFAULT '0',
  `views` int NOT NULL DEFAULT '0',
  `interaction_date` date NOT NULL,
  PRIMARY KEY (`username`,`dataset_id`,`interaction_date`),
  KEY `dataset_id` (`dataset_id`),
  CONSTRAINT `views_ibfk_1` FOREIGN KEY (`username`) REFERENCES `user` (`username`),
  CONSTRAINT `views_ibfk_2` FOREIGN KEY (`dataset_id`) REFERENCES `dataset` (`dataset_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `weather`
--

DROP TABLE IF EXISTS `weather`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `weather` (
  `satellite_id` int NOT NULL,
  `coverage_region` varchar(100) NOT NULL,
  `imaging_channels` int DEFAULT NULL,
  `repeat_cycle_min` int DEFAULT NULL,
  `instrument` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`satellite_id`),
  CONSTRAINT `weather_ibfk_1` FOREIGN KEY (`satellite_id`) REFERENCES `satellite` (`satellite_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping routines for database 'sattrack'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-03-13 11:21:34
