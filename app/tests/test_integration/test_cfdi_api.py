"""
Integration tests for the CFDI API endpoints
"""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.core.deps import get_current_token
from app.main import app

# Create TestClient
client = TestClient(app)

# Mock data
valid_cfdi_response = {
    "estado": "Vigente",
    "es_cancelable": "Cancelable sin aceptación",
    "estatus_cancelacion": "No disponible",
    "codigo_estatus": "S - Comprobante obtenido satisfactoriamente.",
    "raw_response": "<xml>test</xml>",
}


# Mock the token verification
@pytest.fixture(autouse=True)
def mock_token_verification():
    """
    Override the token dependency to skip authentication
    """

    async def override_get_current_token():
        return "fake_token"

    app.dependency_overrides[get_current_token] = override_get_current_token
    yield
    app.dependency_overrides.pop(get_current_token)


@pytest.fixture
def mock_verify_cfdi():
    with patch("app.api.cfdi.verify_cfdi", new_callable=AsyncMock) as mock:
        mock.return_value = valid_cfdi_response
        yield mock


def test_verify_cfdi_endpoint(mock_verify_cfdi):
    """Test the /verify-cfdi endpoint"""
    # Test data
    request_data = {
        "uuid": "6128396f-c09b-4ec6-8699-43c5f7e3b230",
        "emisor_rfc": "CDZ050722LA9",
        "receptor_rfc": "XIN06112344A",
        "total": "12000.00",
    }

    # Add a mock token for authorization
    headers = {"Authorization": "Bearer fake_token"}

    # Send request to the endpoint
    response = client.post("/cfdi/verify-cfdi", json=request_data, headers=headers)
    
    # Debug what's different
    print("EXPECTED:", valid_cfdi_response)
    print("ACTUAL:", response.json())

    # Assert the response
    assert response.status_code == 200
    # Deep comparison (ignoring any extra fields in the response)
    response_json = response.json()
    for key, value in valid_cfdi_response.items():
        assert key in response_json, f"Key {key} missing from response"
        assert response_json[key] == value, f"Value mismatch for {key}: expected {value}, got {response_json[key]}"

    # Verify the service was called with the right parameters
    mock_verify_cfdi.assert_called_once_with(
        request_data["uuid"],
        request_data["emisor_rfc"],
        request_data["receptor_rfc"],
        request_data["total"],
    )


def test_verify_cfdi_batch_endpoint(mock_verify_cfdi):
    """Test the /verify-cfdi-batch endpoint"""
    # Test data
    request_data = {
        "cfdis": [
            {
                "uuid": "6128396f-c09b-4ec6-8699-43c5f7e3b230",
                "emisor_rfc": "CDZ050722LA9",
                "receptor_rfc": "XIN06112344A",
                "total": "12000.00",
            },
            {
                "uuid": "abcdef12-c09b-4ec6-8699-43c5f7e3b230",
                "emisor_rfc": "CDZ050722LA9",
                "receptor_rfc": "XIN06112344A",
                "total": "5000.00",
            },
        ]
    }

    # Add a mock token for authorization
    headers = {"Authorization": "Bearer fake_token"}

    # Send request to the endpoint
    response = client.post(
        "/cfdi/verify-batch", json=request_data, headers=headers
    )

    # Assert the response
    assert response.status_code == 200
    # Should get back array of results
    results = response.json()["results"]
    assert len(results) == 2

    # Verify each CFDI request has a response
    for i, cfdi_result in enumerate(results):
        assert cfdi_result["request"] == request_data["cfdis"][i]
        
        # Deep comparison for each response
        response_data = cfdi_result["response"]
        for key, value in valid_cfdi_response.items():
            assert key in response_data, f"Key {key} missing from response {i}"
            assert response_data[key] == value, f"Value mismatch for {key} in response {i}: expected {value}, got {response_data[key]}"

    # Verify the service was called for each CFDI
    assert mock_verify_cfdi.call_count == 2


def test_health_endpoint():
    """Test the /health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
