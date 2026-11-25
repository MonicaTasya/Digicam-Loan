#!/usr/bin/env bash
# Membuat tabel DynamoDB "Cameras" (partition key: cameraId).
set -euo pipefail
aws dynamodb create-table \
  --table-name Cameras \
  --attribute-definitions AttributeName=cameraId,AttributeType=S \
  --key-schema AttributeName=cameraId,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1
aws dynamodb wait table-exists --table-name Cameras --region us-east-1
echo "Tabel Cameras siap."
