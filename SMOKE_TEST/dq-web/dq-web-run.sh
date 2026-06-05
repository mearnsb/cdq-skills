#!/usr/bin/env bash
# DQ Web — Docker run command
# Run this after PostgreSQL is already running on :5432
set -euo pipefail

IMAGE="brianmearns162/dq-web:2024.07.1-ABDGCSHILMH-4202"
ENV_FILE="$(dirname "$0")/dq-web.env"
CONTAINER_NAME="dq-web"

echo "Pulling ${IMAGE}..."
docker pull "${IMAGE}"

echo "Starting ${CONTAINER_NAME}..."
docker run -d --name "${CONTAINER_NAME}" \
  -p 9000:9005 \
  --memory="4g" \
  --add-host=host.docker.internal:host-gateway \
  --env-file "${ENV_FILE}" \
  "${IMAGE}"

echo "Container started. Check logs:"
echo "  docker logs -f ${CONTAINER_NAME}"
echo ""
echo "Wait for 'Started OwlWebApp' (~50s), then verify:"
echo "  curl -s -o /dev/null -w '%{http_code}' http://localhost:9000/"
echo "  # Expected: 302 (redirect to /login)"