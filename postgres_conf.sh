#!/usr/bin/env bash
sudo su postgres
psql
create database testdb;
create user test_user with password 'test_psw';
ALTER ROLE test_user SET client_encoding TO 'utf8';
ALTER ROLE test_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE test_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE testdb TO test_user;
