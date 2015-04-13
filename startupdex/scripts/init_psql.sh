#!/bin/bash
createdb -U postgres startupdex
psql -U postgres -d startupdex -c "CREATE USER taylor WITH PASSWORD 'dave&busterspowercard';"
psql -U postgres -d startupdex -c "GRANT all ON startups TO taylor";
psql -U postgres -d startupdex -c "GRANT all ON angelcomirror TO taylor";
psql -U postgres -d startupdex -c "GRANT all ON users TO taylor";
psql -U postgres -d startupdex -c "GRANT all ON articles TO taylor";
