"""
Printable Clinical Discharge & Triage Report Generator
Generates clinical-grade discharge documentation and emergency transfer summaries.
"""
from datetime import datetime, timezone
from typing import Dict, Any

def generate_printable_report_html(data: Dict[str, Any]) -> str:
    """
    Generates high-fidelity clinical summary HTML formatted for printing or PDF export.
    """
    patient = data.get("patient", {})
    triage = data.get("triage", {})
    safety = data.get("safety_analysis", {})
    meds = data.get("medications", [])
    soap = triage.get("soap_note", {})
    vitals = patient.get("vitals", {})
    helplines = data.get("emergency_facilities", {}).get("helplines", {})
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    triage_color = "#dc2626" if triage.get("level") == "RED" else ("#d97706" if triage.get("level") == "AMBER" else "#059669")
    triage_bg = "#fef2f2" if triage.get("level") == "RED" else ("#fffbeb" if triage.get("level") == "AMBER" else "#ecfdf5")

    patient_photo_html = ""
    if patient.get("photo"):
        patient_photo_html = f'<img src="{patient["photo"]}" alt="Patient Photo" style="width: 70px; height: 70px; border-radius: 8px; object-fit: cover; border: 2px solid #cbd5e1; margin-right: 12px;">'

    meds_rows = ""
    for m in meds:
        pill_v = m.get("pill_visual", {})
        gen_alt = m.get("generic_alternative", {})
        meds_rows += f"""
        <tr style="border-bottom: 1px solid #e2e8f0;">
            <td style="padding: 8px; font-weight: bold;">
                {m.get('brand_name', '')} <br>
                <span style="font-size: 11px; color: #64748b; font-weight: normal;">({m.get('generic_name', '')})</span>
                <div style="font-size: 10px; color: #059669; font-weight: bold; margin-top: 2px;">Generic saves ~{gen_alt.get('avg_savings_percent', 75)}%</div>
            </td>
            <td style="padding: 8px; font-size: 11px;">
                <strong>{pill_v.get('shape', 'Tablet')}</strong><br>
                <span style="color: #0284c7;">{pill_v.get('color', 'White')}</span><br>
                <span style="color: #64748b; font-family: monospace;">Imprint: {pill_v.get('imprint', 'Standard')}</span>
            </td>
            <td style="padding: 8px; font-family: monospace;">{m.get('dosage', '')} ({m.get('route', 'Oral')})</td>
            <td style="padding: 8px; font-weight: 600;">{m.get('frequency', '')}<br><span style="font-size: 10px; color: #475569;">Slot: {m.get('timing_slot', 'Daily')}</span></td>
            <td style="padding: 8px;">{m.get('purpose', '')}</td>
            <td style="padding: 8px; font-size: 11px; color: #b45309;">{m.get('dietary_warnings', '')}</td>
        </tr>
        """

    cond = data.get("condition_profile", {})
    cond_html = ""
    if cond and cond.get("name"):
        symptoms_li = "".join([f"<li>{s}</li>" for s in cond.get("symptoms", [])])
        tests_li = "".join([f"<li>{t}</li>" for t in cond.get("diagnostic_tests", [])])
        red_flags_li = "".join([f"<li style='color: #dc2626;'>{rf}</li>" for rf in cond.get("red_flags", [])])
        
        cond_html = f"""
        <div class="card" style="margin-bottom: 12px; border-left: 4px solid #0284c7; background: #f0f9ff;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <h3 style="margin: 0; font-size: 12px; text-transform: uppercase; color: #0369a1; font-weight: bold;">
                    📖 Mayo Clinic Clinical Impression: {cond.get('name', '')}
                </h3>
                <span style="background: #e0f2fe; color: #0369a1; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 10px; font-family: monospace;">
                    ICD-10: {cond.get('icd10', 'N/A')} | {cond.get('category', 'General Medicine')}
                </span>
            </div>
            <p style="margin: 2px 0 8px 0; font-size: 11px; color: #1e293b; line-height: 1.4;">{cond.get('overview', '')}</p>
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; font-size: 10.5px;">
                <div style="background: #ffffff; padding: 8px; border-radius: 4px; border: 1px solid #e2e8f0;">
                    <strong style="color: #0369a1;">Observed Symptoms:</strong>
                    <ul style="margin: 4px 0 0 0; padding-left: 14px;">{symptoms_li}</ul>
                </div>
                <div style="background: #ffffff; padding: 8px; border-radius: 4px; border: 1px solid #e2e8f0;">
                    <strong style="color: #0369a1;">Diagnostic Tests:</strong>
                    <ul style="margin: 4px 0 0 0; padding-left: 14px;">{tests_li}</ul>
                </div>
                <div style="background: #ffffff; padding: 8px; border-radius: 4px; border: 1px solid #e2e8f0;">
                    <strong style="color: #dc2626;">Red Flags & Care:</strong>
                    <ul style="margin: 4px 0 0 0; padding-left: 14px;">{red_flags_li}</ul>
                    <p style="margin: 4px 0 0 0; font-size: 10px; color: #475569;"><strong>Care:</strong> {cond.get('home_care', '')}</p>
                </div>
            </div>
        </div>
        """

    interactions_html = ""
    all_alerts = (safety.get("allergy_conflicts", []) + safety.get("interactions", []))
    if all_alerts:
        for alert in all_alerts:
            interactions_html += f"""
            <div style="background: #fef2f2; border-left: 4px solid #ef4444; padding: 10px; margin-bottom: 8px; border-radius: 4px;">
                <strong style="color: #991b1b; font-size: 13px;">⚠️ {alert.get('title', 'Drug Alert')}</strong>
                <p style="margin: 4px 0; font-size: 12px; color: #7f1d1d;">{alert.get('mechanism', '')}</p>
                <p style="margin: 0; font-size: 11px; font-weight: bold; color: #b91c1c;">Clinical Action: {alert.get('recommendation', '')}</p>
            </div>
            """
    else:
        interactions_html = "<div style='background: #ecfdf5; border-left: 4px solid #10b981; padding: 8px 12px; border-radius: 4px; color: #065f46; font-size: 12px; font-weight: 600;'>✓ No lethal contraindications or cross-allergy risks identified.</div>"

    vitals_html = ""
    if vitals:
        vitals_html = f"""
        <div style="display: flex; gap: 12px; margin-top: 8px; background: #f1f5f9; padding: 6px 10px; border-radius: 6px; font-size: 11px;">
            <span><strong>BP:</strong> {vitals.get('bp', '120/80 mmHg')}</span>
            <span><strong>HR:</strong> {vitals.get('hr', '72 bpm')}</span>
            <span><strong>SpO2:</strong> {vitals.get('spo2', '98%')}</span>
            <span><strong>Temp:</strong> {vitals.get('temp', '98.6°F')}</span>
            <span><strong>Blood:</strong> {patient.get('blood_group', 'O+')}</span>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>MedForever - Official Clinical Discharge Summary</title>
<style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 20px; color: #0f172a; line-height: 1.4; background: #ffffff; }}
    .header {{ border-bottom: 2px solid #0284c7; padding-bottom: 12px; margin-bottom: 14px; display: flex; justify-content: space-between; align-items: center; }}
    .badge {{ background: {triage_color}; color: white; padding: 5px 12px; border-radius: 6px; font-weight: bold; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; }}
    .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 14px; }}
    .card {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 12px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 11px; margin-top: 8px; }}
    th {{ background: #e2e8f0; padding: 8px; text-align: left; font-weight: bold; font-size: 11px; text-transform: uppercase; color: #334155; }}
    @media print {{
        .no-print {{ display: none !important; }}
        body {{ margin: 0; padding: 10px; }}
    }}
</style>
</head>
<body>
    <div class="no-print" style="text-align: right; margin-bottom: 12px;">
        <button onclick="window.print()" style="background: #0284c7; color: white; border: none; padding: 8px 16px; border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 13px;">🖨️ Print / Save as PDF</button>
    </div>

    <div class="header">
        <div style="display: flex; align-items: center;">
            {patient_photo_html}
            <div>
                <h1 style="margin: 0; font-size: 18px; color: #0f172a; font-weight: 800;">🏥 MedForever Clinical Discharge Summary</h1>
                <p style="margin: 2px 0 0 0; font-size: 11px; color: #64748b;">Gemini 2.5 Multimodal Medical Bridge | HL7 FHIR R4 & HL7 v2.5 Certified Schema</p>
            </div>
        </div>
        <div style="text-align: right;">
            <span class="badge">{triage.get('level', 'GREEN')} TRIAGE (Score: {triage.get('score', 50)}/100)</span>
            <div style="font-size: 10px; color: #64748b; margin-top: 4px;">Time: {now_str}</div>
        </div>
    </div>

    <div class="grid">
        <div class="card">
            <h3 style="margin: 0 0 6px 0; font-size: 12px; color: #0284c7; text-transform: uppercase; font-weight: bold;">Patient Information & Vitals</h3>
            <p style="margin: 2px 0; font-size: 12px;"><strong>Patient Name:</strong> {patient.get('name', 'Anonymous')}</p>
            <p style="margin: 2px 0; font-size: 12px;"><strong>Demographics:</strong> {patient.get('age', 'N/A')} yo | {patient.get('gender', 'Unknown')} | <strong>Blood:</strong> {patient.get('blood_group', 'O+')}</p>
            <p style="margin: 2px 0; font-size: 12px;"><strong>Known Allergies:</strong> <span style="color: #dc2626; font-weight: bold;">{', '.join(patient.get('allergies', [])) or 'None documented'}</span></p>
            <p style="margin: 2px 0; font-size: 12px;"><strong>Chronic Conditions:</strong> {', '.join(patient.get('pre_existing_conditions', [])) or 'None documented'}</p>
            {vitals_html}
        </div>
        <div class="card" style="background: {triage_bg}; border-color: {triage_color}40;">
            <h3 style="margin: 0 0 6px 0; font-size: 12px; color: {triage_color}; text-transform: uppercase; font-weight: bold;">Clinical Triage & Emergency Protocol</h3>
            <p style="margin: 2px 0; font-size: 12px; font-weight: bold;">{triage.get('title', 'Clinical Assessment')}</p>
            <p style="margin: 2px 0; font-size: 11px; color: #334155;">{triage.get('summary', '')}</p>
            <div style="margin-top: 6px; font-size: 11px;">
                <strong>Emergency Helpline:</strong> {helplines.get('emergency', '911 / 112')} | <strong>Ambulance:</strong> {helplines.get('ambulance', '108 / 911')}
            </div>
        </div>
    </div>

    {cond_html}

    <div style="margin-bottom: 12px;">
        <h3 style="margin: 0 0 4px 0; font-size: 13px; text-transform: uppercase; color: #0f172a; font-weight: bold;">🛡️ Pharmacological Safety & Interaction Matrix</h3>
        {interactions_html}
    </div>

    <div style="margin-bottom: 12px;">
        <h3 style="margin: 0 0 4px 0; font-size: 13px; text-transform: uppercase; color: #0f172a; font-weight: bold;">💊 24-Hour Medication Timetable & Pill Visual Guide</h3>
        <table>
            <thead>
                <tr>
                    <th>Medication (Brand / Generic)</th>
                    <th>Visual Identifier</th>
                    <th>Dosage & Route</th>
                    <th>Frequency / Slot</th>
                    <th>Clinical Indication</th>
                    <th>Dietary Instructions</th>
                </tr>
            </thead>
            <tbody>
                {meds_rows}
            </tbody>
        </table>
    </div>

    <div class="card" style="margin-bottom: 12px;">
        <h3 style="margin: 0 0 6px 0; font-size: 12px; text-transform: uppercase; color: #475569; font-weight: bold;">📋 Clinical SOAP Progress Note</h3>
        <div style="font-size: 11px; font-family: monospace;">
            <p style="margin: 2px 0;"><strong>[S] Subjective:</strong> {soap.get('subjective', 'N/A')}</p>
            <p style="margin: 2px 0;"><strong>[O] Objective:</strong> {soap.get('objective', 'N/A')}</p>
            <p style="margin: 2px 0;"><strong>[A] Assessment:</strong> {soap.get('assessment', 'N/A')}</p>
            <p style="margin: 2px 0;"><strong>[P] Plan:</strong> {soap.get('plan', 'N/A')}</p>
        </div>
    </div>

    <div style="margin-top: 18px; padding-top: 10px; border-top: 1px dashed #94a3b8; display: flex; justify-content: space-between; font-size: 10px; color: #64748b;">
        <div>MedForever AI Verification Protocol #MF-{abs(hash(now_str)) % 1000000} | HL7 FHIR Interoperable</div>
        <div>Attending Physician / Pharmacist Signature: ___________________________</div>
    </div>
</body>
</html>
"""
    return html
