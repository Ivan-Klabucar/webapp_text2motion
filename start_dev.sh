#!/bin/bash

export VIDEO_DIR=/Users/klabs/Downloads/app_vids

gunicorn 'app.main:app' \
    --bind ${ADDRESS:-0.0.0.0}:${PORT:-8222} \
    --workers ${WORKERS:-1} \
    --worker-class uvicorn.workers.UvicornWorker \
    --log-level info \
    --access-logfile="-"