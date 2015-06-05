#!/bin/bash
#createdb -U postgres startupdex
#psql -U postgres -d startupdex -c "CREATE USER taylor WITH PASSWORD 'dave&busterspowercard';"
#psql -U postgres -d startupdex -c "GRANT all ON startups TO taylor";
#psql -U postgres -d startupdex -c "GRANT all ON angelcomirror TO taylor";
#psql -U postgres -d startupdex -c "GRANT all ON users TO taylor";
#psql -U postgres -d startupdex -c "GRANT all ON articles TO taylor";

psql -U postgres -d startupdex -c "GRANT all ON startupdex TO taylor";

psql -U taylor -d startupdex -c "
CREATE TABLE users (
	id SERIAL NOT NULL,
	email TEXT NOT NULL,
	password TEXT,
	fullname TEXT NOT NULL,
	phone TEXT,
	confirmed BOOLEAN,
	join_date TIMESTAMP,
	tz TEXT,
	tzoffset TEXT,
	status TEXT,
	location TEXT,
	country TEXT,
	state_province TEXT,
	city TEXT,
	street_address TEXT,
	about TEXT,
	thumb_url TEXT,
	photo_url TEXT,
	local_url TEXT,
	home_url TEXT,
	blog_url TEXT,
	linkedin_url TEXT,
	facebook_url TEXT,
	twitter_url TEXT,
	PRIMARY KEY (id)
);

"

psql -U taylor -d startupdex -c "
CREATE TABLE passwords (
	id SERIAL,
	userid INTEGER UNIQUE NOT NULL,
	password TEXT NOT NULL,
	salt1 TEXT NOT NULL,
	salt2 TEXT NOT NULL,
	version INTEGER,
	PRIMARY KEY (id),
	FOREIGN KEY (userid) REFERENCES users (id) ON DELETE CASCADE
);
"

psql -U taylor -d startupdex -c "
CREATE TABLE startups (
	id SERIAL NOT NULL,
	userid_creator INTEGER,
	name TEXT NOT NULL,
	status TEXT,
	locations TEXT,
	country TEXT,
	state_province TEXT,
	city TEXT,
	street_address TEXT,
	lat FLOAT,
	lng FLOAT,
	tags TEXT ,
	contact_phone TEXT ,
	contact_email TEXT,
	local_url TEXT UNIQUE NOT NULL,
	home_url TEXT ,
	blog_url TEXT ,
	linkedin_url TEXT ,
	facebook_url TEXT ,
	twitter_url TEXT ,
	logo_url TEXT,
	thumb_url TEXT,
	header_info TEXT ,
	short_info TEXT NOT NULL,
	primary_category TEXT,
	categories TEXT,
	about TEXT NOT NULL,
	startupdex_ranking TEXT ,
	founders TEXT,
	angelco_quality INTEGER,
	angelco_follower_count INTEGER ,
	created_at TIMESTAMP NOT NULL,
	updated_at TIMESTAMP NOT NULL,
	angelco_status TEXT ,
	company_size TEXT,
	company_status INTEGER,
	language TEXT NOT NULL DEFAULT('english'),
	PRIMARY KEY (id),
	FOREIGN KEY (userid_creator) REFERENCES users (id)
);
"
psql -U taylor -d startupdex -c "
CREATE TABLE frontpage_startups (
	startupid INTEGER,
	PRIMARY KEY (startupid),
	FOREIGN KEY (startupid) REFERENCES startups (id)
);
"

psql -U taylor -d startupdex -c "
CREATE TABLE angelcomirror (
	id INTEGER,
	startupdexid INTEGER,
	hidden INTEGER,
	community_profile INTEGER,
	name TEXT,
	angellist_url TEXT,
	logo_url TEXT,
	thumb_url TEXT,
	quality INTEGER,
	product_desc TEXT,
	high_concept TEXT,
	follower_count TEXT,
	company_url TEXT,
	company_size TEXT,
	company_type TEXT,
	created_at TIMESTAMP,
	updated_at TIMESTAMP,
	twitter_url TEXT,
	facebook_url TEXT,
	linkedin_url TEXT,
	blog_url TEXT,
	crunchbase_url TEXT,
	video_url TEXT,
	markets TEXT,
	status TEXT,
	screenshots TEXT,
	launch_date TIMESTAMP,
	fundraising TEXT,
	locations TEXT,
	PRIMARY KEY (id)
);
"

psql -U taylor -d startupdex -c "
CREATE TABLE angelcomirror_has_startups (
	angelcoid INTEGER,
	startupdexid INTEGER,
	PRIMARY KEY (angelcoid, startupdexid),
	FOREIGN KEY (startupdexid) REFERENCES startups (id),
	FOREIGN KEY (angelcoid) REFERENCES angelcomirror (id)
);
"

