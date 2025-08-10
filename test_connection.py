#!/usr/bin/env python3
"""
Simple connection test for N8N API
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('N8N_API_KEY')
base_url = os.getenv('N8N_BASE_URL')
cf_client_id = os.getenv('CF_ACCESS_CLIENT_ID')
cf_client_secret = os.getenv('CF_ACCESS_CLIENT_SECRET')

print(f"API Key: {api_key[:20]}..." if api_key else "API Key: None")
print(f"Base URL: {base_url}")
print(f"CF Client ID: {cf_client_id}")
print(f"CF Secret: {cf_client_secret[:20]}..." if cf_client_secret else "CF Secret: None")

# Ensure base URL has proper format
if not base_url.startswith('http'):
    base_url = f"https://{base_url}"
if not base_url.endswith('/api/v1'):
    base_url = f"{base_url.rstrip('/')}/api/v1"

print(f"Full API URL: {base_url}/workflows")

# Test different header combinations
test_cases = [
    {
        "name": "Only Bearer token",
        "headers": {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    },
    {
        "name": "Bearer token + Cloudflare headers",
        "headers": {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'CF-Access-Client-Id': cf_client_id,
            'CF-Access-Client-Secret': cf_client_secret
        }
    },
    {
        "name": "Only Cloudflare headers",
        "headers": {
            'CF-Access-Client-Id': cf_client_id,
            'CF-Access-Client-Secret': cf_client_secret
        }
    }
]

for test_case in test_cases:
    print(f"\n--- Testing: {test_case['name']} ---")
    try:
        response = requests.get(
            f"{base_url}/workflows",
            headers=test_case['headers'],
            timeout=10
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        if response.status_code != 200:
            print(f"Response Text: {response.text[:200]}...")
        else:
            print("✅ SUCCESS!")
            break
    except Exception as e:
        print(f"❌ Error: {e}")
