#!/bin/bash

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE users;

EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "users" <<-EOSQL
    CREATE TABLE users(
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        PRIMARY KEY (username)
    );
    COPY users (username, password)
    FROM '/docker-entrypoint-initdb.d/mil_users.csv'
    DELIMITER ','
    CSV HEADER;
EOSQL
