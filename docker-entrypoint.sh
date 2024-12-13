#!/bin/sh

trap 'exit' INT TERM
trap 'kill 0' EXIT

echo "Waiting for Minio..."

while ! nc -z minio 9000; do
  sleep 0.1
done

echo "Minio is ready!"

exec uvicorn src.main:app --host 0.0.0.0 --port 8085 --reload
