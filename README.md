# 🏥 MedForever
### Universal Multimodal Medical Bridge — From Messy Human Intent to Life-Saving Clinical Actions

[![Google for Developers](https://img.shields.io/badge/Google%20for%20Developers-Build%20with%20AI-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://developers.google.com/)
[![Gemini 2.5 Flash](https://img.shields.io/badge/Powered%20By-Gemini%202.5%20Flash-8E75B2?style=for-the-badge&logo=google-gemini&logoColor=white)](https://deepmind.google/technologies/gemini/)
[![FHIR R4 & HL7 v2.5](https://img.shields.io/badge/Healthcare-FHIR%20R4%20%7C%20HL7%20v2.5-007EC6?style=for-the-badge)](https://hl7.org/fhir/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI%20%7C%20Python-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)

---

## 🌟 Overview

**MedForever** is a Gemini-powered clinical intelligence bridge designed for the **Google for Developers PromptWars x Techverse (Build with AI)** hackathon. 

It takes **messy, unstructured real-world medical data** (illegible handwritten doctor scripts, frantic emergency voice recordings, crumpled pill packaging, complex hospital discharge summaries) and instantly converts them into **verified, life-saving clinical actions, FHIR R4 / HL7 records, drug contraindication alerts, and 24-hour visual medication schedules**.

---

## 🎯 How It Solves the Challenge

```
┌─────────────────────────────────┐       ┌─────────────────────────────────┐       ┌─────────────────────────────────┐
│     Unstructured Messy Inputs   │       │   Gemini 2.5 Intelligence Core  │       │    Verified Life-Saving Action  │
│ • Handwritten Prescriptions/OCR │ ────► │ • Handwriting & Voice Parser    │ ────► │ • Lethal Drug Clash Interceptor │
│ • Panic Bystander Voice Memos   │       │ • ESI Clinical Triage (0-100)   │       │ • 1-Tap EMS SOS Telemetry       │
│ • Multi-Condition History Stack │       │ • SOAP Note Documentation       │       │ • FHIR R4 & HL7 v2 EHR Records  │
│ • Real-Time Environmental Feeds │       │ • Cross-Allergy Sensitivity Guard│       │ • 24h Chrono-Dosing & QR Card   │
└─────────────────────────────────┘       └─────────────────────────────────┘       └─────────────────────────────────┘
```

---

## ✨ Key Features

- **📷 In-Browser Camera Scanner & OCR:** Captures and deciphers messy handwriting, blurred pill strips, and multi-page lab reports.
- **🎙️ Live Voice Memo Triage:** Transcribes panicked emergency audio with live waveform visualizer to classify Emergency Severity Index (ESI Level 1–5).
- **🛡️ 30+ Drug Contraindication Matrix:** Detects fatal drug-drug clashes (e.g. *Warfarin + Ibuprofen* bleeding hazard) and automatically suggests safe clinical alternatives.
- **🏥 Healthcare Standards Interoperability:** Generates both **HL7 FHIR Release 4 JSON Bundles** and **HL7 v2.5 pipe-delimited messages** ready for hospital EHRs (Epic, Cerner).
- **⏰ 24-Hour Chrono-Dosing & Adherence Tracker:** Interactive daily dosage schedule with pill visual identifiers (shape, color, imprint) and generic cost savings calculator.
- **🚨 1-Tap Emergency SOS & Offline Paramedic QR Card:** Instant 911 dispatch telemetry and scannable offline emergency card for first responders.
- **📄 Printable Discharge PDF:** Generates official clinical summaries with physician signature blocks.

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