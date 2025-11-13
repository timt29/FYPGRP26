-- MySQL dump 10.13  Distrib 8.0.42, for Win64 (x86_64)
--
-- Host: localhost    Database: nrs
-- ------------------------------------------------------
-- Server version	8.0.42

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `warnings`
--

DROP TABLE IF EXISTS `warnings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `warnings` (
  `warningID` int NOT NULL AUTO_INCREMENT,
  `userID` int NOT NULL,
  `message` varchar(255) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `notification` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`warningID`)
) ENGINE=InnoDB AUTO_INCREMENT=31 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `warnings`
--

LOCK TABLES `warnings` WRITE;
/*!40000 ALTER TABLE `warnings` DISABLE KEYS */;
INSERT INTO `warnings` VALUES (17,4,'You have received a warning from the moderator.','2025-11-12 15:40:41',0),(18,4,'You have received a warning from the moderator.','2025-11-12 15:45:23',0),(19,4,'You have received a warning from the moderator.','2025-11-12 15:45:24',0),(20,4,'You have received a warning from the moderator.','2025-11-12 15:45:25',0),(21,4,'You have received a warning from the moderator.','2025-11-12 15:45:26',0),(22,4,'You have received a warning from the moderator.','2025-11-12 15:45:26',0),(23,4,'You have received a warning from the moderator.','2025-11-12 15:45:26',0),(24,4,'You have received a warning from the moderator.','2025-11-12 15:45:27',0),(25,4,'You have received a warning from the moderator.','2025-11-12 15:45:27',0),(26,4,'You have received a warning from the moderator.','2025-11-12 15:45:27',0),(27,4,'You have received a warning from the moderator.','2025-11-12 15:45:27',0),(28,4,'You have received a warning from the moderator.','2025-11-12 15:45:27',0),(29,4,'You have received a warning from the moderator.','2025-11-12 15:45:27',0),(30,4,'You have received a warning from the moderator.','2025-11-12 15:45:27',0);
/*!40000 ALTER TABLE `warnings` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-11-13 17:15:19
