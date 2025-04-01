"""Unit tests for the SAT Verification service."""

import xml.etree.ElementTree as ET
from unittest.mock import MagicMock, patch

import pytest
import requests

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

# Alternative XML format with different namespaces
ALTERNATIVE_XML_FORMAT = """<?xml version="1.0" encoding="utf-8"?>
<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
    <s:Body>
        <ConsultaResponse xmlns="http://tempuri.org/">
            <ConsultaResult>
                <a:CodigoEstatus xmlns:a="http://schemas.datacontract.org/2004/07/Sat.Cfdi.Negocio.ConsultaCfdi.Servicio">S - Comprobante obtenido satisfactoriamente.</a:CodigoEstatus>
                <a:Estado xmlns:a="http://schemas.datacontract.org/2004/07/Sat.Cfdi.Negocio.ConsultaCfdi.Servicio">Vigente</a:Estado>
                <a:EsCancelable xmlns:a="http://schemas.datacontract.org/2004/07/Sat.Cfdi.Negocio.ConsultaCfdi.Servicio">Cancelable sin aceptación</a:EsCancelable>
                <a:EstatusCancelacion xmlns:a="http://schemas.datacontract.org/2004/07/Sat.Cfdi.Negocio.ConsultaCfdi.Servicio"></a:EstatusCancelacion>
                <a:ValidacionEFOS xmlns:a="http://schemas.datacontract.org/2004/07/Sat.Cfdi.Negocio.ConsultaCfdi.Servicio">200</a:ValidacionEFOS>
            </ConsultaResult>
        </ConsultaResponse>
    </s:Body>
</s:Envelope>
"""

XML_WITH_VALIDATION_EFOS = """<?xml version="1.0" encoding="utf-8"?>
<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
    <s:Body>
        <ConsultaResponse xmlns="http://tempuri.org/">
            <ConsultaResult CodigoEstatus="S - Comprobante obtenido satisfactoriamente."
                           Estado="Vigente"
                           EsCancelable="Cancelable sin aceptación"
                           EstatusCancelacion=""
                           ValidacionEFOS="200"/>
        </ConsultaResponse>
    </s:Body>
</s:Envelope>
"""


@pytest.mark.asyncio
async def test_verify_cfdi_valid():
    """Test verify_cfdi with a valid CFDI."""
    # Mock the requests.post response
    with patch("requests.post") as mock_post:
        # Configure the mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = VALID_CFDI_XML.encode("utf-8")
        mock_post.return_value = mock_response

        # Call the function
        result = await verify_cfdi(
            uuid="6128396f-c09b-4ec6-8699-43c5f7e3b230",
            emisor_rfc="CDZ050722LA9",
            receptor_rfc="XIN06112344A",
            total="12000.00",
        )

        # Assert results
        assert result["estado"] == "Vigente"
        assert result["es_cancelable"] == "Cancelable sin aceptación"
        assert result["estatus_cancelacion"] == "No disponible"
        assert (
            result["codigo_estatus"] == "S - Comprobante obtenido satisfactoriamente."
        )
        assert mock_post.called


@pytest.mark.asyncio
async def test_verify_cfdi_canceled():
    """Test verify_cfdi with a canceled CFDI."""
    # Mock the requests.post response
    with patch("requests.post") as mock_post:
        # Configure the mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = CANCELED_CFDI_XML.encode("utf-8")
        mock_post.return_value = mock_response

        # Call the function
        result = await verify_cfdi(
            uuid="6128396f-c09b-4ec6-8699-43c5f7e3b230",
            emisor_rfc="CDZ050722LA9",
            receptor_rfc="XIN06112344A",
            total="12000.00",
        )

        # Assert results
        assert result["estado"] == "Cancelado"
        assert result["es_cancelable"] == "No cancelable"
        assert result["estatus_cancelacion"] == "Cancelado sin aceptación"
        assert (
            result["codigo_estatus"] == "S - Comprobante obtenido satisfactoriamente."
        )
        assert mock_post.called


@pytest.mark.asyncio
async def test_verify_cfdi_connection_error():
    """Test verify_cfdi with a connection error."""
    # Mock the requests.post to raise an exception
    with patch("requests.post", side_effect=Exception("Connection error")):
        # Call the function and expect an exception
        with pytest.raises(Exception) as excinfo:
            await verify_cfdi(
                uuid="6128396f-c09b-4ec6-8699-43c5f7e3b230",
                emisor_rfc="CDZ050722LA9",
                receptor_rfc="XIN06112344A",
                total="12000.00",
            )

        assert "Connection error" in str(excinfo.value)


@pytest.mark.asyncio
async def test_verify_cfdi_http_error():
    """Test verify_cfdi with an HTTP error from the SAT service."""
    # Mock the requests.post response with a non-200 status code
    with patch("requests.post") as mock_post:
        # Configure the mock
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response

        # Call the function and expect an exception
        with pytest.raises(Exception) as excinfo:
            await verify_cfdi(
                uuid="6128396f-c09b-4ec6-8699-43c5f7e3b230",
                emisor_rfc="CDZ050722LA9",
                receptor_rfc="XIN06112344A",
                total="12000.00",
            )

        assert "SAT service error: 500" in str(excinfo.value)


@pytest.mark.asyncio
async def test_verify_cfdi_request_exception():
    """Test verify_cfdi with a requests.RequestException."""
    # Mock the requests.post to raise a RequestException
    with patch(
        "requests.post", side_effect=requests.RequestException("Connection refused")
    ):
        # Call the function and expect an exception
        with pytest.raises(Exception) as excinfo:
            await verify_cfdi(
                uuid="6128396f-c09b-4ec6-8699-43c5f7e3b230",
                emisor_rfc="CDZ050722LA9",
                receptor_rfc="XIN06112344A",
                total="12000.00",
            )

        assert "Error connecting to SAT service" in str(excinfo.value)


@pytest.mark.asyncio
async def test_verify_cfdi_invalid_xml():
    """Test verify_cfdi with an invalid XML response."""
    # Mock the requests.post response
    with patch("requests.post") as mock_post:
        # Configure the mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"Invalid XML"
        mock_post.return_value = mock_response

        # Call the function and expect an exception
        with pytest.raises(Exception) as excinfo:
            await verify_cfdi(
                uuid="6128396f-c09b-4ec6-8699-43c5f7e3b230",
                emisor_rfc="CDZ050722LA9",
                receptor_rfc="XIN06112344A",
                total="12000.00",
            )

        assert "syntax error" in str(
            excinfo.value
        ) or "Error parsing SAT response" in str(excinfo.value)


@pytest.mark.asyncio
async def test_verify_cfdi_alternative_xml_format():
    """Test verify_cfdi with an alternative XML format."""
    # Mock the requests.post response
    with patch("requests.post") as mock_post:
        # Configure the mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = ALTERNATIVE_XML_FORMAT.encode("utf-8")
        mock_post.return_value = mock_response

        # Call the function
        result = await verify_cfdi(
            uuid="6128396f-c09b-4ec6-8699-43c5f7e3b230",
            emisor_rfc="CDZ050722LA9",
            receptor_rfc="XIN06112344A",
            total="12000.00",
        )

        # Assert results
        assert result["estado"] == "Vigente"
        assert result["es_cancelable"] == "Cancelable sin aceptación"
        assert result["estatus_cancelacion"] == "No disponible"
        assert (
            result["codigo_estatus"] == "S - Comprobante obtenido satisfactoriamente."
        )
        assert result["validacion_efos"] == "200"
        assert mock_post.called


@pytest.mark.asyncio
async def test_verify_cfdi_with_validacion_efos():
    """Test verify_cfdi with EFOS validation in the response."""
    # Mock the requests.post response
    with patch("requests.post") as mock_post:
        # Configure the mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = XML_WITH_VALIDATION_EFOS.encode("utf-8")
        mock_post.return_value = mock_response

        # Call the function
        result = await verify_cfdi(
            uuid="6128396f-c09b-4ec6-8699-43c5f7e3b230",
            emisor_rfc="CDZ050722LA9",
            receptor_rfc="XIN06112344A",
            total="12000.00",
        )

        # Assert results
        assert result["estado"] == "Vigente"
        assert result["es_cancelable"] == "Cancelable sin aceptación"
        assert result["estatus_cancelacion"] == "No disponible"
        assert (
            result["codigo_estatus"] == "S - Comprobante obtenido satisfactoriamente."
        )
        assert result["validacion_efos"] == "200"
        assert mock_post.called


@pytest.mark.asyncio
async def test_verify_cfdi_with_xml_parsing_error():
    """Test verify_cfdi with an error during XML parsing."""
    # Mock the requests.post response
    with (
        patch("requests.post") as mock_post,
        patch(
            "xml.etree.ElementTree.fromstring",
            side_effect=ET.ParseError("XML parsing error"),
        ),
    ):

        # Configure the mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = VALID_CFDI_XML.encode("utf-8")
        mock_post.return_value = mock_response

        # Call the function and expect an exception
        with pytest.raises(Exception) as excinfo:
            await verify_cfdi(
                uuid="6128396f-c09b-4ec6-8699-43c5f7e3b230",
                emisor_rfc="CDZ050722LA9",
                receptor_rfc="XIN06112344A",
                total="12000.00",
            )

        assert "Error parsing SAT response" in str(excinfo.value)


@pytest.mark.asyncio
async def test_verify_cfdi_special_xml_format():
    """Test verify_cfdi with special XML format where findall returns empty and direct
    attributes are used."""
    # XML with direct attributes on ConsultaResult
    SPECIAL_XML_FORMAT = """<?xml version="1.0" encoding="utf-8"?>
    <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
        <s:Body>
            <ConsultaResponse xmlns="http://tempuri.org/">
                <ConsultaResult Estado="Vigente"
                               EsCancelable="Cancelable sin aceptación"
                               EstatusCancelacion="No cancelado"
                               CodigoEstatus="S - Comprobante obtenido satisfactoriamente."/>
            </ConsultaResponse>
        </s:Body>
    </s:Envelope>
    """

    # Mock the requests.post response
    with patch("requests.post") as mock_post:
        # Configure the mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = SPECIAL_XML_FORMAT.encode("utf-8")
        mock_post.return_value = mock_response

        # Here we patch ET.fromstring to return our own mock Element
        # This allows us to control the behavior of findall and find methods
        original_fromstring = ET.fromstring

        def mock_fromstring(content):
            # Create a real element from the XML
            real_element = original_fromstring(content)

            # Create a mock to wrap it with our custom behavior
            mock_element = MagicMock()

            # Make findall return empty list for a:Estado to trigger special path
            def mock_findall(path, namespaces=None):
                if "a:Estado" in path:
                    return []
                # For other paths, return real element's findall result
                return real_element.findall(path, namespaces)

            # Make find work for retrieving ConsultaResult with attributes
            def mock_find(path, namespaces=None):
                if path == ".//ConsultaResult":
                    # Create an attributes dict matching the XML
                    attr_mock = MagicMock()
                    attr_mock.attrib = {
                        "Estado": "Vigente",
                        "EsCancelable": "Cancelable sin aceptación",
                        "EstatusCancelacion": "No cancelado",
                        "CodigoEstatus": "S - Comprobante obtenido satisfactoriamente.",
                    }
                    return attr_mock
                # For other paths like a:Estado, return None to trigger special path
                if "a:" in path:
                    return None
                # For other paths, return real element's find result
                return real_element.find(path, namespaces)

            # Assign our mock methods
            mock_element.findall = mock_findall
            mock_element.find = mock_find

            # Return the mock element
            return mock_element

        # Patch ET.fromstring
        with patch("xml.etree.ElementTree.fromstring", mock_fromstring):
            # Call the function
            result = await verify_cfdi(
                uuid="6128396f-c09b-4ec6-8699-43c5f7e3b230",
                emisor_rfc="CDZ050722LA9",
                receptor_rfc="XIN06112344A",
                total="12000.00",
            )

            # Assert results
            assert result["estado"] == "Vigente"
            assert result["es_cancelable"] == "Cancelable sin aceptación"
            assert result["estatus_cancelacion"] == "No cancelado"
            assert (
                result["codigo_estatus"]
                == "S - Comprobante obtenido satisfactoriamente."
            )
            assert mock_post.called


@pytest.mark.asyncio
async def test_verify_cfdi_special_xml_empty_estado():
    """Test verify_cfdi with the specific case where both conditions for special
    handling are met."""
    # XML with direct attributes on ConsultaResult
    SPECIAL_XML_FORMAT = """<?xml version="1.0" encoding="utf-8"?>
    <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
        <s:Body>
            <ConsultaResponse xmlns="http://tempuri.org/">
                <ConsultaResult Estado="Vigente"
                               EsCancelable="Cancelable sin aceptación"
                               EstatusCancelacion="No cancelado"
                               CodigoEstatus="S - Comprobante obtenido satisfactoriamente."/>
            </ConsultaResponse>
        </s:Body>
    </s:Envelope>
    """

    # Mock the requests.post response
    with patch("requests.post") as mock_post:
        # Configure the mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = SPECIAL_XML_FORMAT.encode("utf-8")
        mock_post.return_value = mock_response

        # Create a specific mock for ET.fromstring that will force our desired code path
        def mock_fromstring(content):
            mock_root = MagicMock()

            # 1. Make findall return empty list (first condition)
            mock_root.findall.return_value = []

            # 2. Create a mock ConsultaResult with attributes
            mock_consulta_result = MagicMock()
            mock_consulta_result.attrib = {
                "Estado": "Vigente",
                "EsCancelable": "Cancelable sin aceptación",
                "EstatusCancelacion": "No cancelado",
                "CodigoEstatus": "S - Comprobante obtenido satisfactoriamente.",
            }

            # 3. Setup find to return our mock ConsultaResult
            def mock_find(path, namespaces=None):
                if path == ".//ConsultaResult":
                    return mock_consulta_result
                return None  # Return None for other paths

            mock_root.find = mock_find

            return mock_root

        # Patch ET.fromstring
        with patch("xml.etree.ElementTree.fromstring", mock_fromstring):
            # Call the function
            result = await verify_cfdi(
                uuid="6128396f-c09b-4ec6-8699-43c5f7e3b230",
                emisor_rfc="CDZ050722LA9",
                receptor_rfc="XIN06112344A",
                total="12000.00",
            )

            # Assert results
            assert result["estado"] == "Vigente"
            assert result["es_cancelable"] == "Cancelable sin aceptación"
            assert result["estatus_cancelacion"] == "No cancelado"
            assert (
                result["codigo_estatus"]
                == "S - Comprobante obtenido satisfactoriamente."
            )
            assert mock_post.called
