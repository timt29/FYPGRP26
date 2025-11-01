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
-- Table structure for table `advertisement`
--

DROP TABLE IF EXISTS `advertisement`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `advertisement` (
  `adsid` bigint unsigned NOT NULL AUTO_INCREMENT,
  `adstitle` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `adsdescription` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `adsimage` varchar(2048) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `adswebsite` varchar(2048) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `visible` tinyint(1) NOT NULL DEFAULT '1' COMMENT '1 = show, 0 = hide',
  PRIMARY KEY (`adsid`),
  KEY `idx_advertisement_title` (`adstitle`),
  KEY `idx_advertisement_visible` (`visible`),
  CONSTRAINT `chk_adsImage_nonempty` CHECK ((`adsImage` <> _utf8mb4'')),
  CONSTRAINT `chk_adsWebsite_nonempty` CHECK ((`adsWebsite` <> _utf8mb4'')),
  CONSTRAINT `chk_visible_boolean` CHECK ((`visible` in (0,1)))
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `advertisement`
--

LOCK TABLES `advertisement` WRITE;
/*!40000 ALTER TABLE `advertisement` DISABLE KEYS */;
INSERT INTO `advertisement` VALUES (1,'Payment Made Easy','Sign up in minutes and pay anywhere in Singapore with zero annual fees.','/static/ads/PaymentMadeEasy.png','https://www.posb.com.sg/personal/deposits/pay-with-ease/registering-for-paylah',1),(2,'Enjoy $8 Off Delivery','Trusted hawker favourites delivered fast. Limited-time voucher for new users.','/static/ads/Enjoy8OffDelivery.png','https://www.grab.com/sg/food/',1),(3,'Food Delivery 30% Off','Laksa, chicken rice, and more — save on your first three orders.','/static/ads/FoodDelivery30Off.png','https://www.foodpanda.sg/',1),(4,'Experience the Power of 5G','Stream, game, and work on-the-go with ultra-fast speeds across the MRT network.','/static/ads/ExperienceThePowerOf5G.png','https://www.singtel.com/personal/products-services/mobile/5g-plus',1),(5,'Memorable Staycation','Escape the routine with lush greenery, indoor waterfall views, and family perks.','/static/ads/EnjoyAMemorableStaycation.png','https://www.jewelchangiairport.com/en.html',1),(6,'Singapore Online Mega Sale','Up to 70% off with free next-day delivery. Shop now.','/static/ads/OnlineShopping.png','https://shopee.sg/',1),(7,'Student Ambassadors Wanted - Singapore Campus','Flexible hours • Open House guide • Social media crew • Event support. Scan to apply.','/static/ads/StudentAmbassadorsWanted.png','https://www.sim.edu.sg/',1),(8,'Donate - EchoPress','Free membership • Real-time news • Comment / Like / Follow • Community discussion • Localised & global content • Transparent & ad-supported','/static/ads/EchoPressDonate.png','/donate',1);
/*!40000 ALTER TABLE `advertisement` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-11-01 21:58:48
