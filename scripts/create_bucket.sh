#!/usr/bin/env bash
# Membuat bucket S3 untuk menyimpan data kamera.
# Nama bucket harus unik secara global: ganti <inisial-nim> dengan milikmu.
set -euo pipefail
BUCKET="digicam-loan-<inisial-nim>"
aws s3api create-bucket --bucket "$BUCKET" --region us-east-1
echo "Bucket $BUCKET siap."
