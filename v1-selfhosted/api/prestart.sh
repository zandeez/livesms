#!/usr/bin/env bash
OLD=$(pwd)
cd /app/migrations
sleep 10
alembic upgrade head
cd $OLD