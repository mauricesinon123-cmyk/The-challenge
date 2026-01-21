BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "pdescription" (
	"id"	INTEGER NOT NULL,
	"text"	VARCHAR(10000),
	"date"	DATETIME,
	"user_id"	INTEGER,
	PRIMARY KEY("id"),
	FOREIGN KEY("user_id") REFERENCES "user"("id")
);
CREATE TABLE IF NOT EXISTS "user" (
	"id"	INTEGER NOT NULL,
	"email"	VARCHAR(150),
	"password"	VARCHAR(150),
	"first_name"	VARCHAR(150),
	UNIQUE("email"),
	PRIMARY KEY("id")
);
COMMIT;
