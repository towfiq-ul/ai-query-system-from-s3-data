#!/bin/bash
if aws --endpoint-url=http://localhost:4566 s3 mb s3://local-bucket 2>&1; then
  echo "Bucket 'local-bucket' created successfully."
else
  echo "Failed to create bucket 'local-bucket'." >&2
  exit 1
fi