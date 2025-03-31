"""Integration tests for the API endpoints with valid authentication token."""

import json
import sys

import pytest
import requests

# Base URL for the API
BASE_URL = "https://conecta-sat-70222b8ec91a.herokuapp.com"

# Default testing token
DEFAULT_TOKEN = "AfUjLGvif833mJedWq0k4jjmEwWphJ9C3z8Y3N0u8pI"


@pytest.fixture
def api_token():
    """Fixture to provide the API token for tests."""
    return DEFAULT_TOKEN


def test_with_valid_token(api_token):
    """Test API endpoints with a valid authentication token."""
    token = api_token
    headers = {"Authorization": f"Bearer {token}"}

    print("\n1. Testing CFDI verification with valid token...")
    # First, let's create a CFDI verification which should create a history entry
    verification_url = f"{BASE_URL}/cfdi/verify-cfdi"
    verification_data = {
        "uuid": "6128396f-c09b-4ec6-8699-43c5f7e3b230",
        "emisor_rfc": "CDZ050722LA9",
        "receptor_rfc": "XIN06112344A",
        "total": "12000.00",
    }

    verification_response = requests.post(
        verification_url, json=verification_data, headers=headers
    )

    print(f"CFDI verification status: {verification_response.status_code}")
    if verification_response.status_code == 200:
        print("✓ CFDI verification succeeded")
        verification_result = verification_response.json()
        print(json.dumps(verification_result, indent=2))
    else:
        print("✗ CFDI verification failed")
        print(
            json.dumps(verification_response.json(), indent=2)
            if verification_response.content
            else "No response body"
        )
        if verification_response.status_code == 401:
            print("The token provided might be invalid or expired.")
            return

    print("\n2. Testing CFDI history with valid token...")
    # Now, let's retrieve the history for all CFDIs
    history_url = f"{BASE_URL}/cfdi/history"
    history_response = requests.get(history_url, headers=headers)

    print(f"CFDI history status: {history_response.status_code}")
    if history_response.status_code == 200:
        print("✓ CFDI history retrieval succeeded")
        history_data = history_response.json()
        print(f"Found {len(history_data)} history entries")
        if history_data:
            print("First history entry:")
            print(json.dumps(history_data[0], indent=2))
    else:
        print("✗ CFDI history retrieval failed")
        print(
            json.dumps(history_response.json(), indent=2)
            if history_response.content
            else "No response body"
        )

    print("\n3. Testing CFDI history by UUID with valid token...")
    # Now, let's retrieve the history for a specific UUID
    uuid = "6128396f-c09b-4ec6-8699-43c5f7e3b230"
    history_by_uuid_url = f"{BASE_URL}/cfdi/history/{uuid}"
    history_by_uuid_response = requests.get(history_by_uuid_url, headers=headers)

    print(f"CFDI history by UUID status: {history_by_uuid_response.status_code}")
    if history_by_uuid_response.status_code == 200:
        print(f"✓ CFDI history retrieval for UUID {uuid} succeeded")
        history_data = history_by_uuid_response.json()
        print(f"Found {len(history_data)} history entries for this UUID")
        if history_data:
            print("First history entry for this UUID:")
            print(json.dumps(history_data[0], indent=2))
    else:
        print(f"✗ CFDI history retrieval for UUID {uuid} failed")
        print(
            json.dumps(history_by_uuid_response.json(), indent=2)
            if history_by_uuid_response.content
            else "No response body"
        )


if __name__ == "__main__":
    # Use the provided token or fall back to default
    token = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_TOKEN

    print(
        f"Testing API with token: {token[:5]}...{token[-5:] if len(token) > 10 else ''}"
    )
    test_with_valid_token(token)
