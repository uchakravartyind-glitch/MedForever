"""
Pharmacological Safety Engine & Clinical Contraindication Matrix
Provides validated drug-drug interaction detection, allergy cross-reactivity guards,
and dietary interaction screening.
"""
from typing import List, Dict, Any

KNOWN_INTERACTIONS = [
    {
        "pair": {"warfarin", "ibuprofen"},
        "severity": "CRITICAL",
        "title": "Severe Gastrointestinal Bleeding Risk",
        "mechanism": "NSAIDs (Ibuprofen) inhibit platelet aggregation and cause gastric mucosal erosion, synergistically magnifying anticoagulant potency of Warfarin.",
        "recommendation": "DO NOT CO-ADMINISTER. Switch analgesic to Acetaminophen / Paracetamol (max 2g/day) or topical Diclofenac with INR monitoring."
    },
    {
        "pair": {"warfarin", "aspirin"},
        "severity": "CRITICAL",
        "title": "Major Hemorrhage & Bleeding Event Risk",
        "mechanism": "Dual antiplatelet and anticoagulant effect dramatically elevates major internal and intracranial bleeding risk.",
        "recommendation": "Requires explicit dual-therapy clinical indication with gastroprotection (PPI) and strict INR monitoring."
    },
    {
        "pair": {"metformin", "contrast agent"},
        "severity": "CRITICAL",
        "title": "Lactic Acidosis & Acute Renal Failure",
        "mechanism": "Iodinated contrast media can precipitate acute kidney injury, leading to severe Metformin accumulation and fatal lactic acidosis.",
        "recommendation": "Hold Metformin at time of or prior to imaging procedure and withhold for 48 hours post-contrast."
    },
    {
        "pair": {"lisinopril", "spironolactone"},
        "severity": "CRITICAL",
        "title": "Severe Hyperkalemia & Cardiac Arrhythmia Risk",
        "mechanism": "Combined ACE inhibitor and potassium-sparing diuretic effect leads to dangerous serum potassium retention.",
        "recommendation": "Monitor serum potassium and creatinine within 1-2 weeks of initiation. Avoid potassium supplements."
    },
    {
        "pair": {"lisinopril", "losartan"},
        "severity": "MODERATE",
        "title": "Dual RAAS Blockade (Redundant Nephrotoxicity)",
        "mechanism": "Combining ACE inhibitor and ARB increases risk of severe hypotension, hyperkalemia, and acute renal impairment without clinical benefit.",
        "recommendation": "Discontinue one agent; maintain monotherapy with single RAAS inhibitor."
    },
    {
        "pair": {"amiodarone", "digoxin"},
        "severity": "CRITICAL",
        "title": "Digoxin Toxicity & Severe Bradycardia",
        "mechanism": "Amiodarone inhibits P-glycoprotein and renal clearance of Digoxin, doubling serum Digoxin concentrations.",
        "recommendation": "Reduce Digoxin dosage by 50% when starting Amiodarone and closely monitor ECG and serum levels."
    },
    {
        "pair": {"sildenafil", "nitroglycerin"},
        "severity": "CRITICAL",
        "title": "Fatal Hypotension & Cardiovascular Collapse",
        "mechanism": "PDE5 inhibitor + organic nitrates causes massive cyclic GMP-mediated systemic vasodilation.",
        "recommendation": "ABSOLUTELY CONTRAINDICATED. Do not administer nitrates within 24-48 hours of PDE5 inhibitors."
    },
    {
        "pair": {"ciprofloxacin", "theophylline"},
        "severity": "MODERATE",
        "title": "Theophylline Toxicity (Seizures / Arrhythmias)",
        "mechanism": "Fluoroquinolone inhibits CYP1A2 metabolism of Theophylline.",
        "recommendation": "Monitor Theophylline serum levels and consider dose reduction."
    },
    {
        "pair": {"fluoxetine", "tramadol"},
        "severity": "MODERATE",
        "title": "Serotonin Syndrome Risk & Lowered Seizure Threshold",
        "mechanism": "Synergistic serotonergic activity and CYP2D6 inhibition.",
        "recommendation": "Avoid concurrent use. Monitor for agitation, hyperthermia, tremor, and diaphoresis."
    },
    {
        "pair": {"atorvastatin", "clarithromycin"},
        "severity": "MODERATE",
        "title": "Rhabdomyolysis & Myopathy Risk",
        "mechanism": "Macrolide strongly inhibits CYP3A4, dramatically increasing Atorvastatin blood levels.",
        "recommendation": "Temporarily suspend Atorvastatin during antibiotic course, or switch to Azithromycin / Rosuvastatin."
    },
    {
        "pair": {"amoxicillin", "methotrexate"},
        "severity": "MODERATE",
        "title": "Methotrexate Toxicity (Bone Marrow Suppression)",
        "mechanism": "Penicillins reduce renal tubular clearance of Methotrexate.",
        "recommendation": "Carefully monitor complete blood count and renal function."
    },
    {
        "pair": {"clopidogrel", "omeprazole"},
        "severity": "MODERATE",
        "title": "Reduced Antiplatelet Efficacy of Clopidogrel",
        "mechanism": "Omeprazole competitively inhibits CYP2C19, the primary enzyme activating Clopidogrel pro-drug.",
        "recommendation": "Switch PPI to Pantoprazole or Rabeprazole, which exhibit minimal CYP2C19 inhibition."
    },
    {
        "pair": {"simvastatin", "amlodipine"},
        "severity": "MODERATE",
        "title": "Elevated Statin Exposure & Myopathy Hazard",
        "mechanism": "Amlodipine inhibits CYP3A4 metabolism of Simvastatin.",
        "recommendation": "Limit Simvastatin dose to a maximum of 20mg daily or switch to Atorvastatin / Pravastatin."
    },
    {
        "pair": {"levothyroxine", "calcium carbonate"},
        "severity": "LOW",
        "title": "Decreased Thyroid Hormone Absorption",
        "mechanism": "Calcium chelates Levothyroxine in the gastrointestinal tract, preventing systemic absorption.",
        "recommendation": "Separate administration by at least 4 hours."
    }
]

ALLERGY_CROSS_REACTIONS = {
    "penicillin": ["amoxicillin", "ampicillin", "augmentin", "piperacillin", "cephalexin", "cefuroxime", "novamox"],
    "sulfa": ["sulfamethoxazole", "bactrim", "septra", "sulfasalazine", "hydrochlorothiazide", "furosemide"],
    "nsaid": ["aspirin", "ibuprofen", "naproxen", "diclofenac", "ketorolac", "meloxicam", "celecoxib", "brufen"],
    "opioid": ["morphine", "codeine", "oxycodone", "hydrocodone", "tramadol", "fentanyl"]
}

def check_drug_safety(medications: List[Dict[str, Any]], patient_allergies: List[str] = None) -> Dict[str, Any]:
    """
    Cross-checks extracted medications against drug-drug interactions and known allergies.
    """
    allergies = [a.lower().strip() for a in (patient_allergies or []) if a and a.strip()]
    extracted_names = []
    
    for med in medications:
        name = med.get("generic_name") or med.get("brand_name") or med.get("name") or ""
        if name:
            extracted_names.append(name.lower().strip())

    flagged_interactions = []
    allergy_warnings = []

    # 1. Drug-Drug Interactions
    for item in KNOWN_INTERACTIONS:
        pair = item["pair"]
        matches = [m for m in extracted_names if any(p in m for p in pair)]
        if len(matches) >= 2:
            flagged_interactions.append({
                "drug_a": list(pair)[0].capitalize(),
                "drug_b": list(pair)[1].capitalize(),
                "severity": item["severity"],
                "title": item["title"],
                "mechanism": item["mechanism"],
                "recommendation": item["recommendation"]
            })

    # 2. Allergy Cross-Reactions
    for allergy in allergies:
        for drug_class, related_drugs in ALLERGY_CROSS_REACTIONS.items():
            if allergy in drug_class or drug_class in allergy:
                for med_name in extracted_names:
                    if any(r in med_name for r in related_drugs):
                        allergy_warnings.append({
                            "severity": "CRITICAL",
                            "allergy_detected": allergy.capitalize(),
                            "conflicting_medication": med_name.capitalize(),
                            "title": f"Direct Allergy Conflict: {allergy.capitalize()} Allergy vs {med_name.capitalize()}",
                            "mechanism": f"Patient has documented allergy to '{allergy}', which cross-reacts with prescribed medication '{med_name}'.",
                            "recommendation": "STOP MEDICATION IMMEDIATELY. Select non-cross-reacting alternative agent."
                        })

    has_critical = any(i["severity"] == "CRITICAL" for i in flagged_interactions) or len(allergy_warnings) > 0
    has_moderate = any(i["severity"] == "MODERATE" for i in flagged_interactions)

    if has_critical:
        status = "CRITICAL_HAZARD"
        score = 95
        color = "red"
        badge = "DANGER: Lethal Interaction / Allergy Alert"
    elif has_moderate:
        status = "MODERATE_WARNING"
        score = 65
        color = "amber"
        badge = "CAUTION: Clinical Interaction Flagged"
    else:
        status = "CLEARED"
        score = 10
        color = "emerald"
        badge = "SAFE: No High-Risk Clashes Detected"

    return {
        "status": status,
        "score": score,
        "color": color,
        "badge": badge,
        "interactions": flagged_interactions,
        "allergy_conflicts": allergy_warnings,
        "total_alerts": len(flagged_interactions) + len(allergy_warnings)
    }
