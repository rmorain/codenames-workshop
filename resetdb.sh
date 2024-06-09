#!/bin/bash
cp cn.db cn.db.bak
rm cn.db
sqlite3 cn.db < tables.sql
