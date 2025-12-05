# S3 Upload Feature

## Overview

The test runner can automatically upload test result JSON files to AWS S3 after exporting them locally.

## S3 Path Format

Files are uploaded to S3 with the following path structure:

```
{testFrameworkRepoName}/{catomaticCycle}/{catomaticRunId}/{catomaticSuiteName}/{testName}_{catomaticTimeStamp}.json
```

Where:
- `testFrameworkRepoName`: Test framework repository name (e.g., `cato-cli_tf_ci_read_only_tests`)
- `catomaticCycle`: Catomatic cycle name (e.g., `cctest`)
- `catomaticRunId`: Catomatic run ID (e.g., `123`)
- `catomaticSuiteName`: Test suite name (`generated` or `custom`)
- `testName`: Sanitized test name
- `catomaticTimeStamp`: Current timestamp in milliseconds (generated automatically)

## Usage

### Basic S3 Upload

```bash
python3 run_all_tests.py \
    --json-output results/ \
    --s3-upload \
    --s3-region eu-central-1 \
    --s3-bucket external-test-results \
    --s3-test-framework-repo-name cato-cli_tf_ci_read_only_tests \
    --s3-catomatic-cycle cctest \
    --s3-catomatic-run-id 123
```

### With All Options

```bash
python3 run_all_tests.py \
    --skip-validation \
    --json-output results/ \
    --s3-upload \
    --s3-region eu-central-1 \
    --s3-bucket external-test-results \
    --s3-test-framework-repo-name cato-cli_tf_ci_read_only_tests \
    --s3-catomatic-cycle cctest \
    --s3-catomatic-run-id 123 \
    --verbose
```

### Command-Line Arguments

- `--s3-upload`: Enable S3 upload (required for upload)
- `--s3-region`: AWS S3 region (default: `eu-central-1`)
- `--s3-bucket`: AWS S3 bucket name (default: `external-test-results`)
- `--s3-test-framework-repo-name`: Test framework repository name (**required**)
- `--s3-catomatic-cycle`: Catomatic cycle name (**required**)
- `--s3-catomatic-run-id`: Catomatic run ID (**required**)

## AWS Credentials

The S3 upload requires AWS credentials to be configured. You can configure them using:

1. **AWS CLI**: `aws configure`
2. **Environment variables**: 
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_DEFAULT_REGION` (optional)
3. **IAM Role**: If running on EC2/ECS with IAM role
4. **Credentials file**: `~/.aws/credentials`

## Example Output

```
✓ Exported 5 test result(s) to individual JSON files in results

✓ Uploaded 5 file(s) to S3 bucket 'external-test-results'
```

## Example S3 Paths

With the simulated data:
- `cato-cli_tf_ci_read_only_tests/cctest/123/generated/query.accountMetrics_-_Generated_Test_1764927919074.json`
- `cato-cli_tf_ci_read_only_tests/cctest/123/custom/Account_Metrics_-_Detailed_Bandwidth_Analysis_1764927919074.json`

## Error Handling

If AWS credentials are not configured, you'll see:
```
Error: AWS credentials not found. Please configure AWS credentials.
```

If the bucket doesn't exist or you don't have permissions:
```
Error uploading to S3 (NoSuchBucket): ...
```

## Dependencies

The S3 upload feature requires `boto3`:

```bash
pip install boto3
```

## Test Script

A test script is available at `tests/test_s3_upload.sh`:

```bash
./tests/test_s3_upload.sh
```

