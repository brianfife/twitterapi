CREATE DATABASE IF NOT EXISTS `twitter`;
USE `twitter`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `friends` (
  `userId` int(11) NOT NULL,
  `followingId` int(11) NOT NULL,
  PRIMARY KEY (`userId`,`followingId`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;
INSERT INTO `friends` VALUES (1,2),(1,4),(1,5),(2,1),(3,1),(4,1);
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tweets` (
  `messageId` int(11) NOT NULL AUTO_INCREMENT,
  `userId` int(11) NOT NULL,
  `message` varchar(140) NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`messageId`)
) ENGINE=MyISAM AUTO_INCREMENT=10 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;
INSERT INTO `tweets` VALUES (1,1,'testing brian','2013-08-15 18:28:19'),(2,2,'testing angelique','2013-08-14 02:48:01'),(3,3,'testing andrea','2013-08-14 02:48:01'),(4,4,'testing TJ','2013-08-15 15:21:46'),(5,5,'testing tqbf','2013-08-15 15:21:57'),(6,5,'Brian Fife finishes #58 (new finisher! new finisher!) in Python. http://tinyurl.com/mtsocrypt','2013-08-15 15:22:41'),(7,4,'Hello world','2013-08-15 18:27:14'),(8,1,'RT: Brian Fife finishes #58 (new finisher! new finisher!) in Python. http://tinyurl.com/mtsocrypt','2013-08-15 18:27:52'),(9,6,'testing test user','2013-08-16 18:01:36');
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(40) NOT NULL,
  `password` char(40) NOT NULL,
  `token` char(16) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=7 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;
INSERT INTO `users` VALUES (1,'brian','5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8','1b43ef1e0618de6d'),(2,'angelique','5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8','3ef0a1e7f2275a9f'),(3,'andrea','5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8','68d6dc76314c72e9'),(4,'TJ','5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8','099c34d85e4fb1e6'),(5,'tbqf','5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8','5ca7e4730994f56c'),(6,'test','5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8','1234567890abcdef');
