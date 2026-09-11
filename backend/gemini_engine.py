"""
Gemini Multimodal Intelligence Engine v2.0
Handles multimodal inputs (Images, Audio, Text) using Google Gemini 2.5/1.5 Flash
and extracts structured clinical entities, SOAP notes, drug safety warnings,
pill appearance identifiers, environmental risks, and emergency care routes.
"""
import os
import json
import base64
import requests
from typing import Dict, Any, Optional, List
from .config import get_api_key, DEFAULT_GEMINI_MODEL
from .drug_safety import check_drug_safety
from .demo_data import get_demo_scenario
from .pill_catalog import enrich_medication_pill_info
from .environmental_service import analyze_environmental_risks
from .emergency_router import get_nearby_emergency_resources
from .clinical_intelligence import analyze_patient_clinical_input

SYSTEM_CLINICAL_PROMPT = """You are MedForever - an advanced, life-saving Clinical AI & Multimodal Medical Bridge developed for Google for Developers Build with AI.

Your mission is to take messy, unstructured, real-world inputs (patient symptoms, prescription notes, vitals, voice dictation, discharge summaries) and transform them into structured, verified, life-saving clinical intelligence matching Mayo Clinic format.

Strictly output your response as valid, parseable JSON matching the following schema. Do NOT include markdown code fences (```json ... ```) or any extraneous conversational text. Output pure JSON only.

{
  "triage": {
    "level": "RED" | "AMBER" | "GREEN",
    "score": 0-100 (integer, 100=most critical emergency),
    "title": "Short punchy clinical status title",
    "summary": "2-3 sentences explaining immediate clinical findings and urgency.",
    "soap_note": {
      "subjective": "Patient complaints, symptoms, history in clinical terms",
      "objective": "Deciphered medications, observed physical/audio indicators, vitals if any",
      "assessment": "Clinical diagnosis, contraindication risks, severity assessment",
      "plan": "Numbered actionable clinical steps, triage actions, monitoring plan"
    }
  },
  "patient": {
    "name": "Patient Name if found, else 'Patient'",
    "age": integer or null,
    "gender": "Male" | "Female" | "Unknown",
    "allergies": ["Allergy 1", "Allergy 2"],
    "pre_existing_conditions": ["Condition 1", "Condition 2"]
  },
  "condition_profile": {
    "name": "Clinical Disease / Condition Name",
    "icd10": "ICD-10 Code",
    "category": "Medical Category",
    "overview": "Mayo Clinic style clinical overview",
    "symptoms": ["Key symptom 1", "Key symptom 2"],
    "causes": ["Etiological factor 1", "Etiological factor 2"],
    "diagnostic_tests": ["Test 1", "Test 2"],
    "red_flags": ["Emergency danger sign 1", "Emergency danger sign 2"],
    "home_care": "Guidance and precautions"
  },
  "medications": [
    {
      "brand_name": "Brand name or Trade name",
      "generic_name": "Active pharmacological ingredient",
      "dosage": "Strength (e.g. 500 mg, 5 mL)",
      "frequency": "Frequency (e.g. Twice daily with meals, BID, Once daily at bedtime)",
      "route": "Oral" | "Inhalation" | "Topical" | "IV" | "Sublingual",
      "duration": "Duration (e.g. 7 days, Ongoing)",
      "timing_slot": "morning" | "afternoon" | "evening" | "night",
      "purpose": "What this treats in plain medical terms",
      "instructions": "Crucial administration directions",
      "dietary_warnings": "Food, alcohol, or timing interactions",
      "is_high_risk": boolean
    }
  ],
  "safety_analysis": {
    "status": "CRITICAL_HAZARD" | "MODERATE_WARNING" | "CLEARED",
    "score": 0-100,
    "color": "red" | "amber" | "emerald",
    "badge": "Short badge text",
    "interactions": [
      {
        "drug_a": "Drug A",
        "drug_b": "Drug B",
        "severity": "CRITICAL" | "MODERATE" | "LOW",
        "title": "Interaction title",
        "mechanism": "Why they interact biologically",
        "recommendation": "Life-saving alternative or doctor action"
      }
    ],
    "allergy_conflicts": [
      {
        "severity": "CRITICAL",
        "allergy_detected": "Allergy",
        "conflicting_medication": "Drug name",
        "title": "Direct allergy conflict",
        "mechanism": "Cross-sensitivity details",
        "recommendation": "Immediate withholding and alternative"
      }
    ]
  },
  "patient_friendly_guide": {
    "plain_summary": "Simple, reassuring 2-sentence summary in 5th-grade reading level explaining what was prescribed and why.",
    "schedule_breakdown": {
      "morning": "Morning pill instructions with exact time & food tips",
      "afternoon": "Afternoon instructions",
      "evening": "Evening instructions",
      "night": "Night instructions"
    },
    "red_flag_symptoms": [
      "Danger symptom 1 that warrants immediate ER visit",
      "Danger symptom 2"
    ],
    "lifestyle_precautions": "Hydration, food precautions, and activity advice."
  }
}
"""

