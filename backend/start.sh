#!/bin/sh
pytest -v /backend/app/tests
exec gunicorn --bind 0.0.0.0:8080 main:application