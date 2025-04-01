"""Integration tests for the Admin API endpoints."""

import os

import requests

# Base URL for the API - can be overridden with environment variable
BASE_URL = os.environ.get(
    "API_BASE_URL", "https://conecta-sat-70222b8ec91a.herokuapp.com"
)

# Admin credentials for testing
# These should match the credentials in the environment being tested
ADMIN_USERNAME = "admin"
# Determine which password to use based on the environment
if "herokuapp.com" in BASE_URL:
    # Heroku environment
    ADMIN_PASSWORD = "heroku-admin-password123"
else:
    # Local or other environment
    ADMIN_PASSWORD = "changeme"

print(f"Using API URL: {BASE_URL}")
print(f"Using admin credentials: {ADMIN_USERNAME}:{'*' * len(ADMIN_PASSWORD)}")


def test_admin_token_not_found() -> None:
    """Test token not found error path in production.

    This specifically tests the error handling when trying to access a non-existent
    token by ID, which will trigger the 404 error path in the admin.py file that is
    currently not covered.
    """
    # Set up auth with admin credentials
    auth = (ADMIN_USERNAME, ADMIN_PASSWORD)

    # Try to get a non-existent token with a very high ID that shouldn't exist
    url = f"{BASE_URL}/admin/tokens/99999"
    response = requests.get(url, auth=auth)

    # Verify 404 error is returned with an error message
    assert response.status_code == 404
    response_data = response.json()
    assert "detail" in response_data
    print(
        f"✅ Admin token not found test passed: {response.status_code} {response_data}"
    )


def test_admin_superadmin_not_found() -> None:
    """Test superadmin not found error path in production.

    This specifically tests the error handling when trying to deactivate a non-existent
    superadmin account, which will trigger the 404 error path in the admin.py file that
    is currently not covered.
    """
    # Set up auth with admin credentials
    auth = (ADMIN_USERNAME, ADMIN_PASSWORD)

    # Try to deactivate a non-existent superadmin account
    url = f"{BASE_URL}/admin/superadmins/nonexistentuser"
    response = requests.delete(url, auth=auth)

    # Verify 404 error is returned with an error message
    assert response.status_code == 404
    response_data = response.json()
    assert "detail" in response_data
    print(
        f"✅ Superadmin not found test passed: {response.status_code} {response_data}"
    )


def test_admin_regenerate_token_not_found() -> None:
    """Test token regeneration not found error path in production.

    This tests the error handling when trying to regenerate a token that doesn't exist,
    which will trigger another 404 path in admin.py.
    """
    # Set up auth with admin credentials
    auth = (ADMIN_USERNAME, ADMIN_PASSWORD)

    # Try to regenerate a non-existent token
    url = f"{BASE_URL}/admin/tokens/99999/regenerate"
    response = requests.post(url, auth=auth)

    # Verify 404 error is returned with an error message
    assert response.status_code == 404
    response_data = response.json()
    assert "detail" in response_data
    print(
        f"✅ Regenerate token not found test passed: "
        f"{response.status_code} {response_data}"
    )


def test_admin_update_password_not_found() -> None:
    """Test updating password for a non-existent admin account.

    This tests the error handling when trying to update the password for a non-existent
    admin account, which should trigger a 404 error path.
    """
    # Set up auth with admin credentials
    auth = (ADMIN_USERNAME, ADMIN_PASSWORD)

    # Password update data
    password_data = {"current_password": "changeme", "new_password": "newpassword123"}

    # Try to update password for a non-existent admin account
    url = f"{BASE_URL}/admin/superadmins/nonexistentuser/password"
    response = requests.put(url, json=password_data, auth=auth)

    # Verify 404 error is returned with an error message
    assert response.status_code == 404
    response_data = response.json()
    assert "detail" in response_data
    print(
        f"✅ Admin update password not found test passed: "
        f"{response.status_code} {response_data}"
    )


if __name__ == "__main__":
    print("======== Testing Admin API (Production) ========")

    print("\n🔍 Testing token not found error...")
    test_admin_token_not_found()

    print("\n🔍 Testing superadmin not found error...")
    test_admin_superadmin_not_found()

    print("\n🔍 Testing regenerate token not found error...")
    test_admin_regenerate_token_not_found()

    print("\n🔍 Testing update password not found error...")
    test_admin_update_password_not_found()

    print("\n✅ All admin API integration tests passed! ✅")
