"""
Unit tests for the SAT Verification service
"""
import pytest
from unittest.mock import patch, MagicMock
import xml.etree.ElementTree as ET
from app.services.sat_verification import verify_cfdi

# Sample XML responses for mocking
VALID_CFDI_XML = """<?xml version="1.0" encoding="utf-8"?>
<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
    <s:Body>
        <ConsultaResponse xmlns="http://tempuri.org/">
            <ConsultaResult CodigoEstatus="S - Comprobante obtenido satisfactoriamente." 
                           Estado="Vigente" 
                           EsCancelable="Cancelable sin aceptación" 
                           EstatusCancelacion=""/>
        </ConsultaResponse>
    </s:Body>
</s:Envelope>
"""

CANCELED_CFDI_XML = """<?xml version="1.0" encoding="utf-8"?>
<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
    <s:Body>
        <ConsultaResponse xmlns="http://tempuri.org/">
            <ConsultaResult CodigoEstatus="S - Comprobante obtenido satisfactoriamente." 
                           Estado="Cancelado" 
                           EsCancelable="No cancelable" 
                           EstatusCancelacion="Cancelado sin aceptación"/>
        </ConsultaResponse>
    </s:Body>
</s:Envelope>
"""

@pytest.mark.asyncio
async def test_verify_cfdi_valid():
    """Test verify_cfdi with a valid CFDI"""
    # Mock the requests.post response
    with patch('requests.post') as mock_post:
        # Configure the mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = VALID_CFDI_XML.encode('utf-8')
        mock_post.return_value = mock_response
        
        # Call the function
        result = await verify_cfdi(
            uuid="6128396f-c09b-4ec6-8699-43c5f7e3b230",
            emisor_rfc="CDZ050722LA9",
            receptor_rfc="XIN06112344A",
            total="12000.00"
        )
        
        # Assert results
        assert result["estado"] == "Vigente"
        assert result["es_cancelable"] == "Cancelable sin aceptación"
        assert result["estatus_cancelacion"] == "No disponible"
        assert result["codigo_estatus"] == "S - Comprobante obtenido satisfactoriamente."
        assert mock_post.called

@pytest.mark.asyncio
async def test_verify_cfdi_canceled():
    """Test verify_cfdi with a canceled CFDI"""
    # Mock the requests.post response
    with patch('requests.post') as mock_post:
        # Configure the mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = CANCELED_CFDI_XML.encode('utf-8')
        mock_post.return_value = mock_response
        
        # Call the function
        result = await verify_cfdi(
            uuid="6128396f-c09b-4ec6-8699-43c5f7e3b230",
            emisor_rfc="CDZ050722LA9",
            receptor_rfc="XIN06112344A",
            total="12000.00"
        )
        
        # Assert results
        assert result["estado"] == "Cancelado"
        assert result["es_cancelable"] == "No cancelable"
        assert result["estatus_cancelacion"] == "Cancelado sin aceptación"
        assert result["codigo_estatus"] == "S - Comprobante obtenido satisfactoriamente."
        assert mock_post.called

@pytest.mark.asyncio
async def test_verify_cfdi_connection_error():
    """Test verify_cfdi with a connection error"""
    # Mock the requests.post to raise an exception
    with patch('requests.post', side_effect=Exception("Connection error")):
        # Call the function and expect an exception
        with pytest.raises(Exception) as excinfo:
            await verify_cfdi(
                uuid="6128396f-c09b-4ec6-8699-43c5f7e3b230",
                emisor_rfc="CDZ050722LA9",
                receptor_rfc="XIN06112344A",
                total="12000.00"
            )
        
        assert "Connection error" in str(excinfo.value) 