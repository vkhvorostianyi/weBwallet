#!/usr/bin/env bash
sudo su postgres
psql
create database $1;
create user $2 with password $3;
ALTER ROLE $2 SET client_encoding TO 'utf8';
ALTER ROLE $2 SET default_transaction_isolation TO 'read committed';
ALTER ROLE $2 SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE $1 TO $2;
