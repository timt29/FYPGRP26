-- MySQL dump 10.13  Distrib 8.0.43, for Win64 (x86_64)
--
-- Host: localhost    Database: nrs
-- ------------------------------------------------------
-- Server version	8.0.43

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
-- Table structure for table `login_activity`
--

DROP TABLE IF EXISTS `login_activity`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `login_activity` (
  `activityID` int NOT NULL AUTO_INCREMENT,
  `userid` int NOT NULL,
  `email` varchar(255) NOT NULL,
  `login_time` datetime DEFAULT CURRENT_TIMESTAMP,
  `ip_address` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`activityID`),
  KEY `userid` (`userid`),
  CONSTRAINT `login_activity_ibfk_1` FOREIGN KEY (`userid`) REFERENCES `users` (`userid`)
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `login_activity`
--

LOCK TABLES `login_activity` WRITE;
/*!40000 ALTER TABLE `login_activity` DISABLE KEYS */;
INSERT INTO `login_activity` VALUES (1,10,'random@gmail.com','2025-10-06 02:47:59','127.0.0.1'),(2,1,'alice@example.com','2025-10-06 02:49:21','127.0.0.1'),(3,1,'alice@example.com','2025-10-06 02:52:42','127.0.0.1'),(4,2,'mike@example.com','2025-10-06 02:53:32','127.0.0.1'),(5,3,'sam@example.com','2025-10-06 02:53:42','127.0.0.1'),(6,9,'allah@example.com','2025-10-06 02:54:00','127.0.0.1'),(7,8,'dog@example.com','2025-10-06 02:54:10','127.0.0.1'),(8,1,'alice@example.com','2025-10-06 02:54:15','127.0.0.1'),(9,4,'amy@example.com','2025-10-06 02:54:26','127.0.0.1'),(10,5,'tim@example.com','2025-10-06 02:54:49','127.0.0.1'),(11,1,'alice@example.com','2025-10-06 02:55:01','127.0.0.1'),(12,1,'alice@example.com','2025-10-06 02:56:11','127.0.0.1'),(13,12,'nc@123.com','2025-10-16 20:59:36','127.0.0.1'),(14,12,'nc@123.com','2025-10-16 21:02:27','127.0.0.1'),(15,12,'nc@123.com','2025-10-16 21:07:03','127.0.0.1'),(16,12,'nc@123.com','2025-10-16 21:09:18','127.0.0.1'),(17,12,'nc@123.com','2025-10-16 21:11:57','127.0.0.1'),(18,12,'nc@123.com','2025-10-16 21:14:10','127.0.0.1'),(19,12,'nc@123.com','2025-10-16 21:16:52','127.0.0.1'),(20,12,'nc@123.com','2025-10-16 21:18:18','127.0.0.1'),(21,12,'nc@123.com','2025-10-16 21:19:15','127.0.0.1'),(22,12,'nc@123.com','2025-10-16 21:19:43','127.0.0.1'),(23,12,'nc@123.com','2025-10-16 21:24:00','127.0.0.1'),(24,12,'nc@123.com','2025-10-16 21:26:03','127.0.0.1'),(25,12,'nc@123.com','2025-10-16 21:27:52','127.0.0.1'),(26,12,'nc@123.com','2025-10-16 21:30:03','127.0.0.1'),(27,12,'nc@123.com','2025-10-16 21:33:59','127.0.0.1'),(28,12,'nc@123.com','2025-10-16 21:49:52','127.0.0.1');
/*!40000 ALTER TABLE `login_activity` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-10-16 21:51:07
