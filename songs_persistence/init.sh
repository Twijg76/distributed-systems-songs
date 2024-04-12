#!/bin/bash

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE songs;

EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "songs" <<-EOSQL
    CREATE TABLE songs(
        artist TEXT NOT NULL,
        title TEXT NOT NULL,
        PRIMARY KEY (artist, title)
    );
    COPY songs (artist, title)
    FROM '/docker-entrypoint-initdb.d/mil_song.csv'
    DELIMITER ','
    CSV HEADER;
    CREATE TABLE playlists(
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        username TEXT NOT NULL
    );
    COPY playlists (name, username)
    FROM '/docker-entrypoint-initdb.d/playlists.csv'
    DELIMITER ',' CSV HEADER;
    CREATE TABLE playlist_songs(
        playlist_id INTEGER NOT NULL,
        artist TEXT NOT NULL,
        title TEXT NOT NULL,
        PRIMARY KEY (playlist_id, artist, title)
    );
    COPY playlist_songs (playlist_id, artist, title)
    FROM '/docker-entrypoint-initdb.d/playlist_songs.csv'
    DELIMITER ',' CSV HEADER;
EOSQL