def analyze_multimodal_input(
    image_data: Optional[str] = None,
    audio_data: Optional[str] = None,
    text_notes: Optional[str] = None,
    patient_history: Optional[str] = None,
    patient_allergies: Optional[str] = None,
    target_language: str = "en",
    patient_photo: Optional[str] = None,
    vitals: Optional[Dict[str, Any]] = None,
    location_lat: Optional[float] = None,
    location_lon: Optional[float] = None,
    country_code: Optional[str] = None,
    city: Optional[str] = None
) -> Dict[str, Any]:
    """
    Analyzes multimodal medical inputs with Gemini and clinical post-processing.
    """
    api_key = get_api_key()
    result = None
    
    if api_key and len(api_key) > 10:
        try:
            result = _call_gemini_api(
                api_key=api_key,
                image_data=image_data,
                audio_data=audio_data,
                text_notes=text_notes,
                patient_history=patient_history,
                patient_allergies=patient_allergies,
                target_language=target_language,
                country_code=country_code,
                city=city
            )
        except Exception as e:
            print(f"[Gemini Exception] {e} - Using clinical intelligence pipeline")

    if not result:
        result = _smart_clinical_fallback(
            image_data=image_data,
            audio_data=audio_data,
            text_notes=text_notes,
            patient_history=patient_history,
            patient_allergies=patient_allergies,
            vitals=vitals,
            target_language=target_language
        )

    # Attach patient photo and vitals if provided
    if "patient" not in result:
        result["patient"] = {}
    if patient_photo:
        result["patient"]["photo_base64"] = patient_photo
    if vitals:
        result["patient"]["vitals"] = vitals
        result["vitals"] = vitals

    # 1. Deterministic Pharmacological Safety Validation
    allergies = result.get("patient", {}).get("allergies", [])
    if patient_allergies:
        for a in patient_allergies.split(","):
            if a.strip() and a.strip() not in allergies:
                allergies.append(a.strip())
        result["patient"]["allergies"] = allergies

    safety_check = check_drug_safety(result.get("medications", []), allergies)
    
    if "safety_analysis" not in result:
        result["safety_analysis"] = {"interactions": [], "allergy_conflicts": []}

    if safety_check["interactions"]:
        existing_titles = [x.get("title") for x in result.get("safety_analysis", {}).get("interactions", [])]
        for item in safety_check["interactions"]:
            if item["title"] not in existing_titles:
                result["safety_analysis"]["interactions"].append(item)

    if safety_check["allergy_conflicts"]:
        existing_alg = [x.get("title") for x in result.get("safety_analysis", {}).get("allergy_conflicts", [])]
        for item in safety_check["allergy_conflicts"]:
            if item["title"] not in existing_alg:
                result["safety_analysis"]["allergy_conflicts"].append(item)

    if safety_check["status"] == "CRITICAL_HAZARD":
        result["safety_analysis"]["status"] = "CRITICAL_HAZARD"
        result["safety_analysis"]["color"] = "red"
        result["safety_analysis"]["badge"] = "Lethal Interaction Intercepted"
        result["triage"]["level"] = "RED"

    # 2. Enrich with Pill Visual Recognition & Generic Bioequivalents
    enriched_meds = []
    for med in result.get("medications", []):
        enriched_meds.append(enrich_medication_pill_info(med))
    result["medications"] = enriched_meds

    # 4. Enrich with Emergency Facilities & Verified 24/7 Pharmacies
    triage_level = result.get("triage", {}).get("level", "GREEN")
    result["nearby_emergency_resources"] = get_nearby_emergency_resources(
        triage_level=triage_level,
        lat=location_lat,
        lon=location_lon,
        country_code=country_code,
        city=city
    )

    # 5. Enrich with Mayo Clinic Condition Profile & ICD-10 Workup
    if "condition_profile" not in result or not result["condition_profile"]:
        from backend.clinical_intelligence import match_symptoms_to_condition
        combined_text = f"{text_notes or ''} {patient_history or ''} {result.get('triage', {}).get('title', '')}"
        cond, _ = match_symptoms_to_condition(combined_text)
        result["condition_profile"] = {
            "name": cond["condition_name"],
            "icd10": cond["icd10"],
            "category": cond["category"],
            "overview": cond["mayo_overview"],
            "symptoms": cond["mayo_symptoms"],
            "causes": cond["mayo_causes"],
            "diagnostic_tests": cond["diagnostic_tests"],
            "red_flags": cond["red_flags"],
            "home_care": cond["home_care"]
        }

    return result

