#!/bin/bash

# start postgreSQL in the background
docker-entrypoint.sh postgres &

until psql -h localhost -U postgres -c '\l'; do
  echo 'Waiting for PostgreSQL to start...'
  sleep 1
done

python3 src/manage.py migrate
python3 src/manage.py runserver 0.0.0.0:8000
