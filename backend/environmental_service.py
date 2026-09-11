"""
Environmental & Contextual Risk Factor Engine
Correlates real-world weather, Air Quality Index (AQI), temperature, and pollen
with patient chronic conditions (Asthma, COPD, Hypertension, Heart Failure).
"""
from typing import Dict, Any, List

def analyze_environmental_risks(
    patient_conditions: List[str],
    aqi: int = 145,
    temperature_c: float = 34.0,
    humidity_pct: int = 78,
    pollen_level: str = "HIGH"
) -> Dict[str, Any]:
    """
    Evaluates environmental stress factors against patient medical conditions.
    """
    conditions_lower = [c.lower() for c in (patient_conditions or [])]
    alerts = []
    risk_level = "LOW"
    risk_score = 15

    has_respiratory = any("asthma" in c or "copd" in c or "bronch" in c or "wheez" in c for c in conditions_lower)
    if has_respiratory:
        if aqi > 100:
            alerts.append({
                "severity": "HIGH",
                "trigger": f"Elevated AQI ({aqi} PM2.5)",
                "impact": "Triggers bronchial inflammation and acute bronchospasms in asthmatic patients.",
                "action": "Ensure rescue inhaler (Salbutamol/Levosalbutamol) is immediately accessible. Avoid outdoor exertion."
            })
            risk_level = "HIGH"
            risk_score = max(risk_score, 80)
        if pollen_level in ["HIGH", "VERY_HIGH"]:
            alerts.append({
                "severity": "MODERATE",
                "trigger": f"High Allergen / Pollen Index ({pollen_level})",
                "impact": "Exacerbates allergic rhinitis and nocturnal cough.",
                "action": "Keep windows closed; take prescribed antihistamine (Cetirizine / Montelukast) as scheduled."
            })
            risk_score = max(risk_score, 65)

    has_cardio = any("hypertens" in c or "cardiac" in c or "heart" in c or "fibrillat" in c for c in conditions_lower)
    if has_cardio:
        if temperature_c > 35.0 or (temperature_c > 32.0 and humidity_pct > 70):
            alerts.append({
                "severity": "MODERATE",
                "trigger": f"Extreme Heat & Humidity ({temperature_c}°C, {humidity_pct}% RH)",
                "impact": "Increases cardiac workload and can induce orthostatic hypotension in patients taking ACE inhibitors or diuretics.",
                "action": "Maintain optimal electrolyte hydration; monitor seated vs standing blood pressure."
            })
            risk_score = max(risk_score, 60)

    return {
        "aqi": aqi,
        "temperature_c": temperature_c,
        "humidity_pct": humidity_pct,
        "pollen_level": pollen_level,
        "environmental_risk_level": risk_level,
        "risk_score": risk_score,
        "contextual_alerts": alerts
    }
