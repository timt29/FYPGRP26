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
-- Table structure for table `articles`
--

DROP TABLE IF EXISTS `articles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `articles` (
  `articleID` int NOT NULL AUTO_INCREMENT,
  `title` varchar(255) NOT NULL,
  `content` mediumtext,
  `author` varchar(45) DEFAULT NULL,
  `published_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `image` mediumblob,
  PRIMARY KEY (`articleID`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `articles`
--

LOCK TABLES `articles` WRITE;
/*!40000 ALTER TABLE `articles` DISABLE KEYS */;
INSERT INTO `articles` VALUES (1,'Woman charged over possessing almost 200 etomidate-laced vapes, buying another 50','SINGAPORE – A woman was charged over possessing 195 etomidate-laced vapes, or Kpods, and buying another 50 such pods on separate occasions in 2024. On Sept 4, Law Jia Yi, 23, was handed five charges in relation to vapes. She was also charged over possessing a knife with a 20cm-long blade, a card knife and a screwdriver without lawful purposes in August 2024 at a carpark in Yishun. For Law’s vape-related charges, she allegedly had 55 Kpods and four vapes in Yishun Avenue 5 on Aug 9, 2024. That month, she also purportedly bought 50 Kpods in Geylang. It was not stated in court documents where or whom she bought them from. Separately, Law is accused of possessing 49 vape pods in Yishun, which were later analysed and found to contain etomidate. Law also allegedly had 98 vape pods and two vapes in Sentosa, in Siloso Road. She is also said to have had 91 Kpods at the same location. Law’s case has been scheduled for a pre-trial conference on Sept 11. On Sept 3, a 17-year-old boy was charged with possessing a vape device containing a cannabis-related substance. In his National Day Rally speech in August, Prime Minister Lawrence Wong said the Government will treat vaping as a drug issue and impose stiffer penalties. Since Sept 1, first-time etomidate abusers below 18 years old will be fined $500, while adults will be fined $700. This is a $200 increase for each group. They must also attend mandatory rehabilitation for up to six months. Sellers of Kpods will face higher penalties under the Misuse of Drugs Act. Those who import Kpods will face between three and 20 years’ jail, and between five and 15 strokes of the cane. Those convicted of selling or distributing Kpods will face between two and 10 years’ jail, and receive between two and five strokes of the cane. The public can report vaping offences to the Tobacco Regulation Branch on 6684-2036 or 6684-2037 from 9am to 9pm daily, or online at go.gov.sg/reportvape Those using Kpods can seek help through a national programme called QuitVape. More information on vaping can be found at gov.sg/stopvaping, a microsite launched in August to consolidate resources, helplines and reporting avenues. The authorities have said that those who voluntarily seek support to quit vaping will not face any penalties for doing so.','Nadine Chua','2025-09-04 17:45:00','2025-09-05 00:16:00',NULL);
/*!40000 ALTER TABLE `articles` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-09-24 18:08:08