psql -U taylor -d startupdex -c "
CREATE TABLE articles (
	id SERIAL NOT NULL,
	startupdexid INTEGER,
	authorid INTEGER NOT NULL,
	author_name TEXT,
	title TEXT,
	subtitle TEXT,
	lead_text TEXT,
	story TEXT,
	local_url TEXT UNIQUE,
	tags TEXT,
	date_published TIMESTAMP,
	date_edited TIMESTAMP,
	photo_url TEXT,
	header_image TEXT,
	other_images TEXT,
	PRIMARY KEY (id),
	FOREIGN KEY (startupdexid) REFERENCES startups (id),
	FOREIGN KEY (authorid) REFERENCES users (id)
);
"

psql -U taylor -d startupdex -c "
CREATE TABLE categories (
	id SERIAL NOT NULL,
	name TEXT UNIQUE NOT NULL,
	local_url TEXT UNIQUE NOT NULL,
	popularity INTEGER,
	num_startups INTEGER,
	PRIMARY KEY (id)
);
"

psql -U taylor -d startupdex -c "
CREATE TABLE user_has_articles (
	userid INTEGER,
	articleid INTEGER,
	PRIMARY KEY (userid, articleid),
	FOREIGN KEY (userid) REFERENCES users (id) ON DELETE CASCADE,
	FOREIGN KEY (articleid) REFERENCES articles (id) ON DELETE CASCADE
);
CREATE TABLE startup_has_articles (
	startupid INTEGER,
	articleid INTEGER,
	PRIMARY KEY (startupid, articleid),
	FOREIGN KEY (startupid) REFERENCES startups(id) ON DELETE CASCADE,
	FOREIGN KEY (articleid) REFERENCES articles(id) ON DELETE CASCADE
);
CREATE TABLE user_has_startups (
	userid INTEGER,
	startupid INTEGER,
	PRIMARY KEY (userid, startupid),
	FOREIGN KEY (userid) REFERENCES users (id) ON DELETE CASCADE,
	FOREIGN KEY (startupid) REFERENCES startups (id) ON DELETE CASCADE
);
CREATE TABLE startup_has_categories (
	startupid INTEGER,
	categoryid INTEGER,
	rank INTEGER,
	PRIMARY KEY (startupid, categoryid),
	FOREIGN KEY (startupid) REFERENCES startups (id) ON DELETE CASCADE,
	FOREIGN KEY (categoryid) REFERENCES categories (id) ON DELETE CASCADE
);
"

psql -U taylor -d startupdex -c "
CREATE TABLE fts_startups (
	id SERIAL,
	startupdexid INTEGER UNIQUE REFERENCES startups(id) ON DELETE CASCADE,
	angelcoid INTEGER UNIQUE,
	name TEXT,
	short_info TEXT,
	local_url TEXT UNIQUE,
	photo_url TEXT,
	ranking TEXT,
	doc TEXT,
	tsv TSVECTOR,
	PRIMARY KEY (id)
);
"


### FULL TEXT SEARCH ###
psql -U taylor -d startupdex -c "
CREATE TRIGGER tsvupdate BEFORE INSERT OR UPDATE ON fts_startups 
FOR EACH ROW EXECUTE PROCEDURE tsvector_update_trigger (
tsv, 'pg_catalog.english', doc);

CREATE INDEX fts_idx ON fts_startups USING GIN (tsv);
"

psql -U taylor -d startupdex -c "
SELECT id, name
FROM (SELECT startup.id as id,
startup.name as name,
setweight(to_tsvector(post.english::regconfig, startup.name), 'A') ||
setweight(to_tsvector(post.english::regconfig, startup.about), 'B') as document 


SELECT to_tsvector(post.english, 
"


SELECT to_tsvector('It''s kind of fun to do the impossible') @@ to_tsquery('impossible');
SELECT to_tsvector('tree') @@ to_tsquery(


psql -U taylor -d startupdex -c "
CREATE OR REPLACE TRIGGER add_to_category
AFTER INSERT ON startup_has_categories
FOR EACH ROW
BEGIN
	UPDATE categories
	SET num_startups = num_startups + 1
	WHERE categories.id = :NEW.categoryid
END;

CREATE OR REPLACE TRIGGER del_from_category
AFTER DELETE ON startup_has_categories
FOR EACH ROW
BEGIN
	UPDATE category
	SET num_startups = num_startups - 1
	WHERE categories.id = :NEW.
END;
"


### initialize values ###
psql -U taylor -d startupdex -c "
INSERT INTO users (id, email, fullname)
VALUES (1, 'unclaimed', 'unclaimed');
"
