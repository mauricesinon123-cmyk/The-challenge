BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "audit_log" (
	"id"	INTEGER NOT NULL,
	"user_id"	INTEGER NOT NULL,
	"action"	VARCHAR(50) NOT NULL,
	"resource_type"	VARCHAR(50) NOT NULL,
	"resource_id"	INTEGER,
	"details"	VARCHAR(500),
	"timestamp"	DATETIME,
	"ip_address"	VARCHAR(50),
	PRIMARY KEY("id"),
	FOREIGN KEY("user_id") REFERENCES "user"("id")
);
CREATE TABLE IF NOT EXISTS "login_attempt" (
	"id"	INTEGER NOT NULL,
	"email"	VARCHAR(150) NOT NULL,
	"success"	BOOLEAN,
	"ip_address"	VARCHAR(50),
	"timestamp"	DATETIME,
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "pdescription" (
	"id"	INTEGER NOT NULL,
	"title"	VARCHAR(200) NOT NULL,
	"text"	VARCHAR(10000) NOT NULL,
	"group"	INTEGER NOT NULL,
	"date"	DATETIME,
	"user_id"	INTEGER NOT NULL,
	PRIMARY KEY("id"),
	FOREIGN KEY("user_id") REFERENCES "user"("id")
);
CREATE TABLE IF NOT EXISTS "user" (
	"id"	INTEGER NOT NULL,
	"email"	VARCHAR(150),
	"password"	VARCHAR(150),
	"first_name"	VARCHAR(150),
	"date_of_birth"	DATE,
	"region"	VARCHAR(100),
	"profile_picture_path"	VARCHAR(300),
	"account_setup_complete"	BOOLEAN,
	"is_locked"	BOOLEAN,
	"locked_until"	DATETIME,
	"last_login"	DATETIME,
	"created_at"	DATETIME,
	UNIQUE("email"),
	PRIMARY KEY("id")
);
INSERT INTO "audit_log" VALUES (1,1,'SIGNUP','USER',1,NULL,'2026-01-14 10:07:20','127.0.0.1');
INSERT INTO "audit_log" VALUES (2,1,'LOGIN','USER',1,NULL,'2026-01-14 12:51:48','145.52.203.174');
INSERT INTO "audit_log" VALUES (3,2,'SIGNUP','USER',2,NULL,'2026-01-14 12:54:22','145.52.202.199');
INSERT INTO "audit_log" VALUES (4,1,'CREATE','PROJECT',1,'Project aangemaakt: Afvalscheidingsysteem','2026-01-14 12:59:12','145.52.203.174');
INSERT INTO "audit_log" VALUES (5,2,'CREATE','PROJECT',2,'Project aangemaakt: Arme mensen voeden','2026-01-14 13:01:37','145.52.202.199');
INSERT INTO "audit_log" VALUES (6,2,'LOGIN','USER',2,NULL,'2026-01-14 13:06:21','145.52.202.199');
INSERT INTO "audit_log" VALUES (7,2,'LOGOUT','USER',2,NULL,'2026-01-14 13:06:41','145.52.202.199');
INSERT INTO "audit_log" VALUES (8,1,'LOGIN','USER',1,NULL,'2026-01-14 13:09:53','145.52.203.174');
INSERT INTO "audit_log" VALUES (9,2,'LOGIN','USER',2,NULL,'2026-01-14 13:28:02','145.52.202.199');
INSERT INTO "audit_log" VALUES (10,2,'CREATE','PROJECT',3,'Project aangemaakt: Vijver schoonmaken','2026-01-14 13:29:01','145.52.202.199');
INSERT INTO "audit_log" VALUES (11,2,'UPDATE','PROJECT',3,'Project gewijzigd: Vijver schoonmaken -> Vijver schoonmaken','2026-01-14 13:29:46','145.52.202.199');
INSERT INTO "audit_log" VALUES (12,2,'CREATE','PROJECT',4,'Project aangemaakt: Straat bibliotheek','2026-01-14 13:31:57','145.52.202.199');
INSERT INTO "audit_log" VALUES (13,2,'CREATE','PROJECT',5,'Project aangemaakt: wijkmoesuin','2026-01-14 13:38:21','145.52.202.199');
INSERT INTO "audit_log" VALUES (14,2,'UPDATE','PROJECT',5,'Project gewijzigd: wijkmoesuin -> wijkmoesuin','2026-01-14 13:38:42','145.52.202.199');
INSERT INTO "audit_log" VALUES (15,2,'UPDATE','PROJECT',5,'Project gewijzigd: wijkmoesuin -> wijkmoesuin','2026-01-14 13:38:56','145.52.202.199');
INSERT INTO "audit_log" VALUES (16,1,'CREATE','PROJECT',6,'Project aangemaakt: wijk moestuin','2026-01-14 13:40:56','145.52.203.174');
INSERT INTO "audit_log" VALUES (17,3,'SIGNUP','USER',3,NULL,'2026-01-14 13:41:22','145.52.203.209');
INSERT INTO "audit_log" VALUES (18,2,'DELETE','PROJECT',5,'Project verwijderd: wijkmoesuin','2026-01-14 13:41:50','145.52.202.199');
INSERT INTO "audit_log" VALUES (19,3,'LOGIN','USER',3,NULL,'2026-01-14 13:43:01','145.52.203.226');
INSERT INTO "audit_log" VALUES (20,2,'UPDATE','PROJECT',4,'Project gewijzigd: Straat bibliotheek -> Straat bibliotheek','2026-01-14 13:44:11','145.52.202.199');
INSERT INTO "audit_log" VALUES (21,3,'CREATE','PROJECT',7,'Project aangemaakt: Medische telefoonnummers','2026-01-14 13:44:56','145.52.203.226');
INSERT INTO "audit_log" VALUES (22,1,'UPDATE','PROJECT',6,'Project gewijzigd: wijk moestuin -> wijk moestuin','2026-01-14 13:46:15','145.52.203.174');
INSERT INTO "audit_log" VALUES (23,3,'CREATE','PROJECT',8,'Project aangemaakt: Kleine windmolens','2026-01-14 13:48:52','145.52.203.226');
INSERT INTO "audit_log" VALUES (24,3,'LOGOUT','USER',3,NULL,'2026-01-14 13:50:35','145.52.203.226');
INSERT INTO "audit_log" VALUES (25,1,'LOGIN','USER',1,NULL,'2026-01-14 14:46:13','127.0.0.1');
INSERT INTO "audit_log" VALUES (26,1,'LOGOUT','USER',1,NULL,'2026-01-14 14:47:10','127.0.0.1');
INSERT INTO "audit_log" VALUES (27,1,'LOGIN','USER',1,NULL,'2026-01-14 14:47:27','127.0.0.1');
INSERT INTO "audit_log" VALUES (28,1,'CREATE','PROJECT',9,'Project aangemaakt: straat schoonmaken','2026-01-14 14:48:27','127.0.0.1');
INSERT INTO "audit_log" VALUES (29,1,'LOGOUT','USER',1,NULL,'2026-01-14 14:49:13','127.0.0.1');
INSERT INTO "audit_log" VALUES (30,1,'LOGIN','USER',1,NULL,'2026-01-14 17:34:04','192.168.2.18');
INSERT INTO "audit_log" VALUES (31,1,'CREATE','PROJECT',10,'Project aangemaakt: Vijver schoonmaken','2026-01-14 17:34:42','192.168.2.18');
INSERT INTO "audit_log" VALUES (32,1,'DELETE','PROJECT',10,'Project verwijderd: Vijver schoonmaken','2026-01-14 17:36:00','192.168.2.18');
INSERT INTO "audit_log" VALUES (33,1,'LOGOUT','USER',1,NULL,'2026-01-14 17:36:31','192.168.2.18');
INSERT INTO "audit_log" VALUES (34,1,'LOGIN','USER',1,NULL,'2026-01-14 17:36:38','192.168.2.18');
INSERT INTO "audit_log" VALUES (35,1,'LOGOUT','USER',1,NULL,'2026-01-14 17:36:57','192.168.2.18');
INSERT INTO "audit_log" VALUES (36,4,'SIGNUP','USER',4,NULL,'2026-01-14 17:37:54','192.168.2.18');
INSERT INTO "audit_log" VALUES (37,4,'CREATE','PROJECT',10,'Project aangemaakt: Vijver schoonmaken','2026-01-14 17:38:46','192.168.2.18');
INSERT INTO "audit_log" VALUES (38,4,'LOGOUT','USER',4,NULL,'2026-01-14 17:39:46','192.168.2.18');
INSERT INTO "audit_log" VALUES (39,5,'SIGNUP','USER',5,NULL,'2026-01-14 18:26:02','192.168.2.18');
INSERT INTO "audit_log" VALUES (40,5,'CREATE','PROJECT',11,'Project aangemaakt: Straat schoonmaken','2026-01-14 18:27:01','192.168.2.18');
INSERT INTO "audit_log" VALUES (41,5,'LOGOUT','USER',5,NULL,'2026-01-14 18:28:16','192.168.2.18');
INSERT INTO "audit_log" VALUES (42,5,'LOGIN','USER',5,NULL,'2026-01-16 15:01:59','192.168.2.18');
INSERT INTO "audit_log" VALUES (43,5,'CREATE','PROJECT',12,'Project aangemaakt: Chess club','2026-01-16 15:03:04','192.168.2.18');
INSERT INTO "audit_log" VALUES (44,5,'LOGIN','USER',5,NULL,'2026-01-16 15:11:03','192.168.2.18');
INSERT INTO "audit_log" VALUES (45,5,'LOGOUT','USER',5,NULL,'2026-01-16 15:11:52','192.168.2.18');
INSERT INTO "audit_log" VALUES (46,5,'LOGIN','USER',5,NULL,'2026-01-16 15:50:11','192.168.2.18');
INSERT INTO "audit_log" VALUES (47,5,'LOGIN','USER',5,NULL,'2026-01-20 12:00:10','192.168.2.18');
INSERT INTO "audit_log" VALUES (48,5,'LOGIN','USER',5,NULL,'2026-01-20 12:02:41','192.168.2.18');
INSERT INTO "audit_log" VALUES (49,5,'LOGIN','USER',5,NULL,'2026-01-20 12:08:03','192.168.2.18');
INSERT INTO "audit_log" VALUES (50,5,'LOGIN','USER',5,NULL,'2026-01-20 12:08:50','192.168.2.18');
INSERT INTO "audit_log" VALUES (51,5,'UPDATE','PROJECT',11,'Project gewijzigd: Straat schoonmaken -> Straat schoonmaken','2026-01-20 12:09:10','192.168.2.18');
INSERT INTO "audit_log" VALUES (52,5,'UPDATE','PROJECT',11,'Project gewijzigd: Straat schoonmaken -> Straat schoonmaken','2026-01-20 12:11:26','192.168.2.18');
INSERT INTO "audit_log" VALUES (53,5,'UPDATE','PROJECT',12,'Project gewijzigd: Chess club -> Chess club','2026-01-20 12:11:50','192.168.2.18');
INSERT INTO "audit_log" VALUES (54,5,'LOGOUT','USER',5,NULL,'2026-01-20 12:13:18','192.168.2.18');
INSERT INTO "audit_log" VALUES (55,6,'SIGNUP','USER',6,NULL,'2026-01-21 08:36:16','145.52.202.120');
INSERT INTO "audit_log" VALUES (56,6,'LOGOUT','USER',6,NULL,'2026-01-21 08:36:22','145.52.202.120');
INSERT INTO "audit_log" VALUES (57,5,'LOGIN','USER',5,NULL,'2026-01-21 08:48:13','145.52.202.120');
INSERT INTO "audit_log" VALUES (58,5,'LOGIN','USER',5,NULL,'2026-01-21 09:08:13','145.52.202.120');
INSERT INTO "audit_log" VALUES (59,5,'LOGOUT','USER',5,NULL,'2026-01-21 09:15:07','145.52.202.120');
INSERT INTO "audit_log" VALUES (60,5,'LOGIN','USER',5,NULL,'2026-01-21 10:50:33','145.52.202.120');
INSERT INTO "audit_log" VALUES (61,5,'LOGOUT','USER',5,NULL,'2026-01-21 10:51:34','145.52.202.120');
INSERT INTO "login_attempt" VALUES (1,'email@gmail.com',0,'127.0.0.1','2026-01-14 10:06:56');
INSERT INTO "login_attempt" VALUES (2,'email@gmail.com',0,'145.52.203.174','2026-01-14 12:51:34');
INSERT INTO "login_attempt" VALUES (3,'mauricesinon@gmail.com',1,'145.52.203.174','2026-01-14 12:51:48');
INSERT INTO "login_attempt" VALUES (4,'25037102@student.hhs.nl',1,'145.52.202.199','2026-01-14 13:06:21');
INSERT INTO "login_attempt" VALUES (5,'mauricesinon@gmail.com',1,'145.52.203.174','2026-01-14 13:09:53');
INSERT INTO "login_attempt" VALUES (6,'25037102@student.hhs.nl',1,'145.52.202.199','2026-01-14 13:28:02');
INSERT INTO "login_attempt" VALUES (7,'lukegierde@icloud.com',1,'145.52.203.226','2026-01-14 13:43:01');
INSERT INTO "login_attempt" VALUES (8,'mauricesinon@gmail.com',1,'127.0.0.1','2026-01-14 14:46:13');
INSERT INTO "login_attempt" VALUES (9,'mauricesinon@gmail.com',1,'127.0.0.1','2026-01-14 14:47:27');
INSERT INTO "login_attempt" VALUES (10,'mauricesinon@gmail.com',0,'192.168.2.18','2026-01-14 17:33:49');
INSERT INTO "login_attempt" VALUES (11,'mauricesinon@gmail.com',1,'192.168.2.18','2026-01-14 17:34:04');
INSERT INTO "login_attempt" VALUES (12,'mauricesinon@gmail.com',1,'192.168.2.18','2026-01-14 17:36:38');
INSERT INTO "login_attempt" VALUES (13,'maurice.sinon123@gmail.com',1,'192.168.2.18','2026-01-16 15:01:59');
INSERT INTO "login_attempt" VALUES (14,'maurice.sinon123@gmail.com',1,'192.168.2.18','2026-01-16 15:11:03');
INSERT INTO "login_attempt" VALUES (15,'maurice.sinon123@gmail.com',1,'192.168.2.18','2026-01-16 15:50:11');
INSERT INTO "login_attempt" VALUES (16,'maurice.sinon123@gmail.com',1,'192.168.2.18','2026-01-20 12:00:10');
INSERT INTO "login_attempt" VALUES (17,'maurice.sinon123@gmail.com',1,'192.168.2.18','2026-01-20 12:02:41');
INSERT INTO "login_attempt" VALUES (18,'maurice.sinon123@gmail.com',0,'192.168.2.18','2026-01-20 12:07:56');
INSERT INTO "login_attempt" VALUES (19,'maurice.sinon123@gmail.com',1,'192.168.2.18','2026-01-20 12:08:03');
INSERT INTO "login_attempt" VALUES (20,'maurice.sinon123@gmail.com',1,'192.168.2.18','2026-01-20 12:08:50');
INSERT INTO "login_attempt" VALUES (21,'maurice.sinon123@gmail.com',0,'192.168.2.18','2026-01-20 13:04:44');
INSERT INTO "login_attempt" VALUES (22,'maurice.sinon123@gmail.com',0,'192.168.2.18','2026-01-20 13:04:46');
INSERT INTO "login_attempt" VALUES (23,'maurice.sinon123@gmail.com',0,'192.168.2.18','2026-01-20 13:04:49');
INSERT INTO "login_attempt" VALUES (24,'maurice.sinon123@gmail.com',0,'192.168.2.18','2026-01-20 13:04:51');
INSERT INTO "login_attempt" VALUES (25,'maurice.sinon123@gmail.com',0,'192.168.2.18','2026-01-20 13:04:53');
INSERT INTO "login_attempt" VALUES (26,'maurice.sinon123@gmail.com',0,'192.168.2.18','2026-01-20 13:05:01');
INSERT INTO "login_attempt" VALUES (27,'maurice.sinon123@gmail.com',0,'192.168.2.18','2026-01-20 13:05:07');
INSERT INTO "login_attempt" VALUES (28,'maurice.sinon123@gmail.com',1,'145.52.202.120','2026-01-21 08:48:13');
INSERT INTO "login_attempt" VALUES (29,'maurice.sinon123@gmail.com',1,'145.52.202.120','2026-01-21 09:08:13');
INSERT INTO "login_attempt" VALUES (30,'maurice.sinon123@gmail.com',1,'145.52.202.120','2026-01-21 10:50:33');
INSERT INTO "pdescription" VALUES (1,'Afvalscheidingsysteem','Hoi, ik ben van plan een afvalscheidingssysteem te maken. Zijn er mensen die hierbij willen of kunnen helpen?',12,'2026-01-14 12:59:12',1);
INSERT INTO "pdescription" VALUES (2,'Arme mensen voeden','Heyy mensen, ik zou graag met een groep leuke buurtgenoten de armen in de buurt een kom kippen soep geven van wegen deze koude dagen.',2,'2026-01-14 13:01:37',2);
INSERT INTO "pdescription" VALUES (3,'Vijver schoonmaken','Hallo mede zoetermeerders, ik wil graag mijn vijver schoonmaken en ik zou een paar mensen die daar bij kunnen helpen',6,'2026-01-14 13:29:46',2);
INSERT INTO "pdescription" VALUES (4,'Straat bibliotheek','Hey, ik zoek een paar mensen die een paar oude boeken hebben om een straat bibliotheek te beginnen overal in het stadshart, ik heb alleen maar boeken nodig',4,'2026-01-14 13:44:11',2);
INSERT INTO "pdescription" VALUES (6,'wijk moestuin','Hoi hoi, mij leek het een leuk idee om een wijkmoestuin te maken, mensen geïnteresseerd?',11,'2026-01-14 13:46:15',1);
INSERT INTO "pdescription" VALUES (7,'Medische telefoonnummers','Ik wil een lijst maken van telefoonnummers in de buurt van mensen met een EHBO diploma in geval van verwonding een dichtbij',3,'2026-01-14 13:44:56',3);
INSERT INTO "pdescription" VALUES (8,'Kleine windmolens','Ik heb het idee om kleine windmolens te helpen plaatsen bij mensen zodat we duurzamer kunnen leven.',7,'2026-01-14 13:48:52',3);
INSERT INTO "pdescription" VALUES (9,'straat schoonmaken','Hoi, ik wil een groepje samenstellen om de straten van de wijk schoon te maken. Wie doet er mee?',8,'2026-01-14 14:48:27',1);
INSERT INTO "pdescription" VALUES (10,'Vijver schoonmaken','Hoi hoi, ik wil graag de vijver schoonmaken, zijn er mensen die mij hierbij willen helpen?',6,'2026-01-14 17:38:46',4);
INSERT INTO "pdescription" VALUES (11,'Straat schoonmaken','Hoii, ik ben van plan om ergens aankomende week de straat aan te pakken, vuil opruimen, onkruid weg, weer helemaal netjes maken. Wie wil er mee helpen?',8,'2026-01-20 12:11:26',5);
INSERT INTO "pdescription" VALUES (12,'Chess club','Hoi hoi, om betere banden te creeëren, wilde ik een club op starten om te schaken. Zijn mensen hier ook in geïnteresseerd? Ik dacht dat we dan eens in de week konden samenkomen om te schaken!',17,'2026-01-20 12:11:50',5);
INSERT INTO "user" VALUES (1,'mauricesinon@gmail.com','pbkdf2:sha256:600000$hcqR8Z5YBjmUn9YM$62b86616ed880aa7a0ba108fe2465fee8996d2898548e6a7c800bc7c065d79ef','Maurice','2003-02-14','Seghwaert',NULL,1,0,NULL,'2026-01-14 17:36:38.270751','2026-01-14 10:07:20');
INSERT INTO "user" VALUES (2,'25037102@student.hhs.nl','pbkdf2:sha256:600000$ARUZ8rJRPHRjGW21$56e2bc17b77ccaeb86ce708706f54f0e74205e76a9e431d7416d1cd3d22512f5','Martijn','2007-10-07','Dorp',NULL,1,0,NULL,'2026-01-14 13:28:02.752002','2026-01-14 12:54:22');
INSERT INTO "user" VALUES (3,'lukegierde@icloud.com','pbkdf2:sha256:600000$Or1yGkwlVuPtSsb4$5e4052c60e50042268c784aaaca3e96732e395ba432d8f81252d073b35ba0ece','Luke','2003-05-04','Stadscentrum',NULL,1,0,NULL,'2026-01-14 13:43:01.139790','2026-01-14 13:41:22');
INSERT INTO "user" VALUES (4,'maurice.sinon@gmail.com','pbkdf2:sha256:600000$kWGOZaPqpPIddXJR$e99b2305f2767fd03f97242735f84750d81a4dfebc44cf29a5e067d86ddaadd9','Maurice','2001-06-10','Driemanspolder',NULL,1,0,NULL,NULL,'2026-01-14 17:37:54');
INSERT INTO "user" VALUES (5,'maurice.sinon123@gmail.com','pbkdf2:sha256:600000$r5iIbORHkUW7ikSr$0cbe88c420c9ae010513e4ca10a16a0fe2599a1f19fcf9b2253e4920b5246e00','Maurice','2001-06-10','Rokkeveen','profile_pictures/user_5_1768911055.png',1,0,NULL,'2026-01-21 10:50:33.003196','2026-01-14 18:26:02');
INSERT INTO "user" VALUES (6,'notanemail@i','pbkdf2:sha256:600000$KX8Hki4JQxpOLYkL$4d9f2b0a7201f621f5237ba6733fd125e22842f31653cecda3a8266c0b742801','Tim',NULL,NULL,NULL,0,0,NULL,NULL,'2026-01-21 08:36:16');
COMMIT;
