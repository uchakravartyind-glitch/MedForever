# 🏥 MedForever
### Universal Multimodal Medical Bridge — From Messy Human Intent to Life-Saving Clinical Actions

[![Google for Developers](https://img.shields.io/badge/Google%20for%20Developers-Build%20with%20AI-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://developers.google.com/)
[![Gemini 2.5 Flash](https://img.shields.io/badge/Powered%20By-Gemini%202.5%20Flash-8E75B2?style=for-the-badge&logo=google-gemini&logoColor=white)](https://deepmind.google/technologies/gemini/)
[![FHIR R4 Compliant](https://img.shields.io/badge/Healthcare-FHIR%20R4%20Standard-007EC6?style=for-the-badge)](https://hl7.org/fhir/)
[![HL7 v2.5 Interop](https://img.shields.io/badge/Clinical-HL7%20v2.5%20Standard-10B981?style=for-the-badge)](https://www.hl7.org/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI%20%7C%20Python-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)

---

## 🌟 The Challenge & Problem Statement

> **Challenge (PromptWars x Techverse):** *Build a Gemini-powered App that solves societal benefit by acting as a universal bridge between human intent and complex systems.*
> 
> **Description:** *Participants must create a functional interface that takes unstructured, messy, real-world inputs that can be anything (voice, traffic, weather, news, photos or messy stack of medical history) and instantly converts them into structured, verified, and life-saving actions.*

In healthcare, **unstructured and chaotic data causes thousands of preventable fatal errors every year**:
- **Illegible Doctor Scripts & Drug Confusions:** Over 7,000+ patients die annually in hospitals due to illegible handwriting, look-alike drug brand confusions, and missing dosage units.
- **Frantic Emergency Voice Calls:** Panicked bystanders calling 911/EMS struggle to articulate structured medical histories, active medications, and acute symptoms in the golden hour.
- **Care Transition & Discharge Polypharmacy:** Elderly patients discharged from hospital are given multi-page discharge packets where brand names change, resulting in fatal duplicate therapies and drug-drug clashes (e.g. *Warfarin + high-dose NSAIDs*).

**MedForever** acts as the **universal multimodal bridge** powered by **Google Gemini 2.5 / 1.5 Flash**. It ingests messy doctor handwriting, live panic voice notes, crumpled medicine packaging, and convoluted discharge stacks — instantly converting them into **verified pharmacological safety checks, 1-tap EMS dispatch telemetry, FHIR R4 interoperable records, HL7 v2.5 messages, and 24-hour daily visual medication schedules**.

---

## 🏗️ System Architecture

```
                                  UNSTRUCTURED MESSY INPUTS
        ┌─────────────────────────┬─────────────────────────┬─────────────────────────┐
        │  Messy Handwritten Rx  │   Frantic Voice Memos   │  Hospital Discharge     │
        │  & Pill Bottle Photos   │   (Panic Spoken Audio)  │  & Allergy History      │
        └────────────┬────────────┴────────────┬────────────┴────────────┬────────────┘
                     │                         │                         │
                     ▼                         ▼                         ▼
        ┌─────────────────────────────────────────────────────────────────────────────┐
        │                    GEMINI 2.5 FLASH MULTIMODAL CORE                         │
        │  • Handwriting & Rx OCR          • Voice Emotion & Speech-to-Text           │
        │  • Brand -> Generic Extraction    • Clinical Triage Scoring (ESI Level 1-5) │
        │  • Cross-Allergy Conflict Engine • SOAP Note Clinical Synthesis             │
        └──────────────────────────────────────┬──────────────────────────────────────┘
                                               │
                     ┌─────────────────────────┼─────────────────────────┐
                     ▼                         ▼                         ▼
        ┌─────────────────────────┬─────────────────────────┬─────────────────────────┐
        │  Lethal Drug Clash      │  1-Tap EMS Dispatch     │  FHIR R4 & HL7 v2.5     │
        │  Interception Matrix    │  & Emergency QR Card    │  Interoperable Records  │
        └─────────────────────────┴─────────────────────────┴─────────────────────────┘
                                   STRUCTURED LIFE-SAVING ACTIONS
```

---

## ✨ Key Features & Innovation Highlights

### 1. 📷 Universal Multimodal Ingestion Hub
- **Live Camera Scanner with Reticle:** In-browser viewfinder to scan medicine strips, pill bottles, or handwritten doctor notes.
- **Microphone Audio Voice Memo:** Real-time speech recording with live waveform frequency visualizer for frantic bystander emergency memos.
- **Unstructured History & Allergy Stack:** Freeform text parser for chronic conditions, past surgeries, and known drug allergies.

### 2. 🛡️ Pharmacological Safety & Contraindication Matrix
- **Lethal Interaction Interceptor:** 30+ validated high-hazard drug-drug interaction pairs (e.g. *Warfarin + Ibuprofen* bleeding hazard, *Metformin + Contrast* lactic acidosis, *Lisinopril + Spironolactone* hyperkalemia).
- **Cross-Allergy Guard:** Intercepts cross-sensitivities (e.g. Penicillin allergy vs Amoxicillin / Novamox).
- **Automated Clinical Substitutes:** Auto-recommends safe, non-interacting therapeutic alternatives.

### 3. 🚨 Emergency Severity Index (ESI) & 1-Tap EMS SOS
- **Emergency Triage Scoring ($0-100$):** Classifies cases into RED (Immediate Resuscitation), AMBER (Urgent), and GREEN (Stable).
- **1-Tap EMS Dispatch Payload:** Formats instant 911 / EMS telemetry with patient GPS, active medications, allergy warnings, and SOAP clinical notes.

### 4. ⏰ 24-Hour Chrono-Dosing & Pill Appearance Catalog
- **Chrono-Dosing Schedule:** Breaks daily prescriptions into Morning (08:00), Afternoon (14:00), Evening (18:00), and Night (22:00) with interactive adherence tracking.
- **Physical Pill Appearance:** Visual traits (shape, color, imprint) to help patients verify pills.
- **Generic Bioequivalent Savings:** FDA/WHO AB-rated generic bioequivalent matcher showing 70-90% cost savings.

### 5. 🏥 FHIR R4 & HL7 v2.5 Clinical Interoperability
- **FHIR R4 Bundle JSON:** Standard `Patient`, `Encounter`, `Condition`, `MedicationRequest`, `AllergyIntolerance`, and `Observation` resources.
- **HL7 v2.5 Pipe-Delimited Messages:** Standard `MSH`, `PID`, `PV1`, `AL1`, `ORC`, and `RXO` order strings.

### 6. 📄 Printable Clinical Discharge PDF & Offline Emergency QR Card
- **1-Click Discharge Summary:** Generates printable hospital clinical summary with physician verification signature lines.
- **Offline Paramedic QR Card:** Scannable emergency profile for first responders without internet access.

---

## 🎯 1-Click Evaluation Scenarios

| Scenario | Category | Key Life-Saving Action |
| :--- | :--- | :--- |
| **1. Fatal Drug Clash** | Geriatric Polypharmacy | Intercepts lethal Warfarin + high-dose Ibuprofen combination before dispensing; replaces with safe Acetaminophen. |
| **2. Frantic Voice Memo** | Acute STEMI Cardiac Triage | Bystander voice transcribed in real-time; classifies ESI Level 1 RED, initiates emergency Aspirin chewing protocol, dispatches EMS. |
| **3. Messy Doctor Script** | Pediatric Rx OCR & Dosing | Deciphers illegible handwriting for 6yo child (20kg); validates weight-based Amoxicillin suspension dosage and warns against Aspirin. |
| **4. Discharge Stack Clash** | Hospital Care Transition | Reconciles 6 conflicting discharge meds; eliminates accidental duplicate Metformin and nephrotoxic dual RAAS blockade. |

---

## 🚀 Quickstart Guide

### Prerequisites
- Python 3.10+ (Python 3.13 supported)
- Standard web browser (Chrome, Edge, Firefox, Safari)

### Installation & Launch

1. **Clone the repository:**
   ```bash
   git clone https://github.com/uchakravartyind-glitch/MedForever.git
   cd MedForever
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **(Optional) Configure Gemini API Key:**
   Copy `.env.example` to `.env` and insert your Gemini API Key:
   ```bash
   cp .env.example .env
   ```
   *(Note: You can also enter the API key directly in the web UI header, or use the pre-loaded clinical scenarios without an API key!)*

4. **Launch MedForever:**
   ```bash
   python run.py
   ```
   *The server starts on `http://127.0.0.1:8000` and automatically opens in your default browser.*

5. **Run Automated Test Suite:**
   ```bash
   pytest -v tests/test_api.py
   ```

---

## 📂 Project Structure

```
MedForever/
├── backend/
│   ├── __init__.py
│   ├── config.py             # Environment configuration & runtime API key manager
│   ├── demo_data.py          # Curated realistic messy medical scenarios
│   ├── drug_safety.py        # Pharmacological safety & contraindication rules engine
│   ├── emergency_router.py   # Nearby 24/7 pharmacies & Level-1 trauma centers router
│   ├── environmental_service.py # Environmental risk & weather stress analyzer
│   ├── fhir_service.py       # FHIR R4 Bundle & HL7 v2.5 message generator
│   ├── gemini_engine.py      # Gemini 2.5 Flash multimodal intelligence engine
│   ├── models.py             # Strongly-typed Pydantic schemas
│   └── pdf_service.py        # Printable clinical summary & discharge PDF generator
├── static/
│   └── js/
│       └── app.js            # Reactive dashboard & Web Audio / Live Camera / QR logic
├── templates/
│   └── index.html            # High-fidelity Tailwind CSS responsive dashboard
├── tests/
│   └── test_api.py           # Automated end-to-end integration test suite
├── .env.example              # Sample environment file
├── requirements.txt          # Python dependencies
├── run.py                    # One-click launcher script
├── main.py                   # FastAPI server & REST endpoints
└── README.md                 # Project documentation
```

---

## 👥 Hackathon Submission Details

- **Event:** Google for Developers | H2S | PromptWars x Techverse (Build with AI)
- **Repository:** [https://github.com/uchakravartyind-glitch/MedForever](https://github.com/uchakravartyind-glitch/MedForever)
- **Branch:** `main` (Strict single-branch compliance)
- **Track:** Gemini-Powered Universal Bridge for Societal Benefit