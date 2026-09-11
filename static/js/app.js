/**
 * MedForever Frontend Application Logic v2.0
 * Universal Multimodal Medical Bridge
 */

let currentAnalysisData = null;
let currentFhirBundle = null;
let currentHl7Message = null;
let selectedImageBase64 = null;
let recordedAudioBase64 = null;
let mediaRecorder = null;
let audioChunks = [];
let recordingInterval = null;
let recordSeconds = 0;
let cameraStream = null;
let currentInteropTab = 'fhir';

document.addEventListener("DOMContentLoaded", () => {
  if (window.lucide) {
    window.lucide.createIcons();
  }
  checkApiKeyStatus();
});

// Tab Switching (Image / Audio / Text)
function switchInputTab(tab) {
  const tabs = ['image', 'audio', 'text'];
  tabs.forEach(t => {
    const content = document.getElementById(`tabContent${t.charAt(0).toUpperCase() + t.slice(1)}`);
    const btn = document.getElementById(`tabBtn${t.charAt(0).toUpperCase() + t.slice(1)}`);
    if (t === tab) {
      content.classList.remove('hidden');
      btn.classList.add('bg-slate-800', 'text-white', 'shadow-sm');
      btn.classList.remove('text-slate-400');
    } else {
      content.classList.add('hidden');
      btn.classList.remove('bg-slate-800', 'text-white', 'shadow-sm');
      btn.classList.add('text-slate-400');
    }
  });
  if (window.lucide) window.lucide.createIcons();
}

// Image Selection & Drop Handling
function handleImageSelected(event) {
  const file = event.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = (e) => {
    selectedImageBase64 = e.target.result;
    document.getElementById("imagePreview").src = selectedImageBase64;
    document.getElementById("imagePreviewContainer").classList.remove("hidden");
    document.getElementById("dropZone").classList.add("hidden");
  };
  reader.readAsDataURL(file);
}

function clearImage() {
  selectedImageBase64 = null;
  document.getElementById("prescriptionImageInput").value = "";
  document.getElementById("imagePreview").src = "";
  document.getElementById("imagePreviewContainer").classList.add("hidden");
  document.getElementById("dropZone").classList.remove("hidden");
}

// Live Camera Scanner
async function openLiveCameraModal() {
  const modal = document.getElementById("liveCameraModal");
  const video = document.getElementById("cameraVideo");
  modal.classList.remove("hidden");

  try {
    cameraStream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: "environment", width: { ideal: 1280 }, height: { ideal: 720 } }
    });
    video.srcObject = cameraStream;
  } catch (err) {
    alert("Camera access failed or permission denied: " + err.message);
    closeLiveCameraModal();
  }
  if (window.lucide) window.lucide.createIcons();
}

function closeLiveCameraModal() {
  if (cameraStream) {
    cameraStream.getTracks().forEach(track => track.stop());
    cameraStream = null;
  }
  document.getElementById("liveCameraModal").classList.add("hidden");
}

function captureCameraSnapshot() {
  const video = document.getElementById("cameraVideo");
  const canvas = document.getElementById("cameraCanvas");
  if (!video || !cameraStream) return;

  canvas.width = video.videoWidth || 640;
  canvas.height = video.videoHeight || 480;
  const ctx = canvas.getContext("2d");
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

  selectedImageBase64 = canvas.toDataURL("image/jpeg", 0.9);
  document.getElementById("imagePreview").src = selectedImageBase64;
  document.getElementById("imagePreviewContainer").classList.remove("hidden");
  document.getElementById("dropZone").classList.add("hidden");

  closeLiveCameraModal();
}

