"""
Automated Integration & Clinical Verification Test Suite
Tests all endpoints, scenarios, drug interaction algorithms, and FHIR payloads.
"""
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_index_page():
    """Verify home dashboard renders successfully."""
    response = client.get("/")
    assert response.status_code == 200
    assert "MedForever" in response.text

def test_scenarios_catalog():
    """Verify all 4 evaluation scenarios are returned."""
    response = client.get("/api/scenarios")
    assert response.status_code == 200
    data = response.json()
    assert "scenarios" in data
    assert len(data["scenarios"]) == 4

def test_fatal_drug_clash_scenario():
    """Verify drug contraindication detection for Warfarin + Ibuprofen."""
    response = client.get("/api/scenarios/fatal_drug_clash")
    assert response.status_code == 200
    data = response.json()
    scenario = data["scenario"]
    assert scenario["triage"]["level"] == "RED"
    assert scenario["safety_analysis"]["status"] == "CRITICAL_HAZARD"
    assert "fhir_bundle" in data
    assert "hl7_message" in data

def test_frantic_voice_triage_scenario():
    """Verify emergency cardiac STEMI triage."""
    response = client.get("/api/scenarios/frantic_voice_triage")
    assert response.status_code == 200
    data = response.json()
    scenario = data["scenario"]
    assert scenario["triage"]["level"] == "RED"
    assert scenario["triage"]["score"] >= 90

def test_fhir_export_endpoint():
    """Verify FHIR R4 Bundle generation."""
    scenario_res = client.get("/api/scenarios/pediatric_handwriting")
    scenario_data = scenario_res.json()["scenario"]
    
    response = client.post("/api/fhir", json={"analysis_data": scenario_data})
    assert response.status_code == 200
    bundle = response.json()["fhir_bundle"]
    assert bundle["resourceType"] == "Bundle"
    assert len(bundle["entry"]) > 0

def test_hl7_export_endpoint():
    """Verify HL7 v2.5 pipe-delimited message generation."""
    scenario_res = client.get("/api/scenarios/discharge_stack_clash")
    scenario_data = scenario_res.json()["scenario"]
    
    response = client.post("/api/hl7", json={"analysis_data": scenario_data})
    assert response.status_code == 200
    hl7_msg = response.json()["hl7_message"]
    assert "MSH|^~\\&|MEDFOREVER" in hl7_msg

def test_printable_report_html():
    """Verify PDF / Printable HTML summary endpoint."""
    scenario_res = client.get("/api/scenarios/fatal_drug_clash")
    scenario_data = scenario_res.json()["scenario"]
    
    response = client.post("/api/report/html", json={"analysis_data": scenario_data})
    assert response.status_code == 200
    assert "MedForever Clinical Summary" in response.text
