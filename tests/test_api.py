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
    assert "MedForever" in response.text
    assert "Discharge Summary" in response.text

def test_emergency_lookup_endpoint():
    """Verify GPS-aware emergency directory lookup for various countries."""
    # Test India lookup
    res_in = client.post("/api/emergency/lookup", json={
        "triage_level": "RED",
        "lat": 28.6139,
        "lon": 77.2090,
        "country_code": "IN",
        "city": "New Delhi"
    })
    assert res_in.status_code == 200
    data_in = res_in.json()
    assert data_in["helplines"]["emergency"] == "112"
    assert data_in["helplines"]["ambulance"] == "108"
    assert len(data_in["hospitals"]) > 0

    # Test US lookup
    res_us = client.post("/api/emergency/lookup", json={
        "triage_level": "AMBER",
        "country_code": "US",
        "city": "Boston"
    })
    assert res_us.status_code == 200
    data_us = res_us.json()
    assert data_us["helplines"]["emergency"] == "911"

def test_analyze_real_user_data():
    """Verify analyze endpoint handles custom real patient inputs."""
    payload = {
        "text_notes": "Patient: Jane Doe, Age: 45. Prescribed: Warfarin 5mg, Ibuprofen 800mg.",
        "patient_allergies": "Sulfa drugs",
        "patient_history": "Hypertension",
        "target_language": "en",
        "vitals": {
            "blood_pressure": "135/85 mmHg",
            "heart_rate": "80 bpm",
            "oxygen_saturation": "99%",
            "temperature": "98.4°F"
        },
        "country_code": "US",
        "city": "Chicago"
    }
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "analysis" in data
    assert "fhir_bundle" in data
    assert "hl7_message" in data
    assert data["analysis"]["triage"]["level"] in ["RED", "AMBER", "GREEN"]
    assert "safety_analysis" in data["analysis"]

