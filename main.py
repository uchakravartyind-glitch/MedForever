"""
MedForever - Gemini-Powered Universal Multimodal Medical Bridge
Main FastAPI Application Server v2.0
"""
import os
import json
import base64
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from backend.config import get_api_key, set_runtime_api_key, has_valid_api_key, APP_PORT, APP_HOST
from backend.gemini_engine import analyze_multimodal_input
from backend.fhir_service import generate_fhir_bundle, generate_hl7_v2_message
from backend.demo_data import list_demo_scenarios, get_demo_scenario
from backend.pdf_service import generate_printable_report_html
from backend.pill_catalog import enrich_medication_pill_info
from backend.environmental_service import analyze_environmental_risks
from backend.emergency_router import get_nearby_emergency_resources

# Directories
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

STATIC_DIR.mkdir(exist_ok=True)
TEMPLATES_DIR.mkdir(exist_ok=True)

app = FastAPI(
    title="MedForever - Gemini Medical Bridge",
    description="Universal multimodal bridge from messy real-world inputs to structured, verified, life-saving clinical actions.",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Pydantic Schemas
class AnalyzeRequest(BaseModel):
    image_data: Optional[str] = None
    audio_data: Optional[str] = None
    text_notes: Optional[str] = None
    patient_history: Optional[str] = None
    patient_allergies: Optional[str] = None
    target_language: str = "en"

class ApiKeyRequest(BaseModel):
    api_key: str

class InteropRequest(BaseModel):
    analysis_data: Dict[str, Any]


@app.get("/", response_class=HTMLResponse)
async def serve_index(request: Request):
    """Serve the MedForever dashboard."""
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"has_api_key": has_valid_api_key()}
    )


@app.get("/api/scenarios")
async def get_scenarios():
    """List available demo scenarios."""
    return {"scenarios": list_demo_scenarios()}


@app.get("/api/scenarios/{scenario_id}")
async def get_scenario_by_id(scenario_id: str):
    """Retrieve full enriched scenario data."""
    raw_scenario = get_demo_scenario(scenario_id)
    
    scenario = json.loads(json.dumps(raw_scenario))
    enriched_meds = [enrich_medication_pill_info(m) for m in scenario.get("medications", [])]
    scenario["medications"] = enriched_meds
    
    conditions = scenario.get("patient", {}).get("pre_existing_conditions", [])
    scenario["environmental_context"] = analyze_environmental_risks(conditions)
    scenario["emergency_facilities"] = get_nearby_emergency_resources(scenario.get("triage", {}).get("level", "GREEN"))

    fhir_bundle = generate_fhir_bundle(scenario)
    hl7_message = generate_hl7_v2_message(scenario)

    return {
        "scenario": scenario,
        "fhir_bundle": fhir_bundle,
        "hl7_message": hl7_message
    }


@app.post("/api/analyze")
async def analyze_input(
    payload: Optional[AnalyzeRequest] = None,
    image_file: Optional[UploadFile] = File(None),
    audio_file: Optional[UploadFile] = File(None),
    text_notes: Optional[str] = Form(None),
    patient_history: Optional[str] = Form(None),
    patient_allergies: Optional[str] = Form(None),
    target_language: str = Form("en")
):
    """
    Multimodal analysis endpoint supporting JSON payload or Multipart Form uploads.
    """
    image_b64 = None
    audio_b64 = None
    notes = text_notes
    history = patient_history
    allergies = patient_allergies
    lang = target_language

    if payload:
        image_b64 = payload.image_data
        audio_b64 = payload.audio_data
        notes = payload.text_notes or notes
        history = payload.patient_history or history
        allergies = payload.patient_allergies or allergies
        lang = payload.target_language or lang

    if image_file:
        img_bytes = await image_file.read()
        image_b64 = f"data:{image_file.content_type};base64,{base64.b64encode(img_bytes).decode('utf-8')}"
        
    if audio_file:
        aud_bytes = await audio_file.read()
        audio_b64 = f"data:{audio_file.content_type};base64,{base64.b64encode(aud_bytes).decode('utf-8')}"

    result = analyze_multimodal_input(
        image_data=image_b64,
        audio_data=audio_b64,
        text_notes=notes,
        patient_history=history,
        patient_allergies=allergies,
        target_language=lang
    )

    fhir_bundle = generate_fhir_bundle(result)
    hl7_message = generate_hl7_v2_message(result)

    return {
        "analysis": result,
        "fhir_bundle": fhir_bundle,
        "hl7_message": hl7_message
    }


@app.post("/api/fhir")
async def export_fhir(req: InteropRequest):
    """Generate standard FHIR R4 Bundle from clinical analysis."""
    bundle = generate_fhir_bundle(req.analysis_data)
    return {"fhir_bundle": bundle}


@app.post("/api/hl7")
async def export_hl7(req: InteropRequest):
    """Generate standard HL7 v2.5 pipe-delimited message."""
    hl7_msg = generate_hl7_v2_message(req.analysis_data)
    return {"hl7_message": hl7_msg}


@app.post("/api/report/html", response_class=HTMLResponse)
async def get_report_html(req: InteropRequest):
    """Generate printable / PDF-ready clinical summary HTML."""
    html_content = generate_printable_report_html(req.analysis_data)
    return HTMLResponse(content=html_content)


@app.get("/api/key/status")
async def check_key_status():
    """Check whether Gemini API key is configured."""
    key = get_api_key()
    return {
        "configured": has_valid_api_key(),
        "masked_key": f"{key[:6]}...{key[-4:]}" if len(key) > 10 else None
    }


@app.post("/api/key")
async def set_key(req: ApiKeyRequest):
    """Set or update Gemini API key at runtime."""
    set_runtime_api_key(req.api_key)
    return {
        "success": True,
        "configured": has_valid_api_key()
    }


if __name__ == "__main__":
    import uvicorn
    print(f"[*] Starting MedForever server at http://{APP_HOST}:{APP_PORT}")
    uvicorn.run("main:app", host=APP_HOST, port=APP_PORT, reload=True)
