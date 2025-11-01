-- MySQL dump 10.13  Distrib 8.0.42, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: nrs
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
-- Table structure for table `comments`
--

DROP TABLE IF EXISTS `comments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `comments` (
  `commentid` int NOT NULL AUTO_INCREMENT,
  `articleid` int NOT NULL,
  `userid` int NOT NULL,
  `comment_text` text NOT NULL,
  `likes` int NOT NULL DEFAULT '0',
  `dislikes` int NOT NULL DEFAULT '0',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `is_reply` tinyint(1) NOT NULL DEFAULT '0',
  `reply_to_comment_id` int DEFAULT NULL,
  `visible` tinyint NOT NULL DEFAULT '1',
  PRIMARY KEY (`commentid`),
  KEY `idx_comments_articleID` (`articleid`),
  KEY `idx_comments_userID` (`userid`),
  KEY `idx_comments_parent` (`reply_to_comment_id`),
  CONSTRAINT `fk_comments_article` FOREIGN KEY (`articleid`) REFERENCES `articles` (`articleid`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_comments_parent` FOREIGN KEY (`reply_to_comment_id`) REFERENCES `comments` (`commentid`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_comments_user` FOREIGN KEY (`userid`) REFERENCES `users` (`userid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `comments`
--

LOCK TABLES `comments` WRITE;
/*!40000 ALTER TABLE `comments` DISABLE KEYS */;
INSERT INTO `comments` VALUES (1,1,1,'Seed comment #1 on article 1 by user 1',0,1,'2025-10-03 02:28:14',0,NULL,1),(2,2,2,'Seed comment #2 on article 2 by user 2',1,0,'2025-10-03 02:28:14',0,NULL,1),(3,3,3,'Seed comment #3 on article 3 by user 3',1,0,'2025-10-03 02:28:14',0,NULL,1),(4,4,4,'Seed comment #4 on article 4 by user 4',0,1,'2025-10-03 02:28:14',0,NULL,1),(5,5,5,'Seed comment #5 on article 5 by user 5',1,0,'2025-10-03 02:28:14',0,NULL,1),(6,1,1,'[SEED100-T001] Seed comment 1 on article 1 by user 1',0,0,'2025-10-03 02:31:22',0,NULL,1),(7,2,2,'[SEED100-T002] Seed comment 2 on article 2 by user 2',0,0,'2025-10-03 02:31:22',0,NULL,1),(8,3,3,'[SEED100-T003] Seed comment 3 on article 3 by user 3',0,0,'2025-10-03 02:31:22',0,NULL,1),(9,4,4,'[SEED100-T004] Seed comment 4 on article 4 by user 4',0,0,'2025-10-03 02:31:22',0,NULL,1),(10,5,10,'asda',0,0,'2025-10-05 11:22:00',0,NULL,1),(11,5,10,'testing',0,0,'2025-10-24 10:21:23',0,NULL,1),(12,5,10,'what the hell happened',0,0,'2025-10-24 10:21:38',0,NULL,1),(13,5,3,'lmao',0,0,'2025-10-24 10:22:08',0,NULL,1),(14,5,3,'lmao',0,0,'2025-10-24 10:22:08',0,NULL,1),(15,5,10,'@Sam hi sam this comment is damn funny',1,0,'2025-10-24 10:57:23',1,13,1),(16,5,10,'@random replying to myself is a feature too',0,0,'2025-10-24 10:57:59',1,12,1),(17,5,3,'@random thank you for your comment',0,0,'2025-10-24 11:01:03',1,13,1),(18,5,3,'@random testing nested comment',0,0,'2025-10-24 11:01:54',1,12,1);
/*!40000 ALTER TABLE `comments` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-11-01  8:53:40
