-- MySQL dump 10.13  Distrib 8.0.42, for Win64 (x86_64)
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
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `userID` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `email` varchar(150) NOT NULL,
  `password` varchar(255) NOT NULL,
  `usertype` enum('Admin','Moderator','Subscriber','Author','Suspended') NOT NULL,
  `previous_usertype` varchar(50) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `is_logged_in` tinyint(1) DEFAULT '0',
  `image` varchar(255) DEFAULT NULL,
  `bio` text,
  `last_active` datetime DEFAULT NULL,
  PRIMARY KEY (`userID`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'Alice','alice@example.com','test','Admin',NULL,'2025-09-13 07:50:34',0,'../static/profilePictures/Alice.jpeg','Site administrator who oversees moderation, security and release workflows. Former newsroom ops lead; keeps the platform stable, fast and safe.','2025-10-06 02:56:40'),(2,'Mike','mike@example.com','test','Moderator',NULL,'2025-09-13 07:50:34',0,'../static/profilePictures/Mike.jpg','Community moderator focusing on guideline enforcement, spam takedowns and sensitive-content escalation. Runs weekly quality checks on report queues.','2025-10-06 02:53:36'),(3,'Sam','sam@example.com','test','Subscriber',NULL,'2025-09-13 07:50:34',0,'../static/profilePictures/Sam.jpg','Subscriber who follows technology, city policy and transport. Frequently submits tips and reader questions that spark explainer pieces.','2025-10-08 22:18:57'),(4,'Amy','amy@example.com','test','Author',NULL,'2025-09-13 07:50:34',1,'../static/profilePictures/Amy.jpg','Author covering lifestyle and culture—food, design and weekend guides. Previously wrote for a campus magazine and indie blogs.','2025-10-06 02:54:26'),(5,'Tim','tim@example.com','test1','Author',NULL,'2025-09-13 07:50:34',1,'../static/profilePictures/Tim.jpg','Data reporter building charts and short explainers. Breaks down budgets, transport changes and cost-of-living trends into readable visuals.','2025-10-06 02:54:49'),(7,'Ming','ming@example.com','test','Moderator',NULL,'2025-09-13 07:50:34',0,'../static/profilePictures/Ming.jpg','Moderator covering APAC hours. Bilingual reviewer who handles late-night queues, duplicate link clean-ups and tone checks on heated threads.',NULL),(8,'dog','dog@example.com','test','Moderator',NULL,'2025-09-13 07:50:34',0,'../static/profilePictures/Dog.jpg','Moderator and QA tester who automates common checks for new posts. Enjoys longform features and supports local animal rescue groups.','2025-10-06 02:54:12'),(9,'allah','allah@example.com','test','Moderator',NULL,'2025-09-13 12:26:22',0,'../static/profilePictures/Allah.jpg','Moderator focusing on link verification, source credibility and duplicate submissions. Helps keep discussions on-topic and civil.','2025-10-06 02:54:02'),(10,'random','random@gmail.com','test','Subscriber',NULL,'2025-09-25 11:30:24',0,'../static/profilePictures/Random.jpg','Subscriber who enjoys weekend longreads, photo essays and behind-the-scenes newsroom notes. Early tester of new notification features.','2025-10-06 02:49:18');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-10-08 22:42:54
