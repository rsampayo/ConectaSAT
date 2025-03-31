import requests
import json

# Base URL for the API
BASE_URL = "https://conecta-sat-70222b8ec91a.herokuapp.com"

# Test the health endpoint
def test_health():
    url = f"{BASE_URL}/health"
    response = requests.get(url)
    print(f"Health status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    print("✅ Health endpoint working properly")

# Test the API documentation
def test_docs():
    url = f"{BASE_URL}/docs"
    response = requests.get(url)
    print(f"API docs status: {response.status_code}")
    assert response.status_code == 200
    print("✅ API documentation accessible")
    
    # Check for OpenAPI JSON
    openapi_url = f"{BASE_URL}/openapi.json"
    openapi_response = requests.get(openapi_url)
    print(f"OpenAPI schema status: {openapi_response.status_code}")
    assert openapi_response.status_code == 200
    print("✅ OpenAPI schema accessible")
    
    # Verify it's valid JSON and has the expected structure
    openapi_data = openapi_response.json()
    assert "paths" in openapi_data
    assert "components" in openapi_data
    assert "/cfdi/verify-cfdi" in str(openapi_data["paths"])
    print("✅ CFDI verification endpoints found in OpenAPI schema")
    
    # Verify that our new CFDI history endpoints are in the OpenAPI schema
    assert "/cfdi/history" in str(openapi_data["paths"])
    assert "/cfdi/history/{uuid}" in str(openapi_data["paths"])
    print("✅ CFDI history endpoints found in OpenAPI schema")

# Test the CFDI verification endpoint (without token should return 401 or 403)
def test_verify_cfdi_unauthorized():
    url = f"{BASE_URL}/cfdi/verify-cfdi"
    data = {
        "uuid": "6128396f-c09b-4ec6-8699-43c5f7e3b230",
        "emisor_rfc": "CDZ050722LA9",
        "receptor_rfc": "XIN06112344A",
        "total": "12000.00"
    }
    response = requests.post(url, json=data)
    print(f"CFDI verification status (without token): {response.status_code}")
    print(json.dumps(response.json(), indent=2) if response.content else "No response body")
    assert response.status_code in [401, 403]  # FastAPI returns 401 or 403 for missing token
    print("✅ CFDI verification correctly requires authentication")

# Test the CFDI batch verification endpoint (without token should return 401 or 403)
def test_verify_cfdi_batch_unauthorized():
    url = f"{BASE_URL}/cfdi/verify-cfdi-batch"
    data = {
        "cfdis": [
            {
                "uuid": "6128396f-c09b-4ec6-8699-43c5f7e3b230",
                "emisor_rfc": "CDZ050722LA9",
                "receptor_rfc": "XIN06112344A",
                "total": "12000.00"
            }
        ]
    }
    response = requests.post(url, json=data)
    print(f"CFDI batch verification status (without token): {response.status_code}")
    print(json.dumps(response.json(), indent=2) if response.content else "No response body")
    assert response.status_code in [401, 403]  # FastAPI returns 401 or 403 for missing token
    print("✅ CFDI batch verification correctly requires authentication")

# Test the CFDI history endpoint (without token should return 401 or 403)
def test_cfdi_history_unauthorized():
    url = f"{BASE_URL}/cfdi/history"
    response = requests.get(url)
    print(f"CFDI history status (without token): {response.status_code}")
    print(json.dumps(response.json(), indent=2) if response.content else "No response body")
    assert response.status_code in [401, 403]  # FastAPI returns 401 or 403 for missing token
    print("✅ CFDI history correctly requires authentication")

# Test the CFDI history by UUID endpoint (without token should return 401 or 403)
def test_cfdi_history_by_uuid_unauthorized():
    url = f"{BASE_URL}/cfdi/history/6128396f-c09b-4ec6-8699-43c5f7e3b230"
    response = requests.get(url)
    print(f"CFDI history by UUID status (without token): {response.status_code}")
    print(json.dumps(response.json(), indent=2) if response.content else "No response body")
    assert response.status_code in [401, 403]  # FastAPI returns 401 or 403 for missing token
    print("✅ CFDI history by UUID correctly requires authentication")

# Test with an invalid token
def test_with_invalid_token():
    headers = {"Authorization": "Bearer invalid-token"}
    
    # Test CFDI history with invalid token
    url = f"{BASE_URL}/cfdi/history"
    response = requests.get(url, headers=headers)
    print(f"CFDI history status (invalid token): {response.status_code}")
    print(json.dumps(response.json(), indent=2) if response.content else "No response body")
    assert response.status_code == 401  # Should return unauthorized
    print("✅ CFDI history correctly rejects invalid tokens")
    
    # Test CFDI history by UUID with invalid token
    url = f"{BASE_URL}/cfdi/history/6128396f-c09b-4ec6-8699-43c5f7e3b230"
    response = requests.get(url, headers=headers)
    print(f"CFDI history by UUID status (invalid token): {response.status_code}")
    print(json.dumps(response.json(), indent=2) if response.content else "No response body")
    assert response.status_code == 401  # Should return unauthorized
    print("✅ CFDI history by UUID correctly rejects invalid tokens")

# Main execution
if __name__ == "__main__":
    print("======== Testing API (Production) ========")
    print("\n🔍 Testing API health...")
    test_health()
    
    print("\n🔍 Testing API documentation...")
    test_docs()
    
    print("\n🔍 Testing CFDI verification (unauthorized)...")
    test_verify_cfdi_unauthorized()
    
    print("\n🔍 Testing CFDI batch verification (unauthorized)...")
    test_verify_cfdi_batch_unauthorized()
    
    print("\n🔍 Testing CFDI history (unauthorized)...")
    test_cfdi_history_unauthorized()
    
    print("\n🔍 Testing CFDI history by UUID (unauthorized)...")
    test_cfdi_history_by_uuid_unauthorized()
    
    print("\n🔍 Testing with invalid token...")
    test_with_invalid_token()
    
    print("\n✅ All tests passed successfully! ✅") 