#!/usr/bin/env bash
# Build build/lambda.zip: handler code + runtime deps. boto3 is already in the Lambda runtime.
set -euo pipefail
cd "$(dirname "$0")/.."
rm -rf build && mkdir -p build/pkg
uv pip install --quiet --target build/pkg --python-platform x86_64-manylinux2014 \
  --python-version 3.12 requests
cp -r src/game_tracker build/pkg/
find build/pkg -name __pycache__ -type d -prune -exec rm -rf {} +
(cd build/pkg && python3 -m zipfile -c ../lambda.zip .)
echo "built build/lambda.zip ($(du -h build/lambda.zip | cut -f1))"
