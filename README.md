# 🏥 MedForever
### Universal Multimodal Medical Bridge — From Messy Human Intent to Life-Saving Clinical Actions

[![Google for Developers](https://img.shields.io/badge/Google%20for%20Developers-Build%20with%20AI-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://developers.google.com/)
[![Gemini 2.5 Flash](https://img.shields.io/badge/Powered%20By-Gemini%202.5%20Flash-8E75B2?style=for-the-badge&logo=google-gemini&logoColor=white)](https://deepmind.google/technologies/gemini/)
[![FHIR R4 & HL7 v2.5](https://img.shields.io/badge/Healthcare-FHIR%20R4%20%7C%20HL7%20v2.5-007EC6?style=for-the-badge)](https://hl7.org/fhir/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI%20%7C%20Python-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)

---

## 📌 1. Chosen Vertical

**Vertical:** **Healthcare, Emergency Clinical Triage & Medication Safety Bridge**

In real-world healthcare, over 7,000+ deaths occur annually due to illegible doctor handwriting, medication brand confusions, and uncommunicated drug allergies during emergency calls. **MedForever** serves as a universal multimodal bridge connecting chaotic human intent (frantic voice memos, crumpled prescriptions, multi-page discharge summaries) directly into life-saving clinical systems.

---

## 🧠 2. Approach and Logic

MedForever uses a **Hybrid Multimodal Intelligence Architecture**:

```
┌─────────────────────────────────┐       ┌─────────────────────────────────┐       ┌─────────────────────────────────┐
│     Unstructured Messy Inputs   │       │   Gemini 2.5 Intelligence Core  │       │    Verified Life-Saving Action  │
│ • Handwritten Prescriptions/OCR │ ────► │ • Handwriting & Voice Parser    │ ────► │ • Lethal Drug Clash Interceptor │
│ • Panic Bystander Voice Memos   │       │ • ESI Clinical Triage (0-100)   │       │ • 1-Tap EMS SOS Telemetry       │
│ • Multi-Condition History Stack │       │ • SOAP Note Documentation       │       │ • FHIR R4 & HL7 v2 EHR Records  │
│ • Real-Time Environmental Feeds │       │ • Cross-Allergy Sensitivity Guard│       │ • 24h Chrono-Dosing & QR Card   │
└─────────────────────────────────┘       └─────────────────────────────────┘       └─────────────────────────────────┘
```

1. **Multimodal Ingestion:** Accepts real-world inputs via live camera scanner, microphone audio recording, or freeform text notes.
2. **Gemini 2.5 Flash Intelligence Core:** Performs handwriting OCR, parses frantic voice tone and emergency symptoms, and extracts structured clinical entities (brand name, generic formula, strength, frequency).
3. **Deterministic Safety Guardrail:** All extracted medications and patient allergies are cross-referenced against a rule-based pharmacological knowledge base (30+ high-hazard interactions and cross-allergies) to eliminate LLM hallucinations for life-critical decisions.
4. **Clinical Interoperability Output:** Generates standardized healthcare data structures (FHIR R4 Bundle JSON and HL7 v2.5 pipe-delimited messages) along with plain-language patient guides.

---

## ⚙️ 3. How the Solution Works

- **📷 In-Browser Camera Scanner & OCR:** Live viewfinder with targeting reticle crops and digitizes physical doctor slips and pill packaging.
- **🎙️ Emergency Voice Memo Triage:** Captures panicked speech, calculates an Emergency Severity Index (ESI Level 1–5), and structures SOAP clinical notes.
- **🛡️ Drug-Drug & Allergy Contraindication Matrix:** Detects lethal combinations (e.g., *Warfarin + Ibuprofen* bleeding hazard) and automatically suggests safe substitutes (e.g., *Acetaminophen*).
- **🏥 FHIR R4 & HL7 v2.5 Interoperability:** Exports standard `Patient`, `Encounter`, `Condition`, `MedicationRequest`, and `AllergyIntolerance` records.
- **⏰ 24-Hour Chrono-Dosing & Adherence Checklist:** Organizes daily doses into 4 intuitive time slots (Morning, Afternoon, Evening, Night) with pill visual identifiers (shape, color, imprint) and generic cost savings.
- **🚨 1-Tap EMS SOS & Offline Paramedic QR Card:** Pre-formats 911 dispatch telemetry and generates scannable offline emergency medical wallet cards.
- **📄 Printable Discharge PDF Summary:** Generates official clinical summaries with physician signature verification lines.

---

## 🔍 4. Assumptions Made

1. **Safety-First Hybrid Validation:** LLM responses are cross-verified with a deterministic clinical database to ensure zero false negatives on fatal contraindications.
2. **Standard Reference Values:** Pediatric dosing calculations assume standard weight-based formulas (e.g., 45mg/kg/day for Amoxicillin).
3. **Emergency Interoperability Standards:** Hospital EHR integrations follow HL7 FHIR Release 4 and HL7 v2.5 messaging standards.
4. **Geolocation & Facility Data:** Nearby Level 1 trauma centers and 24/7 pharmacies use simulated coordinates and verified inventory for hackathon demonstration.

---

## 🎯 1-Click Evaluation Scenarios

| Scenario | Category | Key Life-Saving Action |
| :--- | :--- | :--- |
| **1. Fatal Drug Clash** | Geriatric Polypharmacy | Intercepts lethal Warfarin + high-dose Ibuprofen combination; replaces with safe Acetaminophen. |
| **2. Frantic Voice Memo** | Acute STEMI Cardiac Triage | Transcribes frantic bystander speech; activates ESI Level 1 RED and emergency Aspirin chewing protocol. |
| **3. Messy Doctor Script** | Pediatric Rx OCR & Dosing | Deciphers illegible handwriting for 6yo child; validates weight-based Amoxicillin suspension dosing. |
| **4. Discharge Stack Clash** | Hospital Care Transition | Reconciles conflicting discharge meds; eliminates accidental duplicate Metformin and dual RAAS blockade. |

---

## 🚀 Quick Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Launch MedForever:**
   ```bash
   python run.py
   ```
   *(Server boots on `http://127.0.0.1:8000` and opens in your default browser).*

3. **Run tests:**
   ```bash
   pytest -v tests/test_api.py
   ```

---

## 📂 Project Structure

```
MedForever/
├── backend/
│   ├── config.py             # Runtime config & API key manager
│   ├── demo_data.py          # Pre-loaded clinical test scenarios
│   ├── drug_safety.py        # 30+ drug contraindication rules engine
│   ├── emergency_router.py   # 24/7 pharmacies & Level 1 trauma locator
│   ├── environmental_service.py # AQI, pollen & weather risk analyzer
│   ├── fhir_service.py       # FHIR R4 Bundle & HL7 v2.5 generator
│   ├── gemini_engine.py      # Gemini 2.5 Flash multimodal core
│   ├── models.py             # Strongly-typed Pydantic schemas
│   └── pdf_service.py        # Printable clinical summary HTML/PDF generator
├── static/js/app.js          # Reactive dashboard & Web Audio / Camera logic
├── templates/index.html      # Responsive Tailwind CSS dashboard
├── tests/test_api.py         # Automated integration test suite
├── requirements.txt          # Python dependencies
├── run.py                    # One-click launcher script
├── main.py                   # FastAPI server & REST endpoints
└── README.md                 # Project documentation
```

---

## 👥 Hackathon Submission

- **Repository:** [https://github.com/uchakravartyind-glitch/MedForever](https://github.com/uchakravartyind-glitch/MedForever)
- **Branch:** `main` (Strict single-branch compliance)
- **Track:** Google for Developers | PromptWars x Techverse (Build with AI)