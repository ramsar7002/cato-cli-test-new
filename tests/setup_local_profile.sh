#!/bin/bash
# Setup script for local Cato CLI profile configuration
# Usage: ./setup_local_profile.sh

echo "Setting up Cato CLI profile for local testing..."
echo ""

# You can either:
# 1. Set these environment variables before running this script
# 2. Or edit this script to hardcode your values (not recommended for security)

if [ -z "$ACCOUNT_ID" ] || [ -z "$CATO_API_KEY" ]; then
    echo "Please set the following environment variables:"
    echo "  export ACCOUNT_ID='your_account_id'"
    echo "  export CATO_API_KEY='your_api_key'"
    echo "  export API_BASE_URL='https://api.catonetworks.com/api/v1/graphql2'  # optional"
    echo "  export SCIM_URL='your_scim_url'  # optional"
    echo "  export SCIM_TOKEN='your_scim_token'  # optional"
    echo ""
    echo "Or run the configure command manually:"
    echo "  catocli configure set --profile default --account-id YOUR_ID --cato-token YOUR_TOKEN"
    exit 1
fi

# Set defaults if not provided
API_BASE_URL=${API_BASE_URL:-"https://api.catonetworks.com/api/v1/graphql2"}

cd "$(dirname "$0")/.."

# Build the configure command
CONFIG_CMD="catocli configure set --profile default --account-id \"${ACCOUNT_ID}\" --cato-token \"${CATO_API_KEY}\" --endpoint \"${API_BASE_URL}\" --skip-validation"

# Add optional SCIM parameters if provided
if [ -n "$SCIM_URL" ]; then
    CONFIG_CMD="${CONFIG_CMD} --scim-url \"${SCIM_URL}\""
fi

if [ -n "$SCIM_TOKEN" ]; then
    CONFIG_CMD="${CONFIG_CMD} --scim-token \"${SCIM_TOKEN}\""
fi

echo "Running: $CONFIG_CMD"
eval $CONFIG_CMD

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Profile configured successfully!"
    echo ""
    echo "You can now run tests with:"
    echo "  cd tests && python3 run_all_tests.py --json-output results/"
else
    echo ""
    echo "✗ Configuration failed. Please check your credentials."
    exit 1
fi

