"""
Pydantic Data Models for MedForever Clinical Bridge
Defines strongly-typed schemas for Patients, Medications, Triage,
Drug Interactions, SOAP notes, and Environmental Contexts.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class PatientProfile(BaseModel):
    name: str = Field(default="Anonymous Patient", description="Patient full name")
    age: Optional[int] = Field(default=None, description="Patient age in years")
    gender: Optional[str] = Field(default="Unknown", description="Male, Female, or Other")
    allergies: List[str] = Field(default_factory=list, description="Documented allergies")
    pre_existing_conditions: List[str] = Field(default_factory=list, description="Chronic medical conditions")

class PillVisualInfo(BaseModel):
    shape: str = Field(default="Round Tablet", description="Physical shape of the pill")
    color: str = Field(default="White", description="Color of pill or suspension")
    imprint: str = Field(default="Standard", description="Pharmaceutical debossing/imprint")

class GenericAlternative(BaseModel):
    available: bool = True
    generic_name: str = ""
    avg_savings_percent: int = 75
    bioequivalent_rating: str = "AB Rated"

class MedicationItem(BaseModel):
    brand_name: str = Field(..., description="Trade / Brand name")
    generic_name: str = Field(..., description="Active pharmacological ingredient")
    dosage: str = Field(..., description="Strength (e.g., 500mg, 5mL)")
    frequency: str = Field(..., description="Daily frequency (e.g. Twice daily with meals)")
    route: str = Field(default="Oral", description="Administration route (Oral, IV, Inhalation)")
    duration: str = Field(default="Ongoing", description="Duration of therapy")
    timing_slot: str = Field(default="morning", description="morning, afternoon, evening, night")
    purpose: str = Field(default="", description="Clinical indication")
    instructions: str = Field(default="", description="Patient directions")
    dietary_warnings: str = Field(default="", description="Food and nutrient interactions")
    is_high_risk: bool = Field(default=False, description="Narrow therapeutic index flag")
    pill_visual: Optional[PillVisualInfo] = None
    generic_alternative: Optional[GenericAlternative] = None

class DrugInteraction(BaseModel):
    drug_a: str
    drug_b: str
    severity: str = Field(..., description="CRITICAL, MODERATE, or LOW")
    title: str
    mechanism: str
    recommendation: str

class AllergyConflict(BaseModel):
    severity: str = "CRITICAL"
    allergy_detected: str
    conflicting_medication: str
    title: str
    mechanism: str
    recommendation: str

class SafetyAnalysis(BaseModel):
    status: str = Field(..., description="CRITICAL_HAZARD, MODERATE_WARNING, or CLEARED")
    score: int = Field(..., description="Danger score from 0 to 100")
    color: str = Field(..., description="red, amber, or emerald")
    badge: str
    interactions: List[DrugInteraction] = Field(default_factory=list)
    allergy_conflicts: List[AllergyConflict] = Field(default_factory=list)

class SoapNote(BaseModel):
    subjective: str = ""
    objective: str = ""
    assessment: str = ""
    plan: str = ""

class TriageReport(BaseModel):
    level: str = Field(..., description="RED, AMBER, or GREEN")
    score: int = Field(..., description="Emergency Severity Score 0-100")
    title: str
    summary: str
    soap_note: SoapNote

class PatientFriendlyGuide(BaseModel):
    plain_summary: str
    schedule_breakdown: Dict[str, str] = Field(default_factory=dict)
    red_flag_symptoms: List[str] = Field(default_factory=list)
    lifestyle_precautions: str = ""

class EnvironmentalAlert(BaseModel):
    severity: str
    trigger: str
    impact: str
    action: str

class EnvironmentalContext(BaseModel):
    aqi: int = 145
    temperature_c: float = 34.0
    humidity_pct: int = 78
    pollen_level: str = "HIGH"
    environmental_risk_level: str = "LOW"
    risk_score: int = 15
    contextual_alerts: List[EnvironmentalAlert] = Field(default_factory=list)
