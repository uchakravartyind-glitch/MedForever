"""
Healthcare Interoperability Service (FHIR R4 & HL7 v2.5)
Generates HL7 FHIR Release 4 JSON Bundles and HL7 v2.5 pipe-delimited messages
for hospital EHR systems, EMS dispatch, and health exchanges.
"""
import uuid
from datetime import datetime
from typing import Dict, Any, List

def generate_fhir_bundle(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generates a valid FHIR R4 Bundle containing Patient, Encounter/Triage,
    Condition, AllergyIntolerance, and MedicationRequest resources.
    """
    bundle_id = str(uuid.uuid4())
    now_iso = datetime.utcnow().isoformat() + "Z"
    
    patient_data = data.get("patient", {})
    patient_name = patient_data.get("name", "Unknown Patient")
    patient_id = f"pat-{uuid.uuid4().hex[:8]}"
    
    entries = []

    # 1. Patient Resource
    patient_resource = {
        "fullUrl": f"urn:uuid:{patient_id}",
        "resource": {
            "resourceType": "Patient",
            "id": patient_id,
            "active": True,
            "name": [{
                "use": "official",
                "text": patient_name,
                "family": patient_name.split()[-1] if len(patient_name.split()) > 1 else patient_name,
                "given": patient_name.split()[:-1] if len(patient_name.split()) > 1 else [patient_name]
            }],
            "gender": patient_data.get("gender", "unknown").lower(),
            "birthDate": patient_data.get("birth_date", "1980-01-01") if patient_data.get("age") is None else None
        }
    }
    entries.append(patient_resource)

    # 2. Encounter / Triage Resource
    triage = data.get("triage", {})
    encounter_id = f"enc-{uuid.uuid4().hex[:8]}"
    encounter_resource = {
        "fullUrl": f"urn:uuid:{encounter_id}",
        "resource": {
            "resourceType": "Encounter",
            "id": encounter_id,
            "status": "in-progress",
            "class": {
                "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                "code": "EMER",
                "display": "Emergency" if triage.get("level") in ["RED", "AMBER"] else "AMB"
            },
            "priority": {
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/v3-ActPriority",
                    "code": "EM" if triage.get("level") == "RED" else "UR",
                    "display": f"Triage Priority: {triage.get('level', 'GREEN')} (ESI Score: {triage.get('score', 50)})"
                }]
            },
            "subject": {"reference": f"urn:uuid:{patient_id}", "display": patient_name},
            "period": {"start": now_iso}
        }
    }
    entries.append(encounter_resource)

    # 3. AllergyIntolerance Resources
    allergies = patient_data.get("allergies", [])
    for allergy in allergies:
        if allergy and allergy.lower() not in ["none", "nil", "none documented"]:
            allergy_id = f"alg-{uuid.uuid4().hex[:8]}"
            allergy_res = {
                "fullUrl": f"urn:uuid:{allergy_id}",
                "resource": {
                    "resourceType": "AllergyIntolerance",
                    "id": allergy_id,
                    "clinicalStatus": {
                        "coding": [{
                            "system": "http://terminology.hl7.org/CodeSystem/allergyintolerance-clinical",
                            "code": "active"
                        }]
                    },
                    "verificationStatus": {
                        "coding": [{
                            "system": "http://terminology.hl7.org/CodeSystem/allergyintolerance-verification",
                            "code": "confirmed"
                        }]
                    },
                    "category": ["medication"],
                    "criticality": "high",
                    "code": {"text": allergy},
                    "patient": {"reference": f"urn:uuid:{patient_id}", "display": patient_name}
                }
            }
            entries.append(allergy_res)

    # 4. Condition Resources (Symptoms / Assessments)
    conditions = list(patient_data.get("pre_existing_conditions", []) or [])
    soap = triage.get("soap_note", {})
    if soap.get("assessment") and soap.get("assessment") not in conditions:
        conditions.append(soap.get("assessment"))
    
    for cond in conditions:
        if cond:
            cond_id = f"cond-{uuid.uuid4().hex[:8]}"
            cond_res = {
                "fullUrl": f"urn:uuid:{cond_id}",
                "resource": {
                    "resourceType": "Condition",
                    "id": cond_id,
                    "clinicalStatus": {
                        "coding": [{
                            "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                            "code": "active"
                        }]
                    },
                    "code": {"text": cond},
                    "subject": {"reference": f"urn:uuid:{patient_id}", "display": patient_name},
                    "recordedDate": now_iso
                }
            }
            entries.append(cond_res)

    # 5. MedicationRequest Resources
    medications = data.get("medications", [])
    for med in medications:
        med_id = f"medreq-{uuid.uuid4().hex[:8]}"
        med_name = med.get("brand_name") or med.get("generic_name") or med.get("name", "Unknown Medication")
        med_res = {
            "fullUrl": f"urn:uuid:{med_id}",
            "resource": {
                "resourceType": "MedicationRequest",
                "id": med_id,
                "status": "active",
                "intent": "order",
                "medicationCodeableConcept": {
                    "text": med_name,
                    "coding": [{
                        "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
                        "display": med.get("generic_name", med_name)
                    }]
                },
                "subject": {"reference": f"urn:uuid:{patient_id}", "display": patient_name},
                "dosageInstruction": [{
                    "text": f"{med.get('dosage', '')} - {med.get('frequency', '')} ({med.get('instructions', '')})",
                    "route": {"text": med.get("route", "Oral")}
                }],
                "authoredOn": now_iso
            }
        }
        entries.append(med_res)

    bundle = {
        "resourceType": "Bundle",
        "id": bundle_id,
        "type": "document",
        "timestamp": now_iso,
        "meta": {
            "profile": ["http://hl7.org/fhir/StructureDefinition/document"],
            "generator": "MedForever Gemini Multimodal Bridge v2.0"
        },
        "total": len(entries),
        "entry": entries
    }

    return bundle

def generate_hl7_v2_message(data: Dict[str, Any]) -> str:
    """
    Generates standard HL7 v2.5 pipe-delimited message string.
    """
    msg_ctrl_id = uuid.uuid4().hex[:10].upper()
    ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    patient = data.get("patient", {})
    p_name = patient.get("name", "PATIENT^UNKNOWN").replace(" ", "^")
    p_gender = patient.get("gender", "U")[0].upper() if patient.get("gender") else "U"
    triage = data.get("triage", {})

    lines = [
        f"MSH|^~\\&|MEDFOREVER|EMR_GATEWAY|RECEIVING_HOSPITAL|ED_TRIAGE|{ts}||ORM^O01|{msg_ctrl_id}|P|2.5",
        f"PID|1||PAT{uuid.uuid4().hex[:6].upper()}||{p_name}|||{p_gender}|||||||||||",
        f"PV1|1|E|ED^TRIAGE^01|||||||||||||||{triage.get('level', 'GREEN')}|{msg_ctrl_id}|||||||||||||||||||||||||{ts}",
    ]

    for idx, alg in enumerate(patient.get("allergies", []), start=1):
        if alg:
            lines.append(f"AL1|{idx}|DA|{alg}^^RXNORM|MO|Severe Allergy Risk")

    for idx, med in enumerate(data.get("medications", []), start=1):
        m_name = med.get("generic_name") or med.get("brand_name") or "DRUG"
        lines.append(f"ORC|NW|ORD{idx:04d}|||||1^{med.get('frequency', 'DAILY')}^^^^|{ts}")
        lines.append(f"RXO|{m_name}^^RXNORM|{med.get('dosage', '1 TAB')}||||||{med.get('instructions', '')}")

    return "\r\n".join(lines)
