# Quick Start Guide - Running Tests Locally

## Prerequisites Check ✅

- ✅ Python 3.13.5 installed
- ✅ catocli installed (version 3.0.42)
- ✅ pytest installed (version 9.0.1)

## Setup (if needed)

If you need to install dependencies:

```bash
# Install test dependencies
cd /Users/ramsar/work/cato-cli-test-new/tests
pip3 install -r requirements.txt

# Install catocli in development mode (if not already installed)
cd /Users/ramsar/work/cato-cli-test-new
pip3 install -e .
```

## Running Tests

### Basic Test Run

```bash
cd /Users/ramsar/work/cato-cli-test-new/tests
python3 run_all_tests.py
```

### Run with JSON Export (NEW!)

```bash
# Export test results to individual JSON files (one file per test)
python3 run_all_tests.py --json-output test_results/

# Export with external test report link
python3 run_all_tests.py --json-output test_results/ --external-test-report-link "https://example.com/report"

# Export with verbose output
python3 run_all_tests.py --json-output test_results/ --verbose
```

**Note:** Each test result is exported to its own JSON file in the specified directory. Files are named based on the test name (e.g., `query_appStats_-_Generated_Test.json`).

### Common Options

```bash
# Skip validation tests (faster)
python3 run_all_tests.py --skip-validation --json-output results/

# Run only specific operation tests
python3 run_all_tests.py --operation appStats --json-output appstats_results/

# Run only custom tests
python3 run_all_tests.py --skip-generated --skip-validation --json-output custom_results/

# Stop on first failure
python3 run_all_tests.py --stop-on-fail --json-output results/
```

## JSON Output Format

Each test result is exported to its own JSON file in the specified directory. The filename is derived from the test name (e.g., `query_appStats_-_Generated_Test.json`).

Each JSON file contains a single test result in this format:

```json
{
  "externalTestReportLink": "https://example.com/report",
  "steps": [
    {
      "startTime": 1747216742000,
      "endTime": 1747216748000,
      "name": "query.appStats - Generated Test",
      "status": "PASSED",
      "events": [
        {
          "startTime": 1747216742000,
          "level": "INFO",
          "event": "Starting test: query.appStats - Generated Test"
        },
        {
          "startTime": 1747216743000,
          "level": "INFO",
          "event": "Executing CLI command: query.appStats"
        }
      ]
    }
  ]
}
```

For failed tests, the format includes:

```json
{
  "steps": [
    {
      "startTime": 1747216762000,
      "endTime": 1747216768000,
      "name": "Test Name",
      "status": "FAILED",
      "failureMessage": "Error message; Assertion failures",
      "stackTrace": "catocli query appStats '{...}'",
      "events": [
        {
          "startTime": 1747216762000,
          "level": "ERROR",
          "event": "Command failed: ..."
        }
      ]
    }
  ]
}
```

## Example: Run a Quick Test

```bash
# Run a single operation test with JSON export
cd /Users/ramsar/work/cato-cli-test-new/tests
python3 run_all_tests.py --skip-validation --operation accountMetrics --json-output quick_test/ --verbose
```

## View JSON Results

After running tests, view the JSON files:

```bash
# List all JSON files created
ls test_results/

# Pretty print a specific JSON file
cat test_results/query_accountMetrics_-_Generated_Test.json | python3 -m json.tool

# View all JSON files
for file in test_results/*.json; do
  echo "=== $file ==="
  cat "$file" | python3 -m json.tool
done

# Or use jq if installed
cat test_results/*.json | jq '.'
```

## Troubleshooting

### If tests fail with "Module not found"
```bash
cd /Users/ramsar/work/cato-cli-test-new
pip3 install -e .
```

### If you need to configure catocli
```bash
catocli configure set --profile your_profile
```

### To see all available options
```bash
python3 run_all_tests.py --help
```

