#!/bin/bash

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE social;

EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "social" <<-EOSQL
    CREATE TABLE friends(
        username TEXT NOT NULL,
        friend TEXT NOT NULL,
        PRIMARY KEY (username, friend)
    );
    CREATE TABLE feed(
        username TEXT NOT NULL,
        post TEXT NOT NULL,
        time TIMESTAMP NOT NULL,
        PRIMARY KEY (username, post, time)
    );
    COPY friends (username, friend) FROM '/docker-entrypoint-initdb.d/friends.csv' DELIMITER ',' CSV HEADER;
    COPY feed (username, post, time) FROM '/docker-entrypoint-initdb.d/feed.csv' DELIMITER ',' CSV HEADER;
    CREATE TABLE shared_playlists(
        playlist_id INTEGER NOT NULL,
        friendname TEXT NOT NULL,
        PRIMARY KEY (playlist_id, friendname));
    COPY shared_playlists (playlist_id, friendname) FROM '/docker-entrypoint-initdb.d/shared_playlists.csv' DELIMITER ',' CSV HEADER;
EOSQL

