#!/bin/bash
# Script to upload existing test results to S3
# Usage: ./upload_to_s3.sh
#
# Optional environment variables:
#   S3_CATOMATIC_TIMESTAMP - Timestamp in milliseconds (default: auto-generate)

cd "$(dirname "$0")/.."

echo "Uploading test results to S3..."
echo ""

# Build command with optional timestamp
S3_CMD="python3 tests/upload_results_to_s3.py \
    --results-dir tests/results/ \
    --s3-region eu-central-1 \
    --s3-bucket external-test-results \
    --s3-test-framework-repo-name cato-cli_tf_ci_read_only_tests \
    --s3-catomatic-cycle cctest \
    --s3-catomatic-run-id 123 \
    --s3-catomatic-suite-name mysuite"

# Add timestamp if provided
if [ -n "$S3_CATOMATIC_TIMESTAMP" ]; then
    S3_CMD="${S3_CMD} --s3-catomatic-timestamp ${S3_CATOMATIC_TIMESTAMP}"
fi

S3_CMD="${S3_CMD} --verbose"

eval $S3_CMD

echo ""
echo "Upload completed!"

