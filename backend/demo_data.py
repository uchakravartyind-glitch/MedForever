"""
Curated realistic messy medical scenarios for 1-click evaluation & demonstration.
"""
from typing import Dict, Any

DEMO_SCENARIOS: Dict[str, Dict[str, Any]] = {
    "fatal_drug_clash": {
        "id": "fatal_drug_clash",
        "title": "Elderly Polypharmacy & Fatal Drug Interaction",
        "category": "Prescription Clash / Drug Safety",
        "description": "Crumpled prescription slip for a 74-year-old cardiac patient on blood thinners, newly prescribed high-dose NSAIDs for joint pain.",
        "input_type": "Messy Handwritten Prescription + Patient History Stack",
        "raw_text_preview": "Rx: Warfarin 5mg daily, Plavix (Clopidogrel) 75mg daily. Added today: Brufen (Ibuprofen) 800mg TID for knee osteoarthrosis.",
        "triage": {
            "level": "RED",
            "score": 96,
            "title": "CRITICAL: Life-Threatening Hemorrhagic Drug Conflict",
            "summary": "Co-administration of high-dose Ibuprofen (NSAID) with Warfarin and Clopidogrel dramatically elevates the risk of fatal gastrointestinal bleeding and systemic hemorrhage.",
            "soap_note": {
                "subjective": "74yo male with history of Atrial Fibrillation, prior DVT, and worsening bilateral knee osteoarthritis. Complains of chronic joint stiffness.",
                "objective": "Current active medications: Warfarin 5mg daily (INR target 2.0-3.0), Clopidogrel 75mg daily. Newly presented prescription: Ibuprofen 800mg TID.",
                "assessment": "Severe Drug-Drug Contraindication. Concurrent NSAID + Dual Antithrombotic therapy confers a 4-to-7-fold increase in major upper GI bleed risk.",
                "plan": "1. Immediately withhold Ibuprofen. 2. Substitute with Acetaminophen (max 2g/day) or topical NSAID (Diclofenac gel). 3. Order urgent INR check. 4. Initiate PPI gastroprotection (Pantoprazole 40mg)."
            }
        },
        "patient": {
            "name": "Robert Vance",
            "age": 74,
            "gender": "Male",
            "allergies": ["Sulfa drugs"],
            "pre_existing_conditions": ["Atrial Fibrillation", "Deep Vein Thrombosis", "Knee Osteoarthritis"]
        },
        "medications": [
            {
                "brand_name": "Coumadin",
                "generic_name": "Warfarin Sodium",
                "dosage": "5 mg",
                "frequency": "Once daily at 6:00 PM",
                "route": "Oral",
                "duration": "Ongoing",
                "timing_slot": "night",
                "purpose": "Blood thinning & stroke prevention in Atrial Fibrillation",
                "instructions": "Take at the exact same time every evening. Maintain consistent Vitamin K diet.",
                "dietary_warnings": "Avoid cranberries, grapefruit, and alcohol. Keep dietary Vitamin K stable.",
                "is_high_risk": True
            },
            {
                "brand_name": "Plavix",
                "generic_name": "Clopidogrel",
                "dosage": "75 mg",
                "frequency": "Once daily with breakfast",
                "route": "Oral",
                "duration": "Ongoing",
                "timing_slot": "morning",
                "purpose": "Antiplatelet therapy to prevent arterial clot formation",
                "instructions": "Take with food to minimize gastric discomfort.",
                "dietary_warnings": "None significant.",
                "is_high_risk": True
            },
            {
                "brand_name": "Brufen (BLOCKED)",
                "generic_name": "Ibuprofen",
                "dosage": "800 mg",
                "frequency": "Three times daily (TID)",
                "route": "Oral",
                "duration": "PROHIBITED / BLOCKED",
                "timing_slot": "afternoon",
                "purpose": "Anti-inflammatory pain relief for knee osteoarthritis",
                "instructions": "DO NOT DISPENSE OR ADMINISTER. High fatal bleeding hazard.",
                "dietary_warnings": "Severe gastric mucosal irritant.",
                "is_high_risk": True
            },
            {
                "brand_name": "Tylenol (Recommended Substitute)",
                "generic_name": "Acetaminophen",
                "dosage": "500 mg",
                "frequency": "Every 6-8 hours PRN (Max 2,000 mg/day)",
                "route": "Oral",
                "duration": "As needed for joint pain",
                "timing_slot": "morning",
                "purpose": "Safe alternative analgesic with zero antiplatelet or gastric ulceration risk",
                "instructions": "Do not exceed 4 tablets per 24-hour period.",
                "dietary_warnings": "Avoid alcohol co-ingestion to protect liver function.",
                "is_high_risk": False
            }
        ],
        "safety_analysis": {
            "status": "CRITICAL_HAZARD",
            "score": 96,
            "color": "red",
            "badge": "Lethal Interaction Intercepted",
            "interactions": [
                {
                    "drug_a": "Warfarin",
                    "drug_b": "Ibuprofen",
                    "severity": "CRITICAL",
                    "title": "High-Risk Major GI Hemorrhage & Ulceration",
                    "mechanism": "Ibuprofen inhibits platelet COX-1 and causes gastric mucosal injury while Warfarin blocks clotting factor synthesis.",
                    "recommendation": "Intercepted before dispensing. Replace Ibuprofen with Acetaminophen 500mg or topical Diclofenac."
                }
            ],
            "allergy_conflicts": []
        },
        "patient_friendly_guide": {
            "plain_summary": "We stopped a dangerous painkiller combination. Taking Ibuprofen with your regular blood thinner (Warfarin) can cause severe internal stomach bleeding. We have switched your pain plan to safe Paracetamol and alerted your doctor.",
            "schedule_breakdown": {
                "morning": "8:00 AM: Plavix (Clopidogrel 75mg) with breakfast + Paracetamol 500mg (if knee hurts).",
                "afternoon": "2:00 PM: Paracetamol 500mg (only if joint pain persists).",
                "evening": "6:00 PM: Coumadin (Warfarin 5mg) with a glass of water.",
                "night": "10:00 PM: Rest and hydration."
            },
            "red_flag_symptoms": [
                "Unusual dark / tarry stools or vomiting blood",
                "Unexplained large purple bruising or nosebleeds lasting >10 minutes",
                "Sudden dizziness, severe weakness, or fainting"
            ],
            "lifestyle_precautions": "Keep your green leafy vegetables intake steady every week. Avoid rough contact sports or sharp blade shaving."
        }
    },

    "frantic_voice_triage": {
        "id": "frantic_voice_triage",
        "title": "Frantic Voice Triage (Acute STEMI Cardiac Event)",
        "category": "Emergency Voice Dispatch / Triage",
        "description": "Urgent voice audio note from a frantic bystander describing a family member with crushing chest pain and cold sweats.",
        "input_type": "Frantic Voice Audio Recording (Transcribed & Analyzed in Real-Time)",
        "raw_text_preview": "\"Help! My father is 58, he suddenly collapsed in his chair clutching his chest! He says it feels like an elephant sitting on his chest, pain radiating into his jaw and left shoulder, he is drenched in cold sweat and gasping!\"",
        "triage": {
            "level": "RED",
            "score": 98,
            "title": "EMERGENCY: Suspected Acute Myocardial Infarction (STEMI)",
            "summary": "Classified as ESI Level 1 (Immediate Resuscitation). Symptoms of substernal crushing chest pressure radiating to left arm/jaw with diaphoresis are classic hallmarks of Acute Coronary Syndrome.",
            "soap_note": {
                "subjective": "58yo male with acute onset 10/10 substernal chest pressure ('elephant on chest'), radiation to jaw and left arm, accompanied by profuse diaphoresis and dyspnea.",
                "objective": "Voice analysis shows severe acute respiratory distress and severe distress indicators. Bystander reports cold clammy skin.",
                "assessment": "Suspected Acute Coronary Syndrome / STEMI. Immediate emergency protocol activated.",
                "plan": "1. 1-Tap EMS/911 Dispatch with GPS coordinates. 2. Verify no aspirin allergy or recent active bleeding. 3. Instruct bystander to administer 325mg non-enteric chewable Aspirin immediately. 4. Prepare for AED / bystander CPR if consciousness is lost."
            }
        },
        "patient": {
            "name": "David Miller",
            "age": 58,
            "gender": "Male",
            "allergies": ["Penicillin"],
            "pre_existing_conditions": ["Hypertension", "Hyperlipidemia", "Ex-Smoker"]
        },
        "medications": [
            {
                "brand_name": "Emergency Aspirin Protocol",
                "generic_name": "Aspirin (Chewable)",
                "dosage": "325 mg (or 4x 81mg baby aspirin)",
                "frequency": "IMMEDIATELY CHEWED (Single Emergency Dose)",
                "route": "Oral / Chew",
                "duration": "Immediate STAT",
                "timing_slot": "morning",
                "purpose": "Rapid platelet aggregation inhibition to halt coronary thrombus progression",
                "instructions": "CHEW thoroughly before swallowing for rapid buccal and gastric absorption.",
                "dietary_warnings": "Take without food immediately.",
                "is_high_risk": False
            }
        ],
        "safety_analysis": {
            "status": "CLEARED",
            "score": 15,
            "color": "emerald",
            "badge": "Aspirin Admin Safe - No NSAID/Aspirin Allergy Documented",
            "interactions": [],
            "allergy_conflicts": []
        },
        "patient_friendly_guide": {
            "plain_summary": "AMBULANCE DISPATCHED. Keep the patient sitting upright in a comfortable position. Have them chew 325mg aspirin right now. Loosen tight clothing around the neck. Do not leave them alone.",
            "schedule_breakdown": {
                "morning": "NOW: Chew 325mg Aspirin. Keep airway open.",
                "afternoon": "Hospital arrival & Cath Lab coronary angiography.",
                "evening": "Inpatient CCU monitoring.",
                "night": "Continuous telemetry."
            },
            "red_flag_symptoms": [
                "Loss of consciousness or unresponsiveness -> START CHEST COMPRESSIONS IMMEDIATELY",
                "Cessation of normal breathing",
                "Cyanosis (bluish lips or fingertips)"
            ],
            "lifestyle_precautions": "Keep front door unlocked for incoming paramedics. Do not allow patient to walk or exert themselves."
        }
    },

    "pediatric_handwriting": {
        "id": "pediatric_handwriting",
        "title": "Messy Handwritten Pediatric Prescription OCR",
        "category": "Handwriting OCR & Dosing Validation",
        "description": "Crumpled, barely legible pediatric clinic slip for a 6-year-old child (20 kg) with acute otitis media & bronchospasm.",
        "input_type": "Messy Handwritten Doctor Rx Image / OCR",
        "raw_text_preview": "Rx: Syr. Novamox (Amox) 250mg/5ml - 5ml TDS x 7d. Syr. Ascoril LS - 2.5ml BD. Syr. Calpol 250 - 4ml SOS.",
        "triage": {
            "level": "AMBER",
            "score": 48,
            "title": "URGENT: Pediatric Respiratory & Ear Infection Dosing Plan",
            "summary": "Deciphered handwritten script: Amoxicillin antibiotic course + Levosalbutamol bronchodilator + Paracetamol antipyretic. Doses verified against pediatric 20kg bodyweight standards.",
            "soap_note": {
                "subjective": "6yo female (20 kg) presenting with 3 days of otalgia (ear tugging), persistent nocturnal cough, and fever (101.8 F).",
                "objective": "Deciphered Rx: Amoxicillin suspension 250mg/5ml (dosage: 45mg/kg/day standard), Levosalbutamol expectorant, Paracetamol syrup 250mg/5ml.",
                "assessment": "Acute Otitis Media with reactive airway cough. Dosages match international pediatric safety guidelines.",
                "plan": "1. Complete full 7-day antibiotic course even if fever resolves. 2. Paracetamol for fever >100.4 F every 6h SOS. 3. Ensure adequate hydration."
            }
        },
        "patient": {
            "name": "Emma Watson",
            "age": 6,
            "gender": "Female",
            "allergies": ["None documented"],
            "pre_existing_conditions": ["Mild seasonal wheezing"]
        },
        "medications": [
            {
                "brand_name": "Novamox Suspension",
                "generic_name": "Amoxicillin Trihydrate (250mg/5ml)",
                "dosage": "5 mL (250 mg)",
                "frequency": "Three times daily (every 8 hours) after food",
                "route": "Oral Syrup",
                "duration": "7 full days",
                "timing_slot": "morning",
                "purpose": "Bacterial infection clearance in middle ear & respiratory tract",
                "instructions": "Shake bottle well before each dose. Finish all 7 days even if child feels better.",
                "dietary_warnings": "Can be taken with milk or food to avoid stomach upset.",
                "is_high_risk": False
            },
            {
                "brand_name": "Ascoril LS Junior",
                "generic_name": "Levosalbutamol + Ambroxol + Guaifenesin",
                "dosage": "2.5 mL",
                "frequency": "Twice daily (Morning & Evening)",
                "route": "Oral Syrup",
                "duration": "5 days",
                "timing_slot": "morning",
                "purpose": "Relieves chest congestion and opens constricted airways",
                "instructions": "Give with lukewarm water.",
                "dietary_warnings": "Avoid chilled drinks and ice cream.",
                "is_high_risk": False
            },
            {
                "brand_name": "Calpol 250 Pead",
                "generic_name": "Paracetamol / Acetaminophen (250mg/5ml)",
                "dosage": "4 mL (200 mg = 10-15 mg/kg)",
                "frequency": "Every 6 hours ONLY if fever > 100.4 F (SOS)",
                "route": "Oral Syrup",
                "duration": "As needed (SOS)",
                "timing_slot": "afternoon",
                "purpose": "Fever and pain relief",
                "instructions": "Use measuring syringe provided. Do not exceed 4 doses in 24 hours.",
                "dietary_warnings": "Never give Aspirin to children (risk of Reye's syndrome).",
                "is_high_risk": False
            }
        ],
        "safety_analysis": {
            "status": "CLEARED",
            "score": 12,
            "color": "emerald",
            "badge": "Pediatric Dosage Verified Safe for 20kg",
            "interactions": [],
            "allergy_conflicts": []
        },
        "patient_friendly_guide": {
            "plain_summary": "Here is Emma's simple schedule. The pink medicine (Antibiotic) MUST be finished for all 7 days. Give the cough syrup morning and night. Only give the fever syrup if her temperature goes above 100.4°F.",
            "schedule_breakdown": {
                "morning": "8:00 AM: 5ml Antibiotic (Novamox) + 2.5ml Cough Syrup (Ascoril LS) after breakfast.",
                "afternoon": "2:00 PM: 5ml Antibiotic (Novamox) after lunch.",
                "evening": "8:00 PM: 2.5ml Cough Syrup (Ascoril LS) after dinner.",
                "night": "10:00 PM: 5ml Antibiotic (Novamox) before bed. (Fever syrup only if hot)."
            },
            "red_flag_symptoms": [
                "Difficulty breathing, fast belly breathing, or flaring nostrils",
                "Persistent high fever > 103 F not responding to syrup",
                "Extreme lethargy or refusal to drink any liquids"
            ],
            "lifestyle_precautions": "Keep hydrated with warm soups and fluids. Use a cool-mist humidifier in bedroom."
        }
    },

    "discharge_stack_clash": {
        "id": "discharge_stack_clash",
        "title": "Messy Hospital Discharge Stack & Duplicate Therapy",
        "category": "EHR Discharge Reconciliation",
        "description": "Multi-page hospital discharge summary with contradictory brand name switches and accidental duplication of antihypertensives.",
        "input_type": "Messy Multi-Page Medical History Discharge Stack",
        "raw_text_preview": "Discharge meds: Glucophage 1000mg BD, Metformin XR 500mg daily, Lisinopril 20mg, Cozaar (Losartan) 50mg, Lipitor 40mg.",
        "triage": {
            "level": "AMBER",
            "score": 75,
            "title": "CAUTION: Duplicate Therapy & Dual RAAS Blockade Detected",
            "summary": "The discharge stack contains redundant therapies: 1) Metformin prescribed twice under different names (Glucophage + Metformin XR). 2) Lisinopril (ACEI) + Losartan (ARB) prescribed simultaneously (Dual RAAS blockade, high risk of acute kidney injury and hypotension).",
            "soap_note": {
                "subjective": "62yo female discharged post-cholecystectomy with pre-existing Type 2 Diabetes and Hypertension.",
                "objective": "Reconciliation identified overlapping prescriptions from inpatient vs outpatient records.",
                "assessment": "Accidental drug duplication during care transition. Glucophage + Metformin XR total dose exceeds max safe daily limit (2,500mg). Dual ACEI + ARB co-prescribing confers no benefit and elevates hyperkalemia/renal failure.",
                "plan": "1. Discontinue duplicate Metformin XR (retain Glucophage 1000mg BID). 2. Discontinue Losartan; maintain Lisinopril 20mg monotherapy. 3. Monitor eGFR and serum creatinine in 2 weeks."
            }
        },
        "patient": {
            "name": "Maria Rodriguez",
            "age": 62,
            "gender": "Female",
            "allergies": ["Shellfish", "Codeine"],
            "pre_existing_conditions": ["Type 2 Diabetes Mellitus", "Essential Hypertension", "Stage 2 CKD"]
        },
        "medications": [
            {
                "brand_name": "Glucophage",
                "generic_name": "Metformin HCl",
                "dosage": "1,000 mg",
                "frequency": "Twice daily with breakfast and dinner",
                "route": "Oral",
                "duration": "Ongoing",
                "timing_slot": "morning",
                "purpose": "Blood sugar regulation in Type 2 Diabetes",
                "instructions": "Take with meals to prevent gastrointestinal upset.",
                "dietary_warnings": "Limit alcohol consumption.",
                "is_high_risk": False
            },
            {
                "brand_name": "Prinivil",
                "generic_name": "Lisinopril",
                "dosage": "20 mg",
                "frequency": "Once daily in the morning",
                "route": "Oral",
                "duration": "Ongoing",
                "timing_slot": "morning",
                "purpose": "Blood pressure control and renal protection",
                "instructions": "Take consistently at the same time each morning.",
                "dietary_warnings": "Avoid high-potassium salt substitutes.",
                "is_high_risk": False
            },
            {
                "brand_name": "Lipitor",
                "generic_name": "Atorvastatin",
                "dosage": "40 mg",
                "frequency": "Once daily at bedtime",
                "route": "Oral",
                "duration": "Ongoing",
                "timing_slot": "night",
                "purpose": "Cholesterol reduction and cardiovascular risk reduction",
                "instructions": "Take at night before sleep.",
                "dietary_warnings": "Avoid large amounts of grapefruit juice.",
                "is_high_risk": False
            }
        ],
        "safety_analysis": {
            "status": "MODERATE_WARNING",
            "score": 75,
            "color": "amber",
            "badge": "Prescription Duplication Cleared & Optimized",
            "interactions": [
                {
                    "drug_a": "Lisinopril",
                    "drug_b": "Losartan",
                    "severity": "MODERATE",
                    "title": "Dual RAAS Blockade (Redundant & Nephrotoxic)",
                    "mechanism": "Combining ACE inhibitors and ARBs increases risk of severe hypotension, hyperkalemia, and acute renal impairment without additional clinical benefit.",
                    "recommendation": "Losartan successfully removed from active discharge profile. Maintained Lisinopril monotherapy."
                }
            ],
            "allergy_conflicts": []
        },
        "patient_friendly_guide": {
            "plain_summary": "We cleaned up your hospital discharge list to prevent medication mistakes. We removed double-prescribed diabetes pills and removed an extra blood pressure pill that was conflicting with your main one.",
            "schedule_breakdown": {
                "morning": "8:00 AM: Glucophage (Metformin 1000mg) + Lisinopril 20mg with breakfast.",
                "afternoon": "Hydration and regular meals.",
                "evening": "7:00 PM: Glucophage (Metformin 1000mg) with dinner.",
                "night": "10:00 PM: Lipitor (Atorvastatin 40mg) at bedtime."
            },
            "red_flag_symptoms": [
                "Persistent dizziness when standing up",
                "Severe nausea, vomiting, or muscle weakness",
                "Swelling in face, lips, or tongue (Lisinopril alert)"
            ],
            "lifestyle_precautions": "Avoid salt substitutes made with potassium. Keep a daily blood pressure and morning fasting glucose log."
        }
    }
}

def get_demo_scenario(scenario_id: str) -> Dict[str, Any]:
    """Retrieve demo scenario by ID or return default."""
    return DEMO_SCENARIOS.get(scenario_id, DEMO_SCENARIOS["fatal_drug_clash"])

def list_demo_scenarios():
    """Return catalog of available demo scenarios."""
    return [
        {
            "id": s["id"],
            "title": s["title"],
            "category": s["category"],
            "description": s["description"],
            "input_type": s["input_type"],
            "triage_level": s["triage"]["level"]
        }
        for s in DEMO_SCENARIOS.values()
    ]