// Voice Audio Recording
async function toggleAudioRecording() {
  const btn = document.getElementById("btnRecord");
  const btnText = document.getElementById("btnRecordText");
  const timer = document.getElementById("recordingTimer");

  if (mediaRecorder && mediaRecorder.state === "recording") {
    mediaRecorder.stop();
    clearInterval(recordingInterval);
    btn.classList.remove("bg-slate-700", "animate-pulse");
    btn.classList.add("bg-rose-600");
    btnText.innerText = "Re-record Voice Memo";
    return;
  }

  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    audioChunks = [];

    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) audioChunks.push(e.data);
    };

    mediaRecorder.onstop = () => {
      const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
      const audioUrl = URL.createObjectURL(audioBlob);
      const playback = document.getElementById("audioPlayback");
      playback.src = audioUrl;
      playback.classList.remove("hidden");

      const reader = new FileReader();
      reader.onloadend = () => {
        recordedAudioBase64 = reader.result;
      };
      reader.readAsDataURL(audioBlob);

      stream.getTracks().forEach(track => track.stop());
    };

    mediaRecorder.start();
    recordSeconds = 0;
    timer.innerText = "00:00";
    recordingInterval = setInterval(() => {
      recordSeconds++;
      const mins = String(Math.floor(recordSeconds / 60)).padStart(2, '0');
      const secs = String(recordSeconds % 60).padStart(2, '0');
      timer.innerText = `${mins}:${secs}`;
    }, 1000);

    btn.classList.remove("bg-rose-600");
    btn.classList.add("bg-slate-700", "animate-pulse");
    btnText.innerText = "Stop Recording";
  } catch (err) {
    alert("Microphone access is required for voice memo recording: " + err.message);
  }
}

// 1-Click Preset Scenario Loader
async function loadScenario(scenarioId) {
  showLoading(true, "Loading Scenario...", "Extracting clinical entities, pill appearances, and FHIR payloads...");
  try {
    const res = await fetch(`/api/scenarios/${scenarioId}`);
    const data = await res.json();
    currentAnalysisData = data.scenario;
    currentFhirBundle = data.fhir_bundle;
    currentHl7Message = data.hl7_message;

    if (data.scenario.patient) {
      document.getElementById("patientAllergiesInput").value = (data.scenario.patient.allergies || []).join(", ");
      document.getElementById("patientHistoryInput").value = (data.scenario.patient.pre_existing_conditions || []).join(", ");
    }
    if (data.scenario.raw_text_preview) {
      document.getElementById("textNotesInput").value = data.scenario.raw_text_preview;
    }

    renderResults(currentAnalysisData, currentFhirBundle, currentHl7Message);
  } catch (err) {
    alert("Failed to load scenario: " + err.message);
  } finally {
    showLoading(false);
  }
}

// Execute Analysis
async function executeAnalysis() {
  const notes = document.getElementById("textNotesInput").value;
  const allergies = document.getElementById("patientAllergiesInput").value;
  const history = document.getElementById("patientHistoryInput").value;
  const lang = document.getElementById("targetLanguageSelect").value;

  if (!selectedImageBase64 && !recordedAudioBase64 && !notes && !allergies && !history) {
    alert("Please provide at least one input: upload/scan a prescription image, record a voice memo, or enter clinical notes.");
    return;
  }

  showLoading(true, "Gemini Multimodal Reasoning...", "Processing handwriting OCR, audio waveform, and drug contraindications...");

  try {
    const payload = {
      image_data: selectedImageBase64,
      audio_data: recordedAudioBase64,
      text_notes: notes,
      patient_history: history,
      patient_allergies: allergies,
      target_language: lang
    };

    const res = await fetch("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    currentAnalysisData = data.analysis;
    currentFhirBundle = data.fhir_bundle;
    currentHl7Message = data.hl7_message;

    renderResults(currentAnalysisData, currentFhirBundle, currentHl7Message);
  } catch (err) {
    alert("Analysis failed: " + err.message);
  } finally {
    showLoading(false);
  }
}

// Render Results to UI
function renderResults(data, fhirBundle, hl7Message) {
  document.getElementById("welcomeState").classList.add("hidden");
  document.getElementById("resultsDashboard").classList.remove("hidden");

  // 1. Triage Banner
  const triage = data.triage || {};
  const banner = document.getElementById("triageBanner");
  const iconBox = document.getElementById("triageIconBox");
  const levelTag = document.getElementById("triageLevelTag");
  const scoreTag = document.getElementById("triageScoreTag");
  const title = document.getElementById("triageTitle");
  const summary = document.getElementById("triageSummary");

  title.innerText = triage.title || "Clinical Assessment";
  summary.innerText = triage.summary || "";
  scoreTag.innerText = `Triage Urgency: ${triage.score || 50}/100`;

  banner.className = "p-5 rounded-2xl border transition-all flex flex-col md:flex-row items-start md:items-center justify-between gap-4 shadow-xl";
  if (triage.level === "RED") {
    banner.classList.add("bg-red-950/40", "border-red-500/60");
    iconBox.className = "w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0 bg-red-900/60 text-red-400 border border-red-700/60 pulse-danger";
    levelTag.className = "px-2.5 py-0.5 text-xs font-black rounded-full uppercase tracking-wide bg-red-600 text-white";
    levelTag.innerText = "RED: CRITICAL EMERGENCY";
  } else if (triage.level === "AMBER") {
    banner.classList.add("bg-amber-950/40", "border-amber-500/60");
    iconBox.className = "w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0 bg-amber-900/60 text-amber-400 border border-amber-700/60";
    levelTag.className = "px-2.5 py-0.5 text-xs font-black rounded-full uppercase tracking-wide bg-amber-600 text-white";
    levelTag.innerText = "AMBER: URGENT ACTION";
  } else {
    banner.classList.add("bg-emerald-950/40", "border-emerald-500/60");
    iconBox.className = "w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0 bg-emerald-900/60 text-emerald-400 border border-emerald-700/60";
    levelTag.className = "px-2.5 py-0.5 text-xs font-black rounded-full uppercase tracking-wide bg-emerald-600 text-white";
    levelTag.innerText = "GREEN: ROUTINE / STABLE";
  }

  // 2. Environmental Context Card
  const env = data.environmental_context;
  const envCard = document.getElementById("envRiskCard");
  if (env) {
    envCard.classList.remove("hidden");
    document.getElementById("envAqi").innerText = `AQI ${env.aqi}`;
    document.getElementById("envTemp").innerText = `${env.temperature_c}°C (${env.humidity_pct}%)`;
    document.getElementById("envPollen").innerText = env.pollen_level;

    const badge = document.getElementById("envRiskBadge");
    badge.innerText = `${env.environmental_risk_level} ENVIRONMENTAL RISK`;
    badge.className = `text-[10px] font-bold px-2 py-0.5 rounded-full ${env.environmental_risk_level === 'HIGH' ? 'bg-rose-900 text-rose-300' : 'bg-slate-800 text-slate-300'}`;

    const alertsContainer = document.getElementById("envAlertsContainer");
    alertsContainer.innerHTML = "";
    (env.contextual_alerts || []).forEach(al => {
      const div = document.createElement("div");
      div.className = "p-2 rounded-lg bg-slate-950/80 border border-slate-800 text-[11px] text-amber-300 flex items-start gap-1.5";
      div.innerHTML = `<i data-lucide="alert-triangle" class="w-3.5 h-3.5 text-amber-400 flex-shrink-0 mt-0.5"></i> <span><strong>${al.trigger}:</strong> ${al.impact} (${al.action})</span>`;
      alertsContainer.appendChild(div);
    });
  } else {
    envCard.classList.add("hidden");
  }

  // 3. Safety Matrix & Interactions
  const safety = data.safety_analysis || {};
  const safetyBadge = document.getElementById("safetyBadge");
  safetyBadge.innerText = safety.badge || "Safety Checked";
  if (safety.color === "red") {
    safetyBadge.className = "text-[11px] font-bold px-2.5 py-1 rounded-full bg-red-900/60 text-red-300 border border-red-700/60";
  } else if (safety.color === "amber") {
    safetyBadge.className = "text-[11px] font-bold px-2.5 py-1 rounded-full bg-amber-900/60 text-amber-300 border border-amber-700/60";
  } else {
    safetyBadge.className = "text-[11px] font-bold px-2.5 py-1 rounded-full bg-emerald-900/60 text-emerald-300 border border-emerald-700/60";
  }

  const interactionList = document.getElementById("interactionList");
  interactionList.innerHTML = "";

  const allAlerts = [
    ...(safety.allergy_conflicts || []).map(a => ({ ...a, is_allergy: true })),
    ...(safety.interactions || []).map(i => ({ ...i, is_allergy: false }))
  ];

  if (allAlerts.length === 0) {
    interactionList.innerHTML = `
      <div class="p-3.5 rounded-xl bg-emerald-950/30 border border-emerald-800/40 text-xs text-emerald-300 flex items-center gap-2">
        <i data-lucide="check-circle" class="w-4 h-4 text-emerald-400"></i>
        <span>No lethal drug-drug interactions or cross-allergies detected. Prescriptions cleared for administration.</span>
      </div>
    `;
  } else {
    allAlerts.forEach(alertItem => {
      const isCrit = alertItem.severity === "CRITICAL";
      const card = document.createElement("div");
      card.className = `p-3.5 rounded-xl border ${isCrit ? 'bg-red-950/40 border-red-500/60 text-red-200' : 'bg-amber-950/40 border-amber-500/60 text-amber-200'}`;
      card.innerHTML = `
        <div class="flex items-center justify-between font-bold text-xs mb-1">
          <span class="flex items-center gap-1.5">
            <i data-lucide="${isCrit ? 'alert-triangle' : 'alert-circle'}" class="w-4 h-4 ${isCrit ? 'text-red-400' : 'text-amber-400'}"></i>
            ${alertItem.title || 'Drug Hazard Alert'}
          </span>
          <span class="text-[10px] px-2 py-0.5 rounded uppercase ${isCrit ? 'bg-red-900/80 text-red-200' : 'bg-amber-900/80 text-amber-200'}">${alertItem.severity}</span>
        </div>
        <p class="text-[11px] opacity-90 leading-relaxed mb-2">${alertItem.mechanism || ''}</p>
        <div class="p-2 rounded-lg bg-slate-950/60 border border-slate-800 text-[11px]">
          <strong class="${isCrit ? 'text-red-400' : 'text-amber-400'}">Life-Saving Action:</strong> ${alertItem.recommendation || ''}
        </div>
      `;
      interactionList.appendChild(card);
    });
  }

  // 4. Medications & Pill Appearance Table
  const meds = data.medications || [];
  const patient = data.patient || {};
  document.getElementById("patientMeta").innerText = `Patient: ${patient.name || 'Anonymous'} (${patient.age || 'N/A'}yo ${patient.gender || ''})`;

  const tbody = document.getElementById("medicationsTableBody");
  tbody.innerHTML = "";
  meds.forEach(med => {
    const tr = document.createElement("tr");
    tr.className = "hover:bg-slate-800/40 transition-colors";
    
    const pillVis = med.pill_visual || { shape: "Oral Tablet", color: "White", imprint: "Standard" };
    const genericAlt = med.generic_alternative || { available: true, avg_savings_percent: 75 };

    tr.innerHTML = `
      <td class="py-2.5 px-3">
        <div class="font-bold text-white flex items-center gap-1.5">
          ${med.brand_name || med.generic_name}
          ${med.is_high_risk ? '<span class="px-1.5 py-0.2 text-[9px] bg-red-900/80 text-red-300 rounded font-mono">HIGH RISK</span>' : ''}
        </div>
        <div class="text-[11px] text-slate-400 font-mono">${med.generic_name || ''}</div>
        <span class="inline-block mt-1 text-[10px] font-semibold text-emerald-400 bg-emerald-950/80 px-1.5 py-0.2 rounded border border-emerald-800/60">
          Generic Saves ~${genericAlt.avg_savings_percent}%
        </span>
      </td>
      <td class="py-2.5 px-3">
        <div class="text-xs text-slate-200 font-medium">${pillVis.shape}</div>
        <div class="text-[10px] text-cyan-300">${pillVis.color}</div>
        <div class="text-[9px] text-slate-400 font-mono">Imprint: ${pillVis.imprint}</div>
      </td>
      <td class="py-2.5 px-3 font-mono text-[11px] text-cyan-300">
        <div>${med.dosage || 'N/A'} (${med.route || 'Oral'})</div>
        <div class="text-[11px] text-slate-300 font-sans">${med.frequency || ''}</div>
      </td>
      <td class="py-2.5 px-3 text-[11px] text-slate-300">
        <div class="font-medium text-slate-200">${med.purpose || ''}</div>
        <div class="text-[10px] text-amber-300/90">${med.dietary_warnings || med.instructions || ''}</div>
      </td>
    `;
    tbody.appendChild(tr);
  });

  // 5. Chrono-Dosing Timeline
  const guide = data.patient_friendly_guide || {};
  const sched = guide.schedule_breakdown || {};
  document.getElementById("scheduleMorning").innerText = sched.morning || "No scheduled pills";
  document.getElementById("scheduleAfternoon").innerText = sched.afternoon || "No scheduled pills";
  document.getElementById("scheduleEvening").innerText = sched.evening || "No scheduled pills";
  document.getElementById("scheduleNight").innerText = sched.night || "No scheduled pills";

  // 6. Patient Friendly Guide & Red Flags
  document.getElementById("plainSummaryText").innerText = guide.plain_summary || "Prescription instructions verified.";
  const redFlagsUl = document.getElementById("redFlagList");
  redFlagsUl.innerHTML = "";
  (guide.red_flag_symptoms || []).forEach(rf => {
    const li = document.createElement("li");
    li.className = "flex items-start gap-1.5 text-slate-300";
    li.innerHTML = `<span class="text-red-400">•</span> <span>${rf}</span>`;
    redFlagsUl.appendChild(li);
  });

  // 7. SOAP Notes
  const soap = (triage.soap_note || {});
  document.getElementById("soapSubjective").innerText = soap.subjective || "N/A";
  document.getElementById("soapObjective").innerText = soap.objective || "N/A";
  document.getElementById("soapAssessment").innerText = soap.assessment || "N/A";
  document.getElementById("soapPlan").innerText = soap.plan || "N/A";

  // 8. FHIR & HL7 Blocks
  if (fhirBundle) {
    document.getElementById("fhirJsonBlock").innerText = JSON.stringify(fhirBundle, null, 2);
  }
  if (hl7Message) {
    document.getElementById("hl7Block").innerText = hl7Message;
  }

  // Update QR Code
  generateHealthCardQr(patient, meds);

  if (window.lucide) window.lucide.createIcons();
}

// Adherence Tracker
function updateAdherence() {
  const checkboxes = document.querySelectorAll('input[type="checkbox"]');
  let checkedCount = 0;
  checkboxes.forEach(cb => { if (cb.checked) checkedCount++; });
  const pct = Math.round((checkedCount / Math.max(1, checkboxes.length)) * 100);
  document.getElementById("adherenceRateTag").innerText = `Adherence: ${pct}% Logged`;
}

// Text-to-Speech Explainer
function speakPatientSummary() {
  const text = document.getElementById("plainSummaryText").innerText;
  if (!text) return;
  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.95;
    utterance.pitch = 1.0;
    window.speechSynthesis.speak(utterance);
  } else {
    alert("Text-to-speech is not supported in this browser.");
  }
}

// Emergency SOS Modal
function triggerEmergencySOS() {
  if (!currentAnalysisData) return;
  const p = currentAnalysisData.patient || {};
  const meds = (currentAnalysisData.medications || []).map(m => m.generic_name || m.brand_name).join(", ");
  
  document.getElementById("sosPatientName").innerText = `${p.name || 'Unknown'} (${p.age || 'N/A'}yo ${p.gender || ''})`;
  document.getElementById("sosAllergies").innerText = (p.allergies || []).join(", ") || "None Documented";
  document.getElementById("sosMeds").innerText = meds || "None";
  document.getElementById("sosClinicalNote").innerText = currentAnalysisData.triage?.title || "Acute Triage Event";
  
  document.getElementById("emergencySosModal").classList.remove("hidden");
  if (window.lucide) window.lucide.createIcons();
}

function closeEmergencySOS() {
  document.getElementById("emergencySosModal").classList.add("hidden");
}

// Health Card & QR Code
function generateHealthCardQr(patient, meds) {
  const qrDiv = document.getElementById("qrcode");
  qrDiv.innerHTML = "";

  const payload = {
    app: "MedForever Emergency QR",
    patient: patient.name || "Anonymous",
    age: patient.age,
    allergies: patient.allergies || [],
    meds: (meds || []).map(m => m.generic_name || m.brand_name)
  };

  try {
    new QRCode(qrDiv, {
      text: JSON.stringify(payload),
      width: 140,
      height: 140,
      colorDark: "#020617",
      colorLight: "#ffffff",
      correctLevel: QRCode.CorrectLevel.M
    });
  } catch (e) {
    console.error("QR Code Error:", e);
  }

  document.getElementById("cardPatientName").innerText = `${patient.name || 'Anonymous'} (${patient.age || 'N/A'}yo ${patient.gender || ''})`;
  document.getElementById("cardAllergies").innerText = (patient.allergies || []).join(", ") || "None Documented";
  document.getElementById("cardMeds").innerText = (meds || []).map(m => m.brand_name).join(", ") || "None";
}

function openHealthCardModal() {
  document.getElementById("healthCardModal").classList.remove("hidden");
}

function closeHealthCardModal() {
  document.getElementById("healthCardModal").classList.add("hidden");
}

// Interoperability Views (FHIR / HL7)
function toggleInteropView() {
  const cont = document.getElementById("interopViewerContainer");
  const btn = document.getElementById("interopToggleBtnText");
  if (cont.classList.contains("hidden")) {
    cont.classList.remove("hidden");
    btn.innerText = "Hide Interop";
  } else {
    cont.classList.add("hidden");
    btn.innerText = "FHIR / HL7";
  }
}

function switchInteropTab(tab) {
  currentInteropTab = tab;
  const fhirBlock = document.getElementById("fhirJsonBlock");
  const hl7Block = document.getElementById("hl7Block");
  const btnFhir = document.getElementById("tabBtnFhir");
  const btnHl7 = document.getElementById("tabBtnHl7");

  if (tab === 'fhir') {
    fhirBlock.classList.remove("hidden");
    hl7Block.classList.add("hidden");
    btnFhir.className = "px-3 py-1 rounded bg-slate-800 text-cyan-400 font-bold";
    btnHl7.className = "px-3 py-1 rounded bg-slate-950 text-slate-400";
  } else {
    fhirBlock.classList.add("hidden");
    hl7Block.classList.remove("hidden");
    btnHl7.className = "px-3 py-1 rounded bg-slate-800 text-amber-400 font-bold";
    btnFhir.className = "px-3 py-1 rounded bg-slate-950 text-slate-400";
  }
}

function copyCurrentInteropCode() {
  const text = currentInteropTab === 'fhir' 
    ? document.getElementById("fhirJsonBlock").innerText
    : document.getElementById("hl7Block").innerText;

  navigator.clipboard.writeText(text).then(() => {
    const btnText = document.getElementById("copyInteropText");
    btnText.innerText = "Copied!";
    setTimeout(() => { btnText.innerText = "Copy"; }, 2000);
  });
}

// Download Clinical PDF / Printable Summary
async function downloadClinicalReport() {
  if (!currentAnalysisData) {
    alert("Please analyze or load a scenario first.");
    return;
  }
  try {
    const res = await fetch("/api/report/html", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ analysis_data: currentAnalysisData })
    });
    const html = await res.text();
    const win = window.open("", "_blank");
    win.document.write(html);
    win.document.close();
  } catch (e) {
    alert("Failed to generate clinical summary: " + e.message);
  }
}

// Loading Spinner helper
function showLoading(show, title = "Processing...", subtitle = "Please wait...") {
  const loader = document.getElementById("loadingState");
  const btn = document.getElementById("btnAnalyze");
  if (show) {
    document.getElementById("loadingTitle").innerText = title;
    document.getElementById("loadingSubtitle").innerText = subtitle;
    loader.classList.remove("hidden");
    btn.disabled = true;
    btn.classList.add("opacity-60", "cursor-not-allowed");
  } else {
    loader.classList.add("hidden");
    btn.disabled = false;
    btn.classList.remove("opacity-60", "cursor-not-allowed");
  }
}

// API Key Modal
function openApiKeyModal() {
  document.getElementById("apiKeyModal").classList.remove("hidden");
}

function closeApiKeyModal() {
  document.getElementById("apiKeyModal").classList.add("hidden");
}

async function saveApiKey() {
  const key = document.getElementById("apiKeyInput").value.trim();
  if (!key) return;
  try {
    const res = await fetch("/api/key", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ api_key: key })
    });
    const data = await res.json();
    if (data.success) {
      closeApiKeyModal();
      checkApiKeyStatus();
      alert("Gemini API key configured successfully!");
    }
  } catch (e) {
    alert("Failed to set API key: " + e.message);
  }
}

async function checkApiKeyStatus() {
  try {
    const res = await fetch("/api/key/status");
    const data = await res.json();
    const btnText = document.getElementById("apiKeyBtnText");
    if (data.configured) {
      btnText.innerText = data.masked_key || "Key Active";
    } else {
      btnText.innerText = "Set Key";
    }
  } catch (e) {}
}