def _call_gemini_api(
    api_key: str,
    image_data: Optional[str] = None,
    audio_data: Optional[str] = None,
    text_notes: Optional[str] = None,
    patient_history: Optional[str] = None,
    patient_allergies: Optional[str] = None,
    target_language: str = "en",
    country_code: Optional[str] = None,
    city: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """Calls Gemini Flash via REST API with fallback models and JSON extraction."""
    models_to_try = [DEFAULT_GEMINI_MODEL, "gemini-1.5-flash", "gemini-2.0-flash"]
    
    parts = []
    user_prompt = "Analyze these real patient medical inputs and generate structured clinical intelligence.\n"
    if city or country_code:
        user_prompt += f"\n--- Patient Location Context: {city or ''} {country_code or ''} ---\n"
    if text_notes:
        user_prompt += f"\n--- Patient Symptoms, Prescriptions & Case Notes ---\n{text_notes}\n"
    if patient_history:
        user_prompt += f"\n--- Patient Medical History / Pre-existing Conditions ---\n{patient_history}\n"
    if patient_allergies:
        user_prompt += f"\n--- Known Patient Allergies ---\n{patient_allergies}\n"
    if target_language and target_language != "en":
        user_prompt += f"\n--- Translation Note ---\nTranslate the 'patient_friendly_guide' and explanations into language code: '{target_language}'.\n"

    parts.append({"text": user_prompt})

    if image_data:
        mime_type = "image/jpeg"
        b64_content = image_data
        if "data:" in image_data and ";base64," in image_data:
            header, b64_content = image_data.split(";base64,")
            mime_type = header.replace("data:", "")
        parts.append({"inline_data": {"mime_type": mime_type, "data": b64_content}})

    if audio_data:
        mime_type = "audio/mp3"
        b64_content = audio_data
        if "data:" in audio_data and ";base64," in audio_data:
            header, b64_content = audio_data.split(";base64,")
            mime_type = header.replace("data:", "")
        parts.append({"inline_data": {"mime_type": mime_type, "data": b64_content}})

    payload = {
        "contents": [{"parts": parts}],
        "systemInstruction": {"parts": [{"text": SYSTEM_CLINICAL_PROMPT}]},
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.2
        }
    }

    headers = {"Content-Type": "application/json"}

    for model_name in models_to_try:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
            response = requests.post(url, json=payload, headers=headers, timeout=25)
            if response.status_code == 200:
                data = response.json()
                candidates = data.get("candidates", [])
                if candidates:
                    content_text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                    clean_json = content_text.strip()
                    if clean_json.startswith("```json"):
                        clean_json = clean_json[7:]
                    if clean_json.startswith("```"):
                        clean_json = clean_json[3:]
                    if clean_json.endswith("```"):
                        clean_json = clean_json[:-3]
                    clean_json = clean_json.strip()
                    return json.loads(clean_json)
        except Exception as err:
            print(f"Model {model_name} attempt: {err}")
            continue

    return None

def _smart_clinical_fallback(
    image_data: Optional[str] = None,
    audio_data: Optional[str] = None,
    text_notes: Optional[str] = None,
    patient_history: Optional[str] = None,
    patient_allergies: Optional[str] = None,
    vitals: Optional[Dict[str, Any]] = None,
    target_language: str = "en"
) -> Dict[str, Any]:
    """
    Comprehensive Diagnostic Reasoning Engine:
    Parses the user's actual symptoms, identifies diseases/conditions,
    calculates clinical urgency, extracts medications, and structures Mayo Clinic profiles.
    """
    return analyze_patient_clinical_input(
        text_notes=text_notes,
        patient_history=patient_history,
        patient_allergies=patient_allergies,
        vitals=vitals,
        target_language=target_language
    )
