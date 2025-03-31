"""
Integration tests for CFDI History API endpoints
"""

import pytest
from fastapi.testclient import TestClient

from app.core.deps import get_current_token, get_user_id_from_token
from app.main import app
from app.services.cfdi_history import create_cfdi_history


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


def test_get_cfdi_history_authenticated(
    client, db_session, override_get_token_dependency
):
    """Test getting CFDI history when authenticated"""
    # Create test data
    cfdi_data = {
        "uuid": "6128396f-c09b-4ec6-8699-43c5f7e3b230",
        "emisor_rfc": "CDZ050722LA9",
        "receptor_rfc": "XIN06112344A",
        "total": "12000.00",
        "user_id": 1,
        "estado": "Vigente",
        "es_cancelable": "Cancelable sin aceptación",
        "estatus_cancelacion": "No cancelado",
        "codigo_estatus": "S - Comprobante obtenido satisfactoriamente",
        "validacion_efos": "200",
    }
    create_cfdi_history(db_session, **cfdi_data)

    # Override the get_user_id_from_token dependency
    original_get_user_id = app.dependency_overrides.get(get_user_id_from_token, None)
    app.dependency_overrides[get_user_id_from_token] = lambda: 1

    try:
        # Make request
        response = client.get(
            "/cfdi/history", headers={"Authorization": "Bearer test-token"}
        )

        # Assert response
        assert response.status_code == 200

        # Check response data
        history_data = response.json()
        assert isinstance(history_data, list)
        assert len(history_data) >= 1

        # Verify the data
        found = False
        for item in history_data:
            if item["uuid"] == cfdi_data["uuid"]:
                found = True
                assert item["emisor_rfc"] == cfdi_data["emisor_rfc"]
                assert item["receptor_rfc"] == cfdi_data["receptor_rfc"]
                assert item["total"] == cfdi_data["total"]
                assert item["estado"] == cfdi_data["estado"]
                break

        assert found, "Created CFDI history item not found in response"
    finally:
        # Restore the original dependency
        if original_get_user_id:
            app.dependency_overrides[get_user_id_from_token] = original_get_user_id
        else:
            del app.dependency_overrides[get_user_id_from_token]


def test_get_cfdi_history_by_uuid(client, db_session, override_get_token_dependency):
    """Test getting CFDI history for a specific UUID"""
    # Create test data
    uuid = "6128396f-c09b-4ec6-8699-43c5f7e3b230"
    cfdi_data = {
        "uuid": uuid,
        "emisor_rfc": "CDZ050722LA9",
        "receptor_rfc": "XIN06112344A",
        "total": "12000.00",
        "user_id": 1,
        "estado": "Vigente",
        "es_cancelable": "Cancelable sin aceptación",
        "estatus_cancelacion": "No cancelado",
        "codigo_estatus": "S - Comprobante obtenido satisfactoriamente",
        "validacion_efos": "200",
    }
    create_cfdi_history(db_session, **cfdi_data)

    # Override the get_user_id_from_token dependency
    original_get_user_id = app.dependency_overrides.get(get_user_id_from_token, None)
    app.dependency_overrides[get_user_id_from_token] = lambda: 1

    try:
        # Make request
        response = client.get(
            f"/cfdi/history/{uuid}", headers={"Authorization": "Bearer test-token"}
        )

        # Assert response
        assert response.status_code == 200

        # Check response data
        history_data = response.json()
        assert isinstance(history_data, list)
        assert len(history_data) >= 1

        # Verify the data
        item = history_data[0]
        assert item["uuid"] == uuid
        assert item["emisor_rfc"] == cfdi_data["emisor_rfc"]
        assert item["receptor_rfc"] == cfdi_data["receptor_rfc"]
        assert item["total"] == cfdi_data["total"]
        assert item["estado"] == cfdi_data["estado"]
    finally:
        # Restore the original dependency
        if original_get_user_id:
            app.dependency_overrides[get_user_id_from_token] = original_get_user_id
        else:
            del app.dependency_overrides[get_user_id_from_token]


def test_get_cfdi_history_unauthorized(client, db_session):
    """Test that history endpoint requires authentication"""
    # Test without a token
    try:
        # We need to temporarily remove the override for get_current_token
        # to test the unauthorized case
        app.dependency_overrides.pop(get_current_token, None)

        # Make request without token
        response = client.get("/cfdi/history")

        # Assert response requires authentication
        assert (
            response.status_code == 403
        )  # FastAPI's HTTPBearer raises HTTPException 403 by default
    finally:
        # Restore the original dependency (if it exists)
        # We don't restore it here since we don't know the original,
        # the other tests will set up their own overrides
        pass


def test_verify_cfdi_creates_history(client, db_session, override_get_token_dependency):
    """Test that verifying a CFDI automatically creates a history entry"""
    # Prepare test data
    test_data = {
        "uuid": "6128396f-c09b-4ec6-8699-43c5f7e3b230",
        "emisor_rfc": "CDZ050722LA9",
        "receptor_rfc": "XIN06112344A",
        "total": "12000.00",
    }

    # Override the get_user_id_from_token dependency
    original_get_user_id = app.dependency_overrides.get(get_user_id_from_token, None)
    app.dependency_overrides[get_user_id_from_token] = lambda: 1

    try:
        # Need to mock the actual SAT verification since this is an integration test
        # For a real test, you might want to use dependency_overrides to mock the SAT service

        # Make verify-cfdi request
        with pytest.MonkeyPatch.context() as m:
            # Mock the SAT verification service response
            m.setattr(
                "app.services.sat_verification.verify_cfdi",
                lambda uuid, emisor_rfc, receptor_rfc, total: {
                    "estado": "Vigente",
                    "es_cancelable": "Cancelable sin aceptación",
                    "estatus_cancelacion": "No cancelado",
                    "codigo_estatus": "S - Comprobante obtenido satisfactoriamente",
                    "validacion_efos": "200",
                    "raw_response": "<xml>test</xml>",
                },
            )

            response = client.post(
                "/cfdi/verify-cfdi",
                json=test_data,
                headers={"Authorization": "Bearer test-token"},
            )

        # Assert verify response is successful
        assert response.status_code == 200

        # Now get history to check if entry was created
        history_response = client.get(
            f"/cfdi/history/{test_data['uuid']}",
            headers={"Authorization": "Bearer test-token"},
        )

        # Assert history response
        assert history_response.status_code == 200
        history_data = history_response.json()

        # Verify a history entry was created for this CFDI
        assert len(history_data) >= 1
        found = False
        for item in history_data:
            if item["uuid"] == test_data["uuid"]:
                found = True
                assert item["emisor_rfc"] == test_data["emisor_rfc"]
                assert item["receptor_rfc"] == test_data["receptor_rfc"]
                assert item["total"] == test_data["total"]
                break

        assert found, "CFDI history entry not created during verification"
    finally:
        # Restore the original dependency
        if original_get_user_id:
            app.dependency_overrides[get_user_id_from_token] = original_get_user_id
        else:
            del app.dependency_overrides[get_user_id_from_token]
