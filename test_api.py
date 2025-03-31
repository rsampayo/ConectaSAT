import requests
import json

# Test the health endpoint
def test_health():
    url = "https://conecta-sat-70222b8ec91a.herokuapp.com/health"
    response = requests.get(url)
    print(f"Health status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

# Test the API documentation
def test_docs():
    url = "https://conecta-sat-70222b8ec91a.herokuapp.com/docs"
    response = requests.get(url)
    print(f"API docs status: {response.status_code}")
    assert response.status_code == 200
    
    # Check for OpenAPI JSON
    openapi_url = "https://conecta-sat-70222b8ec91a.herokuapp.com/openapi.json"
    openapi_response = requests.get(openapi_url)
    print(f"OpenAPI schema status: {openapi_response.status_code}")
    assert openapi_response.status_code == 200
    
    # Verify it's valid JSON and has the expected structure
    openapi_data = openapi_response.json()
    assert "paths" in openapi_data
    assert "components" in openapi_data
    assert "/verify-cfdi" in openapi_data["paths"]

# Test the CFDI verification endpoint (without token should return 403)
def test_verify_cfdi_unauthorized():
    url = "https://conecta-sat-70222b8ec91a.herokuapp.com/verify-cfdi"
    data = {
        "uuid": "6128396f-c09b-4ec6-8699-43c5f7e3b230",
        "emisor_rfc": "CDZ050722LA9",
        "receptor_rfc": "XIN06112344A",
        "total": "12000.00"
    }
    response = requests.post(url, json=data)
    print(f"CFDI verification status (without token): {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    assert response.status_code == 403  # FastAPI returns 403 for missing token

# Test the CFDI batch verification endpoint (without token should return 403)
def test_verify_cfdi_batch_unauthorized():
    url = "https://conecta-sat-70222b8ec91a.herokuapp.com/verify-cfdi-batch"
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
    print(json.dumps(response.json(), indent=2))
    assert response.status_code == 403  # FastAPI returns 403 for missing token

# Main execution
if __name__ == "__main__":
    print("Testing API health...")
    test_health()
    
    print("\nTesting API documentation...")
    test_docs()
    
    print("\nTesting CFDI verification (unauthorized)...")
    test_verify_cfdi_unauthorized()
    
    print("\nTesting CFDI batch verification (unauthorized)...")
    test_verify_cfdi_batch_unauthorized()
    
    print("\nAll tests passed!") 