"""
SAT Verification Service

Functions for verifying CFDIs with the SAT service and checking EFOS status.
"""

import logging
import xml.etree.ElementTree as ET
from typing import Any, Dict
from xml.dom import minidom

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def verify_cfdi(
    uuid: str, emisor_rfc: str, receptor_rfc: str, total: str
) -> Dict[str, Any]:
    """
    Verify a CFDI with the SAT verification service.

    Args:
        uuid: The UUID of the CFDI to verify
        emisor_rfc: The RFC of the emitter
        receptor_rfc: The RFC of the receiver
        total: The total amount of the CFDI

    Returns:
        A dictionary with the verification results

    Raises:
        Exception: If there is an error connecting to the SAT service
    """
    # Initialize result with default values
    result: Dict[str, Any] = {
        "estado": "",
        "es_cancelable": "",
        "estatus_cancelacion": "",
        "codigo_estatus": "",
        "validacion_efos": "",
        "raw_response": "",
        "efos_emisor": False,
        "efos_receptor": False,
    }

    # SAT verification endpoint
    url = "https://consultaqr.facturaelectronica.sat.gob.mx/ConsultaCFDIService.svc"

    # Headers for SOAP request
    headers = {
        "Content-Type": "text/xml;charset=UTF-8",
        "SOAPAction": "http://tempuri.org/IConsultaCFDIService/Consulta",
    }

    # SOAP envelope template
    soap_envelope = f"""
    <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tem="http://tempuri.org/">
       <soap:Header/>
       <soap:Body>
          <tem:Consulta>
             <tem:expresionImpresa>?re={emisor_rfc}&amp;rr={receptor_rfc}&amp;tt={total}&amp;id={uuid}</tem:expresionImpresa>
          </tem:Consulta>
       </soap:Body>
    </soap:Envelope>
    """

    # Send request to SAT service
    try:
        logger.info(
            f"Verifying CFDI: UUID={uuid}, Emisor={emisor_rfc}, Receptor={receptor_rfc}"
        )
        response = requests.post(
            url, headers=headers, data=soap_envelope.encode("utf-8"), timeout=15
        )

        if response.status_code == 200:
            # Save raw response
            result["raw_response"] = minidom.parseString(response.content).toprettyxml()

            try:
                # Parse XML response
                root = ET.fromstring(response.content)

                # Look for ConsultaResult element with its attributes
                namespaces = {
                    "s": "http://schemas.xmlsoap.org/soap/envelope/",
                    "temp": "http://tempuri.org/",
                    "a": "http://schemas.datacontract.org/2004/07/Sat.Cfdi.Negocio.ConsultaCfdi.Servicio",
                }

                # Find all elements that might contain our attributes
                for elem in root.findall(".//"):
                    # Look for all possible attribute names, handling namespaces
                    for attr_name in [
                        "CodigoEstatus",
                        "EsCancelable",
                        "Estado",
                        "EstatusCancelacion",
                        "ValidacionEFOS",
                    ]:
                        # Try both direct attributes and child elements
                        if attr_name in elem.attrib:
                            attr_key = attr_name.lower()
                            if attr_key == "codigoestatus":
                                result["codigo_estatus"] = elem.attrib[attr_name]
                            elif attr_key == "escancelable":
                                result["es_cancelable"] = elem.attrib[attr_name]
                            elif attr_key == "estado":
                                result["estado"] = elem.attrib[attr_name]
                            elif attr_key == "estatuscancelacion":
                                result["estatus_cancelacion"] = (
                                    elem.attrib[attr_name]
                                    if elem.attrib[attr_name]
                                    else "No disponible"
                                )
                            elif attr_key == "validacionefos":
                                result["validacion_efos"] = elem.attrib[attr_name]

                # If we didn't find attributes, look for child elements with those names
                if not result["estado"]:
                    for ns_prefix in ["a:", ""]:
                        estado_elem = root.find(f".//*{ns_prefix}Estado", namespaces)
                        if estado_elem is not None and estado_elem.text:
                            result["estado"] = estado_elem.text
                            break

                    for ns_prefix in ["a:", ""]:
                        cancelable_elem = root.find(
                            f".//*{ns_prefix}EsCancelable", namespaces
                        )
                        if cancelable_elem is not None and cancelable_elem.text:
                            result["es_cancelable"] = cancelable_elem.text
                            break

                    for ns_prefix in ["a:", ""]:
                        estatus_elem = root.find(
                            f".//*{ns_prefix}EstatusCancelacion", namespaces
                        )
                        if estatus_elem is not None:
                            result["estatus_cancelacion"] = (
                                estatus_elem.text
                                if estatus_elem.text
                                else "No disponible"
                            )
                            break

                    for ns_prefix in ["a:", ""]:
                        codigo_elem = root.find(
                            f".//*{ns_prefix}CodigoEstatus", namespaces
                        )
                        if codigo_elem is not None and codigo_elem.text:
                            result["codigo_estatus"] = codigo_elem.text
                            break

                    for ns_prefix in ["a:", ""]:
                        efos_elem = root.find(
                            f".//*{ns_prefix}ValidacionEFOS", namespaces
                        )
                        if efos_elem is not None and efos_elem.text:
                            result["validacion_efos"] = efos_elem.text
                            break

                # Special handling for our test XML format
                if not result["estado"]:
                    # Try with broader XPath expressions to find the elements
                    for path in [".//*Estado", ".//Estado", ".//a:Estado", ".//*[contains(local-name(),'Estado')]"]:
                        estado_elem = root.find(path, namespaces)
                        if estado_elem is not None and estado_elem.text:
                            result["estado"] = estado_elem.text
                            break
                            
                    for path in [".//*EsCancelable", ".//EsCancelable", ".//a:EsCancelable", ".//*[contains(local-name(),'EsCancelable')]"]:
                        cancelable_elem = root.find(path, namespaces)
                        if cancelable_elem is not None and cancelable_elem.text:
                            result["es_cancelable"] = cancelable_elem.text
                            break
                            
                    # Try a direct attribute lookup approach for ConsultaResult
                    consulta_result = root.find(".//ConsultaResult")
                    if consulta_result is not None:
                        if "Estado" in consulta_result.attrib:
                            result["estado"] = consulta_result.attrib["Estado"]
                        if "EsCancelable" in consulta_result.attrib:
                            result["es_cancelable"] = consulta_result.attrib[
                                "EsCancelable"
                            ]
                        if "EstatusCancelacion" in consulta_result.attrib:
                            result["estatus_cancelacion"] = (
                                consulta_result.attrib["EstatusCancelacion"]
                                if consulta_result.attrib["EstatusCancelacion"]
                                else "No disponible"
                            )
                        if "CodigoEstatus" in consulta_result.attrib:
                            result["codigo_estatus"] = consulta_result.attrib[
                                "CodigoEstatus"
                            ]

                logger.info(
                    f"CFDI verification successful: UUID={uuid}, Estado={result['estado']}"
                )
            except Exception as e:
                logger.error(f"Error parsing SAT response: {str(e)}")
                raise Exception(f"Error parsing SAT response: {str(e)}")
        else:
            logger.error(f"SAT service error: {response.status_code} - {response.text}")
            raise Exception(
                f"SAT service error: {response.status_code} - {response.text}"
            )

    except requests.RequestException as e:
        logger.error(f"Error connecting to SAT service: {str(e)}")
        raise Exception(f"Error connecting to SAT service: {str(e)}")

    return result
