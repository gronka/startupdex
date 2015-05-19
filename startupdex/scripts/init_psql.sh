#!/bin/bash
#createdb -U postgres startupdex
#psql -U postgres -d startupdex -c "CREATE USER taylor WITH PASSWORD 'dave&busterspowercard';"
#psql -U postgres -d startupdex -c "GRANT all ON startups TO taylor";
#psql -U postgres -d startupdex -c "GRANT all ON angelcomirror TO taylor";
#psql -U postgres -d startupdex -c "GRANT all ON users TO taylor";
#psql -U postgres -d startupdex -c "GRANT all ON articles TO taylor";

psql -U postgres -d startupdex -c "GRANT all ON startupdex TO taylor";

psql -U taylor -d startupdex -c "
CREATE TABLE user_has_articles (
	userid integer REFERENCES users(id) ON DELETE CASCADE,
	articleid integer REFERENCES articles(id) ON DELETE CASCADE,
	PRIMARY KEY (userid, articleid)
);
CREATE TABLE startup_has_articles (
	startupid integer REFERENCES startups(id) ON DELETE CASCADE,
	articleid integer REFERENCES articles(id) ON DELETE CASCADE,
	PRIMARY KEY (startupid, articleid)
);
CREATE TABLE user_has_startups (
	userid integer REFERENCES users(id) ON DELETE CASCADE,
	startupid integer REFERENCES startups(id) ON DELETE CASCADE,
	PRIMARY KEY (userid, startupid)
);

CREATE TABLE startups (
	id SERIAL NOT NULL,
	userid_creator INTEGER NOT NULL,
	name TEXT NOT NULL,
	status TEXT,
	country TEXT NOT NULL,
	state_province TEXT NOT NULL,
	city TEXT NOT NULL,
	street_address TEXT,
	tags TEXT ,
	contact_phone TEXT ,
	contact_email TEXT NOT NULL,
	local_url TEXT UNIQUE NOT NULL,
	home_url TEXT ,
	blog_url TEXT ,
	linkedin_url TEXT ,
	facebook_url TEXT ,
	twitter_url TEXT ,
	logo_url TEXT NOT NULL,
	thumb_url TEXT NOT NULL,
	header_info TEXT ,
	short_info TEXT NOT NULL,
	primary_category TEXT NOT NULL,
	categories TEXT NOT NULL,
	about TEXT NOT NULL,
	startupdex_ranking TEXT ,
	angelco_quality INTEGER,
	angelco_follower_count INTEGER ,
	created_at TIMESTAMP NOT NULL,
	updated_at TIMESTAMP NOT NULL,
	angelco_status TEXT ,
	company_size TEXT NOT NULL,
	company_status INTEGER ,
	PRIMARY KEY (id)
);

CREATE TABLE angelcomirror (
	startupdexid INTEGER NOT NULL,
	id INTEGER,
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
	created_at TEXT,
	updated_at TEXT,
	twitter_url TEXT,
	facebook_url TEXT,
	linkedin_url TEXT,
	blog_url TEXT,
	crunchbase_url TEXT,
	video_url TEXT,
	markets TEXT,
	status TEXT,
	screenshots TEXT,
	launch_date TEXT,
	fundraising TEXT,
	locations TEXT,
	PRIMARY KEY (startupdexid)
);

CREATE TABLE passwords (
	id SERIAL,
	user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
	password TEXT NOT NULL,
	salt1 TEXT NOT NULL,
	salt2 TEXT NOT NULL,
	version INTEGER,
	PRIMARY KEY (id)
);

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
	state_province TEXT
	city TEXT,
	street_address TEXT,
	thumb_url TEXT,
	photo_url TEXT,
	local_url TEXT,
	home_url TEXT,
	blog_url TEXT,
	facebook_url TEXT,
	twitter_url TEXT,
);

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
);

CREATE TABLE fts_startups (
	id SERIAL,
	startupdex_id INTEGER UNIQUE REFERENCES startups(id) ON DELETE CASCADE,
	angelco_id INTEGER UNIQUE,
	name TEXT,
	short_info TEXT,
	local_url TEXT UNIQUE,
	photo_url TEXT,
	ranking TEXT,
	doc TEXT,
	tsv TSVECTOR
);

CREATE TRIGGER tsvupdate BEFORE INSERT OR UPDATE ON fts_startups 
FOR EACH ROW EXECUTE PROCEDURE startups_tsvector_update_trigger (
tsv, 'pg_catalog.english', doc);

CREATE INDEX fts_idx ON fts_startups USING GIN (tsv);

";

