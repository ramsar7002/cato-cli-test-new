#!/usr/bin/env python3
"""
Upload existing test result JSON files to S3

Usage:
    python3 upload_results_to_s3.py \
        --results-dir results/ \
        --s3-region eu-central-1 \
        --s3-bucket external-test-results \
        --s3-test-framework-repo-name cato-cli_tf_ci_read_only_tests \
        --s3-catomatic-cycle cctest \
        --s3-catomatic-run-id 123
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path

# ANSI color codes
class Colors:
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    BOLD = '\033[1m'
    NC = '\033[0m'  # No Color


def determine_suite_name(json_file: Path) -> str:
    """
    Determine suite name (generated or custom) from JSON file content.
    Returns 'generated' or 'custom' based on test name pattern.
    """
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check steps for test name
        if 'steps' in data and len(data['steps']) > 0:
            test_name = data['steps'][0].get('name', '')
            
            # Generated tests typically have "- Generated Test" suffix
            if '- Generated Test' in test_name:
                return 'generated'
            # Custom tests usually have descriptive names without that suffix
            else:
                return 'custom'
    except Exception:
        pass
    
    # Default to generated if we can't determine
    return 'generated'


def upload_to_s3(results_dir: Path, s3_config: dict, verbose: bool = False, verify_ssl: bool = False):
    """Upload JSON files from results directory to S3"""
    try:
        import boto3
        from botocore.exceptions import ClientError, NoCredentialsError
        from botocore.config import Config
    except ImportError:
        print(f"{Colors.RED}Error: boto3 is required. Install with: pip install boto3{Colors.NC}")
        return False
    
    region = s3_config.get('region', 'eu-central-1')
    bucket = s3_config.get('bucket', 'external-test-results')
    test_framework_repo_name = s3_config.get('testFrameworkRepoName', '')
    catomatic_cycle = s3_config.get('catomaticCycle', '')
    catomatic_run_id = s3_config.get('catomaticRunId', '')
    catomatic_suite_name = s3_config.get('catomaticSuiteName', '')
    catomatic_timestamp = s3_config.get('catomaticTimestamp', '')
    
    # Generate timestamp if not provided
    if not catomatic_timestamp:
        catomatic_timestamp = int(time.time() * 1000)  # milliseconds
    else:
        # Convert to int if provided as string
        try:
            catomatic_timestamp = int(catomatic_timestamp)
        except (ValueError, TypeError):
            print(f"{Colors.YELLOW}Warning: Invalid timestamp format, generating new timestamp{Colors.NC}")
            catomatic_timestamp = int(time.time() * 1000)
    
    # Find all JSON files in results directory
    json_files = list(results_dir.glob('*.json'))
    
    if not json_files:
        print(f"{Colors.YELLOW}No JSON files found in {results_dir}{Colors.NC}")
        return False
    
    print(f"{Colors.CYAN}Found {len(json_files)} JSON file(s) to upload{Colors.NC}\n")
    
    try:
        # Create S3 client with SSL verification config
        config = Config(
            signature_version='s3v4',
            retries={'max_attempts': 3, 'mode': 'standard'}
        )
        
        # Configure SSL verification
        if not verify_ssl:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            # Monkey patch botocore's URLLib3Session to disable SSL verification
            import botocore.httpsession
            original_init = botocore.httpsession.URLLib3Session.__init__
            
            def patched_init(self, *args, **kwargs):
                kwargs['verify'] = False
                return original_init(self, *args, **kwargs)
            
            botocore.httpsession.URLLib3Session.__init__ = patched_init
        
        s3_client = boto3.client('s3', region_name=region, config=config)
        
        uploaded_count = 0
        failed_count = 0
        
        for json_file in json_files:
            # Use provided suite name or determine from file content
            if catomatic_suite_name:
                suite_name = catomatic_suite_name
            else:
                suite_name = determine_suite_name(json_file)
            
            # Get test name from JSON file
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if 'steps' in data and len(data['steps']) > 0:
                    test_name = data['steps'][0].get('name', json_file.stem)
                else:
                    test_name = json_file.stem
            except Exception:
                test_name = json_file.stem
            
            # Sanitize test name for S3 key
            safe_test_name = re.sub(r'[<>:"/\\|?*]', '_', test_name)
            safe_test_name = re.sub(r'\s+', '_', safe_test_name)
            safe_test_name = safe_test_name[:200]  # Limit length
            
            # Build S3 key path
            s3_key = f"{test_framework_repo_name}/{catomatic_cycle}/{catomatic_run_id}/{suite_name}/{safe_test_name}_{catomatic_timestamp}.json"
            
            try:
                # Upload file to S3
                s3_client.upload_file(
                    str(json_file),
                    bucket,
                    s3_key,
                    ExtraArgs={'ContentType': 'application/json'}
                )
                
                print(f"{Colors.GREEN}✓ Uploaded: {json_file.name}{Colors.NC}")
                if verbose:
                    print(f"  {Colors.CYAN}s3://{bucket}/{s3_key}{Colors.NC}")
                uploaded_count += 1
            except Exception as e:
                print(f"{Colors.RED}✗ Failed to upload {json_file.name}: {str(e)}{Colors.NC}")
                failed_count += 1
        
        print(f"\n{Colors.BOLD}Upload Summary:{Colors.NC}")
        print(f"{Colors.GREEN}  Uploaded: {uploaded_count}{Colors.NC}")
        if failed_count > 0:
            print(f"{Colors.RED}  Failed: {failed_count}{Colors.NC}")
        
        return failed_count == 0
        
    except NoCredentialsError:
        print(f"{Colors.RED}Error: AWS credentials not found. Please configure AWS credentials.{Colors.NC}")
        print(f"{Colors.YELLOW}  Run: aws configure{Colors.NC}")
        print(f"{Colors.YELLOW}  Or set environment variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY{Colors.NC}")
        return False
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        print(f"{Colors.RED}Error uploading to S3 ({error_code}): {str(e)}{Colors.NC}")
        return False
    except Exception as e:
        print(f"{Colors.RED}Error uploading to S3: {str(e)}{Colors.NC}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Upload existing test result JSON files to S3',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Upload results with all required parameters
  %(prog)s --results-dir results/ \\
      --s3-test-framework-repo-name cato-cli_tf_ci_read_only_tests \\
      --s3-catomatic-cycle cctest \\
      --s3-catomatic-run-id 123

  # With custom region and bucket
  %(prog)s --results-dir results/ \\
      --s3-region us-east-1 \\
      --s3-bucket my-test-results \\
      --s3-test-framework-repo-name my-repo \\
      --s3-catomatic-cycle cycle1 \\
      --s3-catomatic-run-id 456 \\
      --verbose
        """
    )
    
    parser.add_argument(
        '--results-dir',
        type=Path,
        required=True,
        help='Directory containing JSON result files',
        metavar='DIR'
    )
    parser.add_argument(
        '--s3-region',
        type=str,
        default='eu-central-1',
        help='AWS S3 region (default: eu-central-1)',
        metavar='REGION'
    )
    parser.add_argument(
        '--s3-bucket',
        type=str,
        default='external-test-results',
        help='AWS S3 bucket name (default: external-test-results)',
        metavar='BUCKET'
    )
    parser.add_argument(
        '--s3-test-framework-repo-name',
        type=str,
        required=True,
        help='Test framework repository name for S3 path',
        metavar='NAME'
    )
    parser.add_argument(
        '--s3-catomatic-cycle',
        type=str,
        required=True,
        help='Catomatic cycle name for S3 path',
        metavar='CYCLE'
    )
    parser.add_argument(
        '--s3-catomatic-run-id',
        type=str,
        required=True,
        help='Catomatic run ID for S3 path',
        metavar='ID'
    )
    parser.add_argument(
        '--s3-catomatic-suite-name',
        type=str,
        help='Catomatic suite name for S3 path (default: auto-detect from test type)',
        metavar='NAME'
    )
    parser.add_argument(
        '--s3-catomatic-timestamp',
        type=str,
        help='Catomatic timestamp in milliseconds (default: current timestamp)',
        metavar='TIMESTAMP'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    parser.add_argument(
        '--verify-ssl',
        action='store_true',
        help='Enable SSL certificate verification (disabled by default)'
    )
    
    args = parser.parse_args()
    
    # Validate results directory
    if not args.results_dir.exists():
        print(f"{Colors.RED}Error: Results directory does not exist: {args.results_dir}{Colors.NC}")
        sys.exit(1)
    
    if not args.results_dir.is_dir():
        print(f"{Colors.RED}Error: Path is not a directory: {args.results_dir}{Colors.NC}")
        sys.exit(1)
    
    # Build S3 config
    s3_config = {
        'region': args.s3_region,
        'bucket': args.s3_bucket,
        'testFrameworkRepoName': args.s3_test_framework_repo_name,
        'catomaticCycle': args.s3_catomatic_cycle,
        'catomaticRunId': args.s3_catomatic_run_id,
        'catomaticSuiteName': args.s3_catomatic_suite_name or '',
        'catomaticTimestamp': args.s3_catomatic_timestamp or ''
    }
    
    print(f"{Colors.BLUE}{'='*70}{Colors.NC}")
    print(f"{Colors.BOLD}Uploading Test Results to S3{Colors.NC}")
    print(f"{Colors.BLUE}{'='*70}{Colors.NC}\n")
    
    print(f"Results Directory: {args.results_dir}")
    print(f"S3 Bucket: {args.s3_bucket}")
    print(f"S3 Region: {args.s3_region}")
    print(f"Repository: {args.s3_test_framework_repo_name}")
    print(f"Cycle: {args.s3_catomatic_cycle}")
    print(f"Run ID: {args.s3_catomatic_run_id}")
    if args.s3_catomatic_suite_name:
        print(f"Suite Name: {args.s3_catomatic_suite_name}")
    else:
        print(f"Suite Name: auto-detect")
    if args.s3_catomatic_timestamp:
        print(f"Timestamp: {args.s3_catomatic_timestamp}")
    else:
        print(f"Timestamp: auto-generate")
    print()
    
    # Upload files (SSL verification disabled by default)
    verify_ssl = args.verify_ssl
    success = upload_to_s3(args.results_dir, s3_config, args.verbose, verify_ssl)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()

