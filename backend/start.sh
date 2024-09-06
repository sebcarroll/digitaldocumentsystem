#!/bin/sh
pytest -v /backend/app/tests

# Start Gunicorn
exec gunicorn --bind :$PORT main:application