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
  `image` varchar(255) DEFAULT NULL,
  `catID` int DEFAULT NULL,
  PRIMARY KEY (`articleID`),
  KEY `catID_idx` (`catID`),
  CONSTRAINT `catID` FOREIGN KEY (`catID`) REFERENCES `categories` (`categoryID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `articles`
--

LOCK TABLES `articles` WRITE;
/*!40000 ALTER TABLE `articles` DISABLE KEYS */;
INSERT INTO `articles` VALUES (1,'Woman charged over possessing almost 200 etomidate-laced vapes, buying another 50','SINGAPORE – A woman was charged over possessing 195 etomidate-laced vapes, or Kpods, and buying another 50 such pods on separate occasions in 2024. On Sept 4, Law Jia Yi, 23, was handed five charges in relation to vapes. She was also charged over possessing a knife with a 20cm-long blade, a card knife and a screwdriver without lawful purposes in August 2024 at a carpark in Yishun. For Law’s vape-related charges, she allegedly had 55 Kpods and four vapes in Yishun Avenue 5 on Aug 9, 2024. That month, she also purportedly bought 50 Kpods in Geylang. It was not stated in court documents where or whom she bought them from. Separately, Law is accused of possessing 49 vape pods in Yishun, which were later analysed and found to contain etomidate. Law also allegedly had 98 vape pods and two vapes in Sentosa, in Siloso Road. She is also said to have had 91 Kpods at the same location. Law’s case has been scheduled for a pre-trial conference on Sept 11. On Sept 3, a 17-year-old boy was charged with possessing a vape device containing a cannabis-related substance. In his National Day Rally speech in August, Prime Minister Lawrence Wong said the Government will treat vaping as a drug issue and impose stiffer penalties. Since Sept 1, first-time etomidate abusers below 18 years old will be fined $500, while adults will be fined $700. This is a $200 increase for each group. They must also attend mandatory rehabilitation for up to six months. Sellers of Kpods will face higher penalties under the Misuse of Drugs Act. Those who import Kpods will face between three and 20 years’ jail, and between five and 15 strokes of the cane. Those convicted of selling or distributing Kpods will face between two and 10 years’ jail, and receive between two and five strokes of the cane. The public can report vaping offences to the Tobacco Regulation Branch on 6684-2036 or 6684-2037 from 9am to 9pm daily, or online at go.gov.sg/reportvape Those using Kpods can seek help through a national programme called QuitVape. More information on vaping can be found at gov.sg/stopvaping, a microsite launched in August to consolidate resources, helplines and reporting avenues. The authorities have said that those who voluntarily seek support to quit vaping will not face any penalties for doing so.','Nadine Chua','2025-09-04 17:45:00','2025-09-05 00:16:00','../static/img/sel-kpod.jpeg',4),(2,'Jail for money mule who was promised $100 a day to withdraw cash for scammers','SINGAPORE – A financially strapped man withdrew scam proceeds in cash from ATMs to earn $100 a day so that he could buy diapers and milk powder for his newborn child. Yves Quah Jun Boon, 24, was sentenced to eight months’ jail on Sept 5 after he withdrew more than $150,000 from various ATMs in one day in June 2023. He pleaded guilty to money laundering and a charge under the Computer Misuse Act. Deputy Public Prosecutor Tan Jing Min said Quah often confided in his primary school friend, identified in court documents as Wei Jian, about his financial struggles – he needed money to pay for the needs of his newborn child. In June 2023, Wei Jian told Quah about an opportunity to earn $100 a day by withdrawing cash from ATMs. That month, Wei Jian and Quah met another man, named Ryan, to collect seven ATM cards registered under three different names, SIM cards and a mobile phone. Ryan told Quah that it was guaranteed to be a “safe job” and that the personal identification number, or PIN, for all the ATM cards was the same. Despite suspecting that he was asked to withdraw criminal proceeds, Quah went ahead with the job. On June 25, he withdrew $151,280 from ATMs at Woodlands Civic Centre and Ngee Ann City. When an ATM card prevented him from withdrawing money, he threw the card away. DPP Tan said Quah made at least 20 unauthorised withdrawals on that day. Quah then handed over the cash to a member of a money laundering syndicate, identified in court documents as Siyuan, at the Ngee Ann City carpark. Siyuan told Quah that $120 was missing and the amount would be deducted from Quah’s salary. This effectively meant that Quah would not be paid for what he did that day. Soon after this took place, the police arrived at the carpark, acting on a tip-off. Quah, Siyuan and Wei Jian were arrested and the $151,280 in cash was seized. The prosecutor asked for an eight-month jail term for Quah. She said: “The accused was not a traditional money mule... but he was part of the ecosystem that launders criminal proceeds, by withdrawing monies that had been deposited into money mules’ bank accounts.” Those convicted of money laundering can be jailed for up to 10 years, fined up to $500,000, or both.','Nadine Chua','2025-09-05 14:05:00','2025-09-05 15:20:00','../static/img/scam.jpg',5),(3,'32 people caught for suspected Kpod abuse after new measures kicked in on Sept 1','SINGAPORE – The first week following sweeping changes to anti-vaping laws has seen the authorities apprehend 32 people across Singapore for suspected abuse of etomidate. In total, the authorities caught 232 people for vape-related offences between Sept 1 and Sept 7, the Ministry of Health (MOH) said late on Sept 8. Those caught with vapes have been issued fines, while devices suspected of containing etomidate have been sent for testing. Ongoing laboratory tests have so far confirmed 14 people to be in possession of Kpods. Seven results have returned negative, while the results for 11 others are still pending. The ministry said that three abusers have been served notices to attend rehabilitation for up to six months. “In line with the enhanced enforcement regime, etomidate abusers are required to attend rehabilitation in lieu of prosecution,” an MOH spokesperson said, adding that the rehabilitation programme will focus on education, counselling, and support to help individuals overcome their addiction. In a Facebook post, Health Minister Ong Ye Kung, who is also Coordinating Minister for Social Policies, said that the first alleged etomidate trafficker was charged on Sept 8 under the Misuse of Drugs Act (MDA).','Andrew Wong','2025-09-08 22:07:00','2025-09-09 16:40:00','../static/img/kpods.png',6),(4,'Man arrested after fire at Chai Chee Avenue HDB block; 4 taken to hospital, 50 residents evacuated','SINGAPORE – A 58-year-old man was arrested for allegedly causing a fire to break out at an HDB block in Chai Chee Avenue on Sept 5, resulting in four people being taken to hospital and prompting the evacuation of about 50 residents. The Singapore Civil Defence Force (SCDF) said it was alerted to a fire at Block 31 Chai Chee Avenue at about 11.05pm. “The living room of an eighth-floor unit was on fire,” SCDF added. It said that it extinguished the fire with a water jet, and that there was no one inside the flat. In response to media queries on Sept 7, the police said the 58-year-old man was arrested for “causing or contributing to risk of dangerous fire”. They added that four men, aged between 20 and 78, were taken to hospital. They were all conscious. Three people from neighbouring flats were assessed for smoke inhalation. Two of them were taken to Changi General Hospital, and the third to Singapore General Hospital (SGH). A firefighter was also assessed for smoke inhalation and taken to SGH.','Grabrielle Andres and Vihanya Rakshika','2025-09-06 13:25:00','2025-09-07 22:44:00','../static/img/fire.jpeg',7);
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

-- Dump completed on 2025-09-25 20:48:14
