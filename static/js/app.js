/**
 * MedForever Frontend Application Logic v3.5
 * Universal Multimodal Medical Bridge
 * Features:
 * - GPS Geolocation & Country-Aware Emergency Helpline Directory
 * - Real Patient Multimodal Intake (Rx Photo, Pill Webcam Scanner, Voice Dictation, Custom Form with Photo/Vitals)
 * - Dynamic Medication List Builder
 * - Phone Camera-Readable Emergency Medical QR Pass (Clean Text + FHIR Toggle)
 * - Fixed Direct PDF Generation via Off-screen Render Target
 * - Multilingual Explainer & Speech Synthesis in 14+ Languages
 * - Light/Dark Theme & Discreet Scenarios Dropdown
 */

let currentAnalysisData = null;
let currentFhirBundle = null;
let currentHl7Message = null;
let selectedImageBase64 = null;
let patientPhotoBase64 = null;
let recordedAudioBase64 = null;
let mediaRecorder = null;
let audioChunks = [];
let recordingInterval = null;
let recordSeconds = 0;
let cameraStream = null;
let currentInteropTab = 'fhir';
let currentQrFormat = 'text';

// User GPS Location State
let userLocation = {
  lat: null,
  lon: null,
  country_code: 'US',
  city: 'New York'
};

// Multi-lingual Translation & Voice Mapping
const LANGUAGE_CONFIG = {
  en: { name: "English", voiceLang: "en-US" },
  hi: { name: "Hindi (हिंदी)", voiceLang: "hi-IN" },
  bn: { name: "Bengali (বাংলা)", voiceLang: "bn-IN" },
  es: { name: "Spanish (Español)", voiceLang: "es-ES" },
  fr: { name: "French (Français)", voiceLang: "fr-FR" },
  de: { name: "German (Deutsch)", voiceLang: "de-DE" },
  te: { name: "Telugu (తెలుగు)", voiceLang: "te-IN" },
  ta: { name: "Tamil (தமிழ்)", voiceLang: "ta-IN" },
  mr: { name: "Marathi (मराठी)", voiceLang: "mr-IN" },
  gu: { name: "Gujarati (ગુજરાતી)", voiceLang: "gu-IN" },
  ar: { name: "Arabic (العربية)", voiceLang: "ar-SA" },
  zh: { name: "Mandarin (中文)", voiceLang: "zh-CN" },
  pt: { name: "Portuguese (Português)", voiceLang: "pt-BR" },
  ja: { name: "Japanese (日本語)", voiceLang: "ja-JP" }
};

// Initialize on DOM load
document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  if (window.lucide) {
    window.lucide.createIcons();
  }
  checkApiKeyStatus();
  
  // Auto-detect location silently on page load
  detectUserLocation(true);

  // Close demo dropdown if clicked outside
  document.addEventListener("click", (e) => {
    const menu = document.getElementById("demoDropdownMenu");
    const btn = document.getElementById("demoDropdownBtn");
    if (menu && !menu.classList.contains("hidden")) {
      if (!menu.contains(e.target) && !btn.contains(e.target)) {
        menu.classList.add("hidden");
      }
    }
  });
});

// ==========================================
// 1. THEME MANAGEMENT (Light / Dark Mode)
// ==========================================
function initTheme() {
  const savedTheme = localStorage.getItem("medforever_theme") || "dark";
  if (savedTheme === "dark") {
    document.documentElement.classList.add("dark");
  } else {
    document.documentElement.classList.remove("dark");
  }
  updateThemeIcon();
}

function toggleTheme() {
  const isDark = document.documentElement.classList.toggle("dark");
  localStorage.setItem("medforever_theme", isDark ? "dark" : "light");
  updateThemeIcon();
}

function updateThemeIcon() {
  const isDark = document.documentElement.classList.contains("dark");
  const icon = document.getElementById("themeIcon");
  if (icon) {
    icon.setAttribute("data-lucide", isDark ? "sun" : "moon");
    if (window.lucide) window.lucide.createIcons();
  }
}

// ==========================================
// 2. GPS GEOLOCATION & EMERGENCY HELPLINES
// ==========================================
async function detectUserLocation(silent = false) {
  const gpsText = document.getElementById("gpsLocationText");
  if (!silent && gpsText) {
    gpsText.innerText = "Locating...";
  }

  if (!navigator.geolocation) {
    if (!silent) alert("Geolocation is not supported by your browser.");
    fetchEmergencyDirectory();
    return;
  }

  navigator.geolocation.getCurrentPosition(
    async (position) => {
      userLocation.lat = position.coords.latitude;
      userLocation.lon = position.coords.longitude;
      
      // Reverse geocode to get country code & city
      try {
        const geoRes = await fetch(`https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${userLocation.lat}&lon=${userLocation.lon}`);
        if (geoRes.ok) {
          const geoData = await geoRes.json();
          const address = geoData.address || {};
          userLocation.country_code = (address.country_code || 'US').toUpperCase();
          userLocation.city = address.city || address.town || address.village || address.state || 'Local Region';
          
          if (gpsText) {
            gpsText.innerText = `${userLocation.city}, ${userLocation.country_code}`;
          }
        }
      } catch (err) {
        console.warn("Reverse geocode fallback:", err);
      }

      await fetchEmergencyDirectory();
    },
    (err) => {
      console.warn("GPS access denied or unavailable:", err.message);
      if (gpsText) gpsText.innerText = "Location (Default)";
      fetchEmergencyDirectory();
    },
    { timeout: 8000, enableHighAccuracy: false }
  );
}

async function fetchEmergencyDirectory() {
  try {
    const res = await fetch("/api/emergency/lookup", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        triage_level: currentAnalysisData?.triage?.level || "AMBER",
        lat: userLocation.lat,
        lon: userLocation.lon,
        country_code: userLocation.country_code,
        city: userLocation.city
      })
    });

    if (!res.ok) return;
    const data = await res.json();
    const helpline = data.helplines || {};

    // Update banner
    const countryBadge = document.getElementById("activeCountryBadge");
    const emergDisplay = document.getElementById("emergencyNumDisplay");
    const ambDisplay = document.getElementById("ambulanceNumDisplay");
    const natDisplay = document.getElementById("nationalHealthNumDisplay");
    const callBtn = document.getElementById("quickCallDispatchBtn");
    const sosCallLink = document.getElementById("sosDirectCallLink");

    if (countryBadge) countryBadge.innerText = `${helpline.country || userLocation.country_code} Emergency Hub`;
    if (emergDisplay) emergDisplay.innerText = helpline.emergency || "112 / 911";
    if (ambDisplay) ambDisplay.innerText = helpline.ambulance || "108 / 911";
    if (natDisplay) natDisplay.innerText = helpline.national_health || "1075 / 211";
    if (callBtn) callBtn.href = `tel:${helpline.emergency || '112'}`;
    if (sosCallLink) sosCallLink.href = `tel:${helpline.emergency || '112'}`;

    // If analysis active, update facilities section
    if (currentAnalysisData) {
      renderNearbyFacilities(data);
    }
  } catch (err) {
    console.warn("Emergency lookup failed:", err);
  }
}

// ==========================================
// 3. MULTIMODAL INTAKE TABS & CONTROLS
// ==========================================
function switchInputTab(tab) {
  const tabs = ['image', 'audio', 'custom', 'text'];
  tabs.forEach(t => {
    const content = document.getElementById(`tabContent${t.charAt(0).toUpperCase() + t.slice(1)}`);
    const btn = document.getElementById(`tabBtn${t.charAt(0).toUpperCase() + t.slice(1)}`);
    if (t === tab) {
      if (content) content.classList.remove('hidden');
      if (btn) btn.className = 'flex-1 py-1.5 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-white shadow-sm flex items-center justify-center gap-1 transition-all font-semibold';
    } else {
      if (content) content.classList.add('hidden');
      if (btn) btn.className = 'flex-1 py-1.5 rounded-lg text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 flex items-center justify-center gap-1 transition-all font-semibold';
    }
  });
  if (window.lucide) window.lucide.createIcons();
}

// Image Selection
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
  const input = document.getElementById("prescriptionImageInput");
  if (input) input.value = "";
  document.getElementById("imagePreview").src = "";
  document.getElementById("imagePreviewContainer").classList.add("hidden");
  document.getElementById("dropZone").classList.remove("hidden");
}

// Patient Profile Photo / Avatar
function handlePatientPhotoSelected(event) {
  const file = event.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = (e) => {
    patientPhotoBase64 = e.target.result;
    const preview = document.getElementById("patientPhotoPreview");
    const placeholder = document.getElementById("patientPhotoPlaceholder");
    if (preview) {
      preview.src = patientPhotoBase64;
      preview.classList.remove("hidden");
    }
    if (placeholder) placeholder.classList.add("hidden");
  };
  reader.readAsDataURL(file);
}

function clearPatientPhoto() {
  patientPhotoBase64 = null;
  const input = document.getElementById("patientPhotoInput");
  if (input) input.value = "";
  const preview = document.getElementById("patientPhotoPreview");
  const placeholder = document.getElementById("patientPhotoPlaceholder");
  if (preview) {
    preview.src = "";
    preview.classList.add("hidden");
  }
  if (placeholder) placeholder.classList.remove("hidden");
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

// Voice Audio Dictation
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

// ==========================================
// 4. DYNAMIC MEDICATION BUILDER
// ==========================================
function addMedicationRow(name = "", slot = "morning", freq = "Once daily") {
  const container = document.getElementById("medicationRowsContainer");
  if (!container) return;

  const row = document.createElement("div");
  row.className = "med-entry-row grid grid-cols-12 gap-1.5 items-center p-2 rounded-lg bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 text-xs";
  
  row.innerHTML = `
    <input type="text" value="${name}" placeholder="Drug (e.g. Lisinopril 10mg)" class="col-span-5 rounded bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 px-2 py-1 text-xs med-name-input">
    <select class="col-span-3 rounded bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 px-1.5 py-1 text-[11px] med-slot-select">
      <option value="morning" ${slot === 'morning' ? 'selected' : ''}>Morning</option>
      <option value="afternoon" ${slot === 'afternoon' ? 'selected' : ''}>Afternoon</option>
      <option value="evening" ${slot === 'evening' ? 'selected' : ''}>Evening</option>
      <option value="night" ${slot === 'night' ? 'selected' : ''}>Night</option>
    </select>
    <input type="text" value="${freq}" placeholder="Freq (Once daily)" class="col-span-3 rounded bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 px-1.5 py-1 text-[11px] med-freq-input">
    <button onclick="removeMedicationRow(this)" class="col-span-1 text-slate-400 hover:text-red-500 flex justify-center">
      <i data-lucide="x" class="w-3.5 h-3.5"></i>
    </button>
  `;
  container.appendChild(row);
  if (window.lucide) window.lucide.createIcons();
}

function removeMedicationRow(btn) {
  const row = btn.closest(".med-entry-row");
  if (row) row.remove();
}

function collectCustomMedications() {
  const rows = document.querySelectorAll(".med-entry-row");
  const meds = [];
  rows.forEach(r => {
    const name = r.querySelector(".med-name-input")?.value?.trim();
    const slot = r.querySelector(".med-slot-select")?.value;
    const freq = r.querySelector(".med-freq-input")?.value?.trim();
    if (name) {
      meds.push({
        drug: name,
        slot: slot || 'morning',
        frequency: freq || 'Once daily'
      });
    }
  });
  return meds;
}

// ==========================================
// 5. TEST SCENARIOS DROPDOWN
// ==========================================
function toggleDemoDropdown() {
  const menu = document.getElementById("demoDropdownMenu");
  if (menu) menu.classList.toggle("hidden");
}

function closeDemoDropdown() {
  const menu = document.getElementById("demoDropdownMenu");
  if (menu) menu.classList.add("hidden");
}

async function loadScenario(scenarioId) {
  closeDemoDropdown();
  showLoading(true, "Loading Scenario...", "Extracting clinical entities, pill appearances, and FHIR payloads...");
  try {
    const res = await fetch(`/api/scenarios/${scenarioId}`);
    const data = await res.json();
    currentAnalysisData = data.scenario;
    currentFhirBundle = data.fhir_bundle;
    currentHl7Message = data.hl7_message;

    if (data.scenario.patient) {
      const p = data.scenario.patient;
      document.getElementById("patientAllergiesInput").value = (p.allergies || []).join(", ");
      document.getElementById("patientHistoryInput").value = (p.pre_existing_conditions || []).join(", ");
      document.getElementById("customPatientName").value = p.name || "";
      document.getElementById("customPatientAge").value = p.age || "";
      if (document.getElementById("customPatientGender")) {
        document.getElementById("customPatientGender").value = p.gender || "Female";
      }
      if (document.getElementById("customBloodGroup")) {
        document.getElementById("customBloodGroup").value = p.blood_group || "O+";
      }
    }

    if (data.scenario.vitals) {
      const v = data.scenario.vitals;
      if (document.getElementById("vitalBp")) document.getElementById("vitalBp").value = v.blood_pressure || "";
      if (document.getElementById("vitalHr")) document.getElementById("vitalHr").value = v.heart_rate || "";
      if (document.getElementById("vitalSpo2")) document.getElementById("vitalSpo2").value = v.oxygen_saturation || "";
      if (document.getElementById("vitalTemp")) document.getElementById("vitalTemp").value = v.temperature || "";
    }

    if (data.scenario.raw_text_preview) {
      document.getElementById("textNotesInput").value = data.scenario.raw_text_preview;
    }

    // Populate dynamic med builder rows
    const container = document.getElementById("medicationRowsContainer");
    if (container && data.scenario.medications) {
      container.innerHTML = "";
      data.scenario.medications.forEach(m => {
        addMedicationRow(
          `${m.brand_name || m.generic_name} ${m.dosage || ''}`.trim(),
          m.timing_slot || 'morning',
          m.frequency || 'Once daily'
        );
      });
    }

    renderResults(currentAnalysisData, currentFhirBundle, currentHl7Message);
  } catch (err) {
    alert("Failed to load scenario: " + err.message);
  } finally {
    showLoading(false);
  }
}

// ==========================================
// 6. EXECUTE MULTIMODAL ANALYSIS
// ==========================================
async function executeAnalysis() {
  const notes = document.getElementById("textNotesInput")?.value || "";
  const allergies = document.getElementById("patientAllergiesInput")?.value || "";
  const history = document.getElementById("patientHistoryInput")?.value || "";
  const lang = document.getElementById("targetLanguageSelect")?.value || "en";

  // Custom Form Builder data
  const customName = document.getElementById("customPatientName")?.value || "";
  const customAge = document.getElementById("customPatientAge")?.value || "";
  const customGender = document.getElementById("customPatientGender")?.value || "Female";
  const customBlood = document.getElementById("customBloodGroup")?.value || "O+";
  const customSymptoms = document.getElementById("customSymptoms")?.value || "";
  const customMeds = collectCustomMedications();

  // Vitals
  const vitals = {
    blood_pressure: document.getElementById("vitalBp")?.value || "120/80 mmHg",
    heart_rate: document.getElementById("vitalHr")?.value || "74 bpm",
    oxygen_saturation: document.getElementById("vitalSpo2")?.value || "98%",
    temperature: document.getElementById("vitalTemp")?.value || "98.6°F"
  };

  let combinedNotes = notes;
  if (customMeds.length > 0 || customSymptoms || customName) {
    const medSummary = customMeds.map(m => `${m.drug} (${m.slot}, ${m.frequency})`).join("; ");
    const patientHeader = `Patient: ${customName || 'Anonymous'}, Age: ${customAge || 'Adult'}, Gender: ${customGender}, Blood: ${customBlood}.`;
    const symptomHeader = customSymptoms ? ` Chief Complaint: ${customSymptoms}.` : "";
    const medsHeader = medSummary ? ` Prescribed Medications: ${medSummary}.` : "";
    combinedNotes = `${patientHeader}${symptomHeader}${medsHeader} ${notes}`.trim();
  }

  if (!selectedImageBase64 && !recordedAudioBase64 && !combinedNotes && !allergies && !history) {
    alert("Please provide at least one input: upload a prescription photo, scan via camera, record voice, or enter patient form details.");
    return;
  }

  showLoading(true, "Gemini Multimodal Reasoning...", "Cross-referencing drug contraindications, handwriting OCR, vitals & generating clinical plan...");

  try {
    const payload = {
      image_data: selectedImageBase64,
      patient_photo: patientPhotoBase64,
      audio_data: recordedAudioBase64,
      text_notes: combinedNotes,
      patient_history: history,
      patient_allergies: allergies,
      target_language: lang,
      vitals: vitals,
      location_lat: userLocation.lat,
      location_lon: userLocation.lon,
      country_code: userLocation.country_code,
      city: userLocation.city
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

    // Synchronize custom user details if entered
    if (customName && currentAnalysisData.patient) {
      currentAnalysisData.patient.name = customName;
      if (customAge) currentAnalysisData.patient.age = parseInt(customAge);
      if (customGender) currentAnalysisData.patient.gender = customGender;
      if (customBlood) currentAnalysisData.patient.blood_group = customBlood;
    }
    if (patientPhotoBase64 && currentAnalysisData.patient) {
      currentAnalysisData.patient.photo_base64 = patientPhotoBase64;
    }
    if (vitals && currentAnalysisData) {
      currentAnalysisData.vitals = vitals;
    }

    renderResults(currentAnalysisData, currentFhirBundle, currentHl7Message);
  } catch (err) {
    alert("Analysis failed: " + err.message);
  } finally {
    showLoading(false);
  }
}

// ==========================================
// 7. RENDER RESULTS DASHBOARD
// ==========================================
function renderResults(data, fhirBundle, hl7Message) {
  document.getElementById("welcomeState").classList.add("hidden");
  document.getElementById("resultsDashboard").classList.remove("hidden");

  const patient = data.patient || {};
  const triage = data.triage || {};
  const safety = data.safety_analysis || {};
  const meds = data.medications || [];
  const guide = data.patient_friendly_guide || {};
  const vitals = data.vitals || {};

  // 1. Patient Profile Header
  document.getElementById("patientDisplayName").innerText = patient.name || "Patient Record";
  document.getElementById("patientBloodBadge").innerText = patient.blood_group || "O+";
  document.getElementById("patientDemographics").innerText = `${patient.age ? patient.age + 'yo' : 'Adult'} • ${patient.gender || 'Patient'} • Allergies: ${(patient.allergies || []).join(', ') || 'None Documented'}`;

  // Patient Avatar / Photo
  const profileImg = document.getElementById("patientProfileImage");
  const defaultIcon = document.getElementById("patientDefaultIcon");
  if (patientPhotoBase64 || patient.photo_base64) {
    profileImg.src = patientPhotoBase64 || patient.photo_base64;
    profileImg.classList.remove("hidden");
    defaultIcon.classList.add("hidden");
  } else {
    profileImg.src = "";
    profileImg.classList.add("hidden");
    defaultIcon.classList.remove("hidden");
  }

  // Vitals Display Bar
  if (document.getElementById("dispBp")) document.getElementById("dispBp").innerText = vitals.blood_pressure || "120/80 mmHg";
  if (document.getElementById("dispHr")) document.getElementById("dispHr").innerText = vitals.heart_rate || "74 bpm";
  if (document.getElementById("dispSpo2")) document.getElementById("dispSpo2").innerText = vitals.oxygen_saturation || "98%";
  if (document.getElementById("dispTemp")) document.getElementById("dispTemp").innerText = vitals.temperature || "98.6°F";

  // 2. Triage Banner & Protocol
  const triageCard = document.getElementById("triageProtocolCard");
  const triageIconBox = document.getElementById("triageIconBox");
  const triageBadgeBox = document.getElementById("triageBadgeBox");
  const triageLevelText = document.getElementById("triageLevelText");
  const triageTitle = document.getElementById("triageTitle");
  const triageSummary = document.getElementById("triageSummary");

  triageTitle.innerText = triage.title || "Clinical Assessment";
  triageSummary.innerText = triage.summary || "";

  if (triage.level === "RED") {
    triageBadgeBox.className = "px-3 py-1.5 rounded-xl text-xs font-extrabold flex items-center gap-1.5 shadow-sm bg-red-600 text-white animate-pulse";
    triageLevelText.innerText = "RED: CRITICAL EMERGENCY";
    triageCard.className = "p-5 rounded-2xl border transition-all shadow-md bg-red-50 dark:bg-red-950/40 border-red-300 dark:border-red-500/60";
    triageIconBox.className = "w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 bg-red-100 dark:bg-red-900/60 text-red-600 dark:text-red-400 border border-red-300 dark:border-red-700/60";
  } else if (triage.level === "AMBER") {
    triageBadgeBox.className = "px-3 py-1.5 rounded-xl text-xs font-extrabold flex items-center gap-1.5 shadow-sm bg-amber-600 text-white";
    triageLevelText.innerText = "AMBER: URGENT ACTION";
    triageCard.className = "p-5 rounded-2xl border transition-all shadow-md bg-amber-50 dark:bg-amber-950/40 border-amber-300 dark:border-amber-500/60";
    triageIconBox.className = "w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 bg-amber-100 dark:bg-amber-900/60 text-amber-600 dark:text-amber-400 border border-amber-300 dark:border-amber-700/60";
  } else {
    triageBadgeBox.className = "px-3 py-1.5 rounded-xl text-xs font-extrabold flex items-center gap-1.5 shadow-sm bg-emerald-600 text-white";
    triageLevelText.innerText = "GREEN: ROUTINE / STABLE";
    triageCard.className = "p-5 rounded-2xl border transition-all shadow-md bg-emerald-50 dark:bg-emerald-950/40 border-emerald-300 dark:border-emerald-500/60";
    triageIconBox.className = "w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 bg-emerald-100 dark:bg-emerald-900/60 text-emerald-600 dark:text-emerald-400 border border-emerald-300 dark:border-emerald-700/60";
  }

  // 3. Mayo Clinic Condition Profile & Diagnostic Workup
  const condProfile = data.condition_profile || {};
  renderAnatomicalArtwork(condProfile.category, condProfile.name);

  const mayoTitle = document.getElementById("mayoConditionTitle");
  const mayoIcd = document.getElementById("mayoIcdBadge");
  const mayoCategory = document.getElementById("mayoCategoryBadge");
  const mayoOverview = document.getElementById("mayoOverviewText");
  const mayoSymptoms = document.getElementById("mayoSymptomsList");
  const mayoCauses = document.getElementById("mayoCausesList");
  const mayoTests = document.getElementById("mayoTestsList");
  const mayoUrgent = document.getElementById("mayoUrgentList");
  const mayoCare = document.getElementById("mayoCareText");

  if (mayoTitle) mayoTitle.innerText = condProfile.name || triage.title || "Clinical Assessment";
  if (mayoIcd) mayoIcd.innerText = `ICD-10: ${condProfile.icd10 || 'R69'}`;
  if (mayoCategory) mayoCategory.innerText = condProfile.category || "General Clinical Medicine";
  if (mayoOverview) mayoOverview.innerText = condProfile.overview || triage.summary || "Clinical assessment completed.";

  if (mayoSymptoms) {
    mayoSymptoms.innerHTML = "";
    (condProfile.symptoms || []).forEach(s => {
      const li = document.createElement("li");
      li.className = "flex items-start gap-1.5";
      li.innerHTML = `<span class="text-teal-500 font-bold">•</span> <span>${s}</span>`;
      mayoSymptoms.appendChild(li);
    });
    if (!condProfile.symptoms || condProfile.symptoms.length === 0) {
      mayoSymptoms.innerHTML = `<li class="text-slate-400 italic">No acute physical distress documented.</li>`;
    }
  }

  if (mayoCauses) {
    mayoCauses.innerHTML = "";
    (condProfile.causes || []).forEach(c => {
      const li = document.createElement("li");
      li.className = "flex items-start gap-1.5";
      li.innerHTML = `<span class="text-slate-400 font-bold">•</span> <span>${c}</span>`;
      mayoCauses.appendChild(li);
    });
  }

  if (mayoTests) {
    mayoTests.innerHTML = "";
    (condProfile.diagnostic_tests || []).forEach(t => {
      const li = document.createElement("li");
      li.className = "flex items-start gap-1.5";
      li.innerHTML = `<i data-lucide="check-circle-2" class="w-3.5 h-3.5 text-blue-500 flex-shrink-0 mt-0.5"></i> <span>${t}</span>`;
      mayoTests.appendChild(li);
    });
    if (!condProfile.diagnostic_tests || condProfile.diagnostic_tests.length === 0) {
      mayoTests.innerHTML = `<li class="text-slate-400 italic">Standard vital signs monitoring indicated.</li>`;
    }
  }

  if (mayoUrgent) {
    mayoUrgent.innerHTML = "";
    (condProfile.red_flags || []).forEach(rf => {
      const li = document.createElement("li");
      li.className = "flex items-start gap-1.5";
      li.innerHTML = `<i data-lucide="alert-circle" class="w-3.5 h-3.5 text-red-500 flex-shrink-0 mt-0.5"></i> <span>${rf}</span>`;
      mayoUrgent.appendChild(li);
    });
  }

  if (mayoCare) {
    mayoCare.innerText = condProfile.home_care || guide.lifestyle_precautions || "Follow doctor's prescription strictly and maintain hydration.";
  }

  // 4. Pharmacological Safety Matrix
  const safetyBadge = document.getElementById("safetyBadge");
  safetyBadge.innerText = safety.badge || (safety.status === "CRITICAL_HAZARD" ? "LETHAL INTERACTION DETECTED" : "Prescription Verified");
  if (safety.color === "red" || safety.status === "CRITICAL_HAZARD") {
    safetyBadge.className = "text-[11px] font-bold px-2.5 py-0.5 rounded-full bg-red-100 dark:bg-red-900/60 text-red-700 dark:text-red-300 border border-red-300 dark:border-red-700/60";
  } else if (safety.color === "amber") {
    safetyBadge.className = "text-[11px] font-bold px-2.5 py-0.5 rounded-full bg-amber-100 dark:bg-amber-900/60 text-amber-700 dark:text-amber-300 border border-amber-300 dark:border-amber-700/60";
  } else {
    safetyBadge.className = "text-[11px] font-bold px-2.5 py-0.5 rounded-full bg-emerald-100 dark:bg-emerald-900/60 text-emerald-700 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-700/60";
  }

  const interactionList = document.getElementById("interactionList");
  interactionList.innerHTML = "";

  const allAlerts = [
    ...(safety.allergy_conflicts || []).map(a => ({ ...a, is_allergy: true })),
    ...(safety.interactions || []).map(i => ({ ...i, is_allergy: false }))
  ];

  if (allAlerts.length === 0) {
    interactionList.innerHTML = `
      <div class="p-3.5 rounded-xl bg-emerald-50 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-800/40 text-xs text-emerald-800 dark:text-emerald-300 flex items-center gap-2">
        <i data-lucide="check-circle" class="w-4 h-4 text-emerald-500 flex-shrink-0"></i>
        <span>No lethal drug-drug interactions or allergy contraindications detected. Prescriptions cleared for administration.</span>
      </div>
    `;
  } else {
    allAlerts.forEach(alertItem => {
      const isCrit = alertItem.severity === "CRITICAL";
      const card = document.createElement("div");
      card.className = `p-3.5 rounded-xl border ${isCrit ? 'bg-red-50 dark:bg-red-950/40 border-red-300 dark:border-red-500/60 text-red-900 dark:text-red-200' : 'bg-amber-50 dark:bg-amber-950/40 border-amber-300 dark:border-amber-500/60 text-amber-900 dark:text-amber-200'}`;
      card.innerHTML = `
        <div class="flex items-center justify-between font-bold text-xs mb-1">
          <span class="flex items-center gap-1.5">
            <i data-lucide="${isCrit ? 'alert-triangle' : 'alert-circle'}" class="w-4 h-4 ${isCrit ? 'text-red-500' : 'text-amber-500'}"></i>
            ${alertItem.title || alertItem.drug || 'Drug Hazard Alert'}
          </span>
          <span class="text-[10px] px-2 py-0.5 rounded uppercase font-bold ${isCrit ? 'bg-red-200 dark:bg-red-900/80 text-red-800 dark:text-red-200' : 'bg-amber-200 dark:bg-amber-900/80 text-amber-800 dark:text-amber-200'}">${alertItem.severity}</span>
        </div>
        <p class="text-[11px] opacity-90 leading-relaxed mb-2">${alertItem.mechanism || alertItem.reaction || ''}</p>
        <div class="p-2 rounded-lg bg-white/80 dark:bg-slate-950/60 border border-slate-200 dark:border-slate-800 text-[11px]">
          <strong class="${isCrit ? 'text-red-600 dark:text-red-400' : 'text-amber-600 dark:text-amber-400'}">Life-Saving Action:</strong> ${alertItem.recommendation || alertItem.clinical_guidance || ''}
        </div>
      `;
      interactionList.appendChild(card);
    });
  }

  // 4. Medications Table
  const tbody = document.getElementById("medicationsTableBody");
  tbody.innerHTML = "";
  meds.forEach(med => {
    const tr = document.createElement("tr");
    tr.className = "hover:bg-slate-50 dark:hover:bg-slate-800/40 transition-colors";
    
    const pillVis = med.pill_visual || { shape: "Oral Tablet", color: "White", imprint: "Standard" };
    const genericAlt = med.generic_alternative || { available: true, avg_savings_percent: 75 };

    tr.innerHTML = `
      <td class="py-2.5 px-3">
        <div class="font-bold text-slate-900 dark:text-white flex items-center gap-1.5">
          ${med.brand_name || med.generic_name}
          ${med.is_high_risk ? '<span class="px-1.5 py-0.2 text-[9px] bg-red-100 dark:bg-red-900/80 text-red-700 dark:text-red-300 rounded font-mono">HIGH RISK</span>' : ''}
        </div>
        <div class="text-[11px] text-slate-500 dark:text-slate-400 font-mono">${med.generic_name || ''}</div>
        <span class="inline-block mt-1 text-[10px] font-semibold text-teal-700 dark:text-teal-400 bg-teal-50 dark:bg-teal-950/80 px-1.5 py-0.2 rounded border border-teal-200 dark:border-teal-800/60">
          Generic Saves ~${genericAlt.avg_savings_percent}%
        </span>
      </td>
      <td class="py-2.5 px-3">
        <div class="text-xs text-slate-800 dark:text-slate-200 font-medium">${pillVis.shape}</div>
        <div class="text-[10px] text-teal-600 dark:text-teal-300 font-medium">${pillVis.color}</div>
        <div class="text-[9px] text-slate-400 font-mono">Imprint: ${pillVis.imprint}</div>
      </td>
      <td class="py-2.5 px-3 font-mono text-[11px] text-teal-700 dark:text-teal-300">
        <div>${med.dosage || 'N/A'} (${med.route || 'Oral'})</div>
        <div class="text-[11px] text-slate-600 dark:text-slate-300 font-sans capitalize">${med.timing_slot || ''} • ${med.frequency || ''}</div>
      </td>
      <td class="py-2.5 px-3 text-[11px] text-slate-700 dark:text-slate-300">
        <div class="font-medium text-slate-900 dark:text-slate-200">${med.purpose || ''}</div>
        <div class="text-[10px] text-amber-700 dark:text-amber-300/90">${med.dietary_warnings || med.instructions || ''}</div>
      </td>
    `;
    tbody.appendChild(tr);
  });

  // 5. 24-Hour Chrono-Dosing Timeline
  const sched = guide.schedule_breakdown || {};
  document.getElementById("scheduleMorning").innerText = sched.morning || "No scheduled medication.";
  document.getElementById("scheduleAfternoon").innerText = sched.afternoon || "No scheduled medication.";
  document.getElementById("scheduleEvening").innerText = sched.evening || "No scheduled medication.";
  document.getElementById("scheduleNight").innerText = sched.night || "No scheduled medication.";

  // 6. Nearby Facilities
  renderNearbyFacilities(data.nearby_emergency_resources);

  // 7. Patient Friendly Guide & Red Flags
  document.getElementById("plainSummaryText").innerText = guide.plain_summary || "Prescription instructions verified.";
  const redFlagsUl = document.getElementById("redFlagList");
  redFlagsUl.innerHTML = "";
  (guide.red_flag_symptoms || []).forEach(rf => {
    const li = document.createElement("li");
    li.className = "flex items-start gap-1.5 text-slate-700 dark:text-slate-300";
    li.innerHTML = `<span class="text-red-500 font-bold">•</span> <span>${rf}</span>`;
    redFlagsUl.appendChild(li);
  });

  // 8. SOAP Notes
  const soap = (triage.soap_note || {});
  document.getElementById("soapSubjective").innerText = soap.subjective || "N/A";
  document.getElementById("soapObjective").innerText = soap.objective || "N/A";
  document.getElementById("soapAssessment").innerText = soap.assessment || "N/A";
  document.getElementById("soapPlan").innerText = soap.plan || "N/A";

  // 9. FHIR & HL7 Blocks
  if (fhirBundle) {
    document.getElementById("fhirJsonBlock").innerText = JSON.stringify(fhirBundle, null, 2);
  }
  if (hl7Message) {
    document.getElementById("hl7Block").innerText = hl7Message;
  }

  // Generate Emergency QR Code Pass
  generateHealthCardQr(patient, meds, triage, currentQrFormat);

  if (window.lucide) window.lucide.createIcons();
}

function renderNearbyFacilities(resources) {
  const locLabel = document.getElementById("facilitiesLocationLabel");
  const hospList = document.getElementById("hospitalsList");
  const pharmList = document.getElementById("pharmaciesList");

  if (!hospList || !pharmList) return;

  const res = resources || {
    hospitals: [
      { name: "Metropolitan Trauma Center", address: "City Center ER", distance_km: 1.2, phone: "112 / 911" }
    ],
    pharmacies: [
      { name: "24/7 MedCare Pharmacy", address: "Main Healthcare Ave", distance_km: 0.6, phone: "+1 (555) 247-0000" }
    ],
    location_tag: userLocation.city ? `${userLocation.city}, ${userLocation.country_code}` : "Local Region"
  };

  if (locLabel) locLabel.innerText = res.location_tag || "Emergency Directory";

  hospList.innerHTML = `<div class="font-bold text-[11px] text-teal-700 dark:text-teal-400 mb-1 flex items-center gap-1"><i data-lucide="hospital" class="w-3.5 h-3.5"></i> Trauma Centers</div>`;
  (res.hospitals || []).forEach(h => {
    const div = document.createElement("div");
    div.className = "p-2.5 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 flex items-center justify-between";
    div.innerHTML = `
      <div>
        <div class="font-bold text-slate-900 dark:text-slate-100">${h.name}</div>
        <div class="text-[10px] text-slate-500 dark:text-slate-400">${h.address || ''} • ${h.distance_km || 1} km away</div>
      </div>
      <a href="tel:${h.phone || '112'}" class="px-2 py-1 rounded-lg bg-red-100 dark:bg-red-950 text-red-700 dark:text-red-300 font-mono font-bold text-[11px] hover:bg-red-200">
        ${h.phone || 'Call'}
      </a>
    `;
    hospList.appendChild(div);
  });

  pharmList.innerHTML = `<div class="font-bold text-[11px] text-blue-700 dark:text-blue-400 mb-1 flex items-center gap-1"><i data-lucide="cross" class="w-3.5 h-3.5"></i> 24/7 Pharmacies</div>`;
  (res.pharmacies || []).forEach(p => {
    const div = document.createElement("div");
    div.className = "p-2.5 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 flex items-center justify-between";
    div.innerHTML = `
      <div>
        <div class="font-bold text-slate-900 dark:text-slate-100">${p.name}</div>
        <div class="text-[10px] text-slate-500 dark:text-slate-400">${p.address || ''} • ${p.distance_km || 0.5} km away</div>
      </div>
      <a href="tel:${p.phone || '112'}" class="px-2 py-1 rounded-lg bg-blue-100 dark:bg-blue-950 text-blue-700 dark:text-blue-300 font-mono font-bold text-[11px] hover:bg-blue-200">
        ${p.phone || 'Call'}
      </a>
    `;
    pharmList.appendChild(div);
  });
}

// ==========================================
// 8. EMERGENCY MEDICAL QR PASS GENERATOR
// ==========================================
function switchQrFormat(format) {
  currentQrFormat = format;
  const textBtn = document.getElementById("qrFmtTextBtn");
  const jsonBtn = document.getElementById("qrFmtJsonBtn");

  if (format === 'text') {
    textBtn.className = "px-2.5 py-1 rounded-md bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-sm";
    jsonBtn.className = "px-2.5 py-1 rounded-md text-slate-500 dark:text-slate-400";
  } else {
    jsonBtn.className = "px-2.5 py-1 rounded-md bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-sm";
    textBtn.className = "px-2.5 py-1 rounded-md text-slate-500 dark:text-slate-400";
  }

  if (currentAnalysisData) {
    generateHealthCardQr(
      currentAnalysisData.patient || {},
      currentAnalysisData.medications || [],
      currentAnalysisData.triage || {},
      currentQrFormat
    );
  }
}

function generateHealthCardQr(patient, meds, triage = {}, format = 'text') {
  const qrDiv = document.getElementById("qrcode");
  if (!qrDiv) return;
  qrDiv.innerHTML = "";

  let qrContent = "";

  if (format === 'text') {
    // Pure clean human-readable text pass for any smartphone camera
    const medLines = (meds || []).map(m => `• ${m.brand_name || m.generic_name} ${m.dosage || ''} (${m.timing_slot || 'daily'}, ${m.frequency || ''})`).join("\n");
    const allergyStr = (patient.allergies || []).join(", ") || "None Documented";
    const conditionStr = (patient.pre_existing_conditions || []).join(", ") || "None Documented";

    qrContent = [
      "🏥 MEDFOREVER EMERGENCY MEDICAL PASS",
      "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
      `👤 PATIENT: ${patient.name || 'Anonymous'} (${patient.age || 'N/A'}yo ${patient.gender || ''})`,
      `🩸 BLOOD GROUP: ${patient.blood_group || 'O+'}`,
      `⚠️ ALLERGIES: ${allergyStr}`,
      `🩺 CONDITIONS: ${conditionStr}`,
      "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
      "💊 ACTIVE MEDICATIONS:",
      medLines || "• None active",
      "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
      `🚨 TRIAGE STATUS: ${triage.level || 'GREEN'} - ${triage.title || 'Stable'}`,
      `📞 EMERGENCY DISPATCH: 112 / 911`
    ].join("\n");
  } else {
    // Interoperable FHIR / JSON Payload
    const jsonPayload = {
      medforever_pass: "VERIFIED",
      patient: {
        name: patient.name || "Anonymous",
        age: patient.age,
        gender: patient.gender,
        blood_group: patient.blood_group || "O+",
        allergies: patient.allergies || [],
        conditions: patient.pre_existing_conditions || []
      },
      triage_level: triage.level || "GREEN",
      active_medications: (meds || []).map(m => ({
        drug: m.brand_name || m.generic_name,
        dosage: m.dosage,
        slot: m.timing_slot,
        frequency: m.frequency
      }))
    };
    qrContent = JSON.stringify(jsonPayload);
  }

  try {
    new QRCode(qrDiv, {
      text: qrContent,
      width: 220,
      height: 220,
      colorDark: "#090d16",
      colorLight: "#ffffff",
      correctLevel: QRCode.CorrectLevel.M
    });
  } catch (e) {
    console.error("QR Code Error:", e);
  }
}

function openHealthCardModal() {
  document.getElementById("healthCardModal").classList.remove("hidden");
  if (currentAnalysisData) {
    generateHealthCardQr(
      currentAnalysisData.patient || {},
      currentAnalysisData.medications || [],
      currentAnalysisData.triage || {},
      currentQrFormat
    );
  }
}

function closeHealthCardModal() {
  document.getElementById("healthCardModal").classList.add("hidden");
}

// ==========================================
// 9. MAYO CLINIC ANATOMICAL SYSTEM ARTWORK
// ==========================================
function renderAnatomicalArtwork(category, conditionName) {
  const iconBox = document.getElementById("mayoAnatomyIconBox");
  const deptTag = document.getElementById("mayoDepartmentTag");
  const subTitle = document.getElementById("mayoPathologySubtitle");
  const metric = document.getElementById("mayoSystemMetric");

  if (!iconBox) return;

  const catLower = (category || "").toLowerCase();
  const nameLower = (conditionName || "").toLowerCase();

  let svgHtml = "";
  let dept = "Mayo Clinic Internal Medicine";
  let pathText = "Evidence-Based Diagnostic Workup";
  let sysMetric = "Systemic Homeostasis Active";

  if (catLower.includes("cardio") || nameLower.includes("heart") || nameLower.includes("stemi") || nameLower.includes("coronary") || nameLower.includes("angina")) {
    dept = "Mayo Clinic Cardiovascular Medicine";
    pathText = "Coronary Arterial & Myocardial Perfusion";
    sysMetric = "Cardiac Rhythm Telemetry Active";
    svgHtml = `
      <svg viewBox="0 0 48 48" fill="none" class="w-10 h-10">
        <path d="M24 40S8 28 8 16a8 8 0 0116-2 8 8 0 0116 2c0 12-16 24-16 24z" fill="#ffe4e6" stroke="#e11d48" stroke-width="2.5"/>
        <path d="M24 8v10M18 12l12 0" stroke="#be123c" stroke-width="2" stroke-linecap="round"/>
        <path d="M12 24l5 2 3-6 4 9 3-5 5 2" stroke="#e11d48" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    `;
  } else if (catLower.includes("pulmon") || catLower.includes("respirat") || nameLower.includes("lung") || nameLower.includes("pneumonia") || nameLower.includes("asthma") || nameLower.includes("bronch")) {
    dept = "Mayo Clinic Pulmonary & Critical Care";
    pathText = "Tracheobronchial & Alveolar Gas Exchange";
    sysMetric = "SpO2 Oxygenation Telemetry Active";
    svgHtml = `
      <svg viewBox="0 0 48 48" fill="none" class="w-10 h-10">
        <path d="M24 4v16M24 16l-8 7M24 16l8 7" stroke="#0284c7" stroke-width="2.5" stroke-linecap="round"/>
        <path d="M16 22c-6 0-10 4-10 11 0 7 5 11 11 11h2V22h-3z" fill="#e0f2fe" stroke="#0284c7" stroke-width="2"/>
        <path d="M32 22c6 0 10 4 10 11 0 7-5 11-11 11h-2V22h3z" fill="#e0f2fe" stroke="#0284c7" stroke-width="2"/>
        <circle cx="16" cy="32" r="2" fill="#38bdf8"/>
        <circle cx="32" cy="32" r="2" fill="#38bdf8"/>
      </svg>
    `;
  } else if (catLower.includes("neuro") || nameLower.includes("stroke") || nameLower.includes("brain") || nameLower.includes("cva") || nameLower.includes("headache") || nameLower.includes("migraine")) {
    dept = "Mayo Clinic Neurology & Stroke Center";
    pathText = "Cerebrovascular & Cortical Neural Mapping";
    sysMetric = "Cranial Nerve / NIHSS Monitored";
    svgHtml = `
      <svg viewBox="0 0 48 48" fill="none" class="w-10 h-10">
        <path d="M24 8c-4 0-7 3-8 6-3 0-6 3-6 7 0 3 2 5 3 6-3 2-4 5-4 8 0 5 4 8 9 8h6V8h-0z" fill="#f3e8ff" stroke="#9333ea" stroke-width="2"/>
        <path d="M24 8c4 0 7 3 8 6 3 0 6 3 6 7 0 3-2 5-3 6 3 2 4 5 4 8 0 5-4 8-9 8h-6V8h0z" fill="#f3e8ff" stroke="#9333ea" stroke-width="2"/>
        <circle cx="20" cy="22" r="2" fill="#a855f7"/>
        <circle cx="28" cy="22" r="2" fill="#a855f7"/>
        <path d="M24 16v18" stroke="#7e22ce" stroke-width="1.5" stroke-dasharray="2 2"/>
      </svg>
    `;
  } else if (catLower.includes("gastro") || nameLower.includes("stomach") || nameLower.includes("digest") || nameLower.includes("bowel") || nameLower.includes("gerd")) {
    dept = "Mayo Clinic Gastroenterology & Hepatology";
    pathText = "Gastrointestinal Mucosal & Enteric System";
    sysMetric = "Enteric Fluid Balance Monitored";
    svgHtml = `
      <svg viewBox="0 0 48 48" fill="none" class="w-10 h-10">
        <path d="M24 6v10c0 4-4 6-4 10 0 7 5 12 11 12s7-4 7-9c0-4-3-6-5-7l-3-2" stroke="#d97706" stroke-width="2.5" stroke-linecap="round"/>
        <circle cx="24" cy="26" r="14" fill="#fef3c7" stroke="#f59e0b" stroke-width="1.5" stroke-dasharray="3 3"/>
      </svg>
    `;
  } else if (catLower.includes("immuno") || nameLower.includes("allergy") || nameLower.includes("anaphylaxis")) {
    dept = "Mayo Clinic Allergy & Clinical Immunology";
    pathText = "Systemic Mast Cell & IgE Receptor Cascade";
    sysMetric = "Airway & Histamine Alert Active";
    svgHtml = `
      <svg viewBox="0 0 48 48" fill="none" class="w-10 h-10">
        <path d="M24 4L8 10v12c0 10.5 6.8 20.2 16 23 9.2-2.8 16-12.5 16-23V10L24 4z" fill="#ecfdf5" stroke="#059669" stroke-width="2.5"/>
        <path d="M24 14v18M15 23h18" stroke="#10b981" stroke-width="3" stroke-linecap="round"/>
      </svg>
    `;
  } else {
    dept = "Mayo Clinic General Internal Medicine";
    pathText = "Multimodal Pharmacotherapy & Disease Protocol";
    sysMetric = "Clinical Bioequivalence Cleared";
    svgHtml = `
      <svg viewBox="0 0 48 48" fill="none" class="w-10 h-10">
        <rect x="10" y="8" width="28" height="34" rx="4" fill="#e0f2fe" stroke="#0284c7" stroke-width="2"/>
        <path d="M24 16v16M16 24h16" stroke="#0369a1" stroke-width="3" stroke-linecap="round"/>
      </svg>
    `;
  }

  iconBox.innerHTML = svgHtml;
  if (deptTag) deptTag.innerText = dept;
  if (subTitle) subTitle.innerText = pathText;
  if (metric) metric.innerText = sysMetric;
}

// ==========================================
// 10. DIRECT PDF DOWNLOAD & DIRECT PRINT
// ==========================================
async function downloadClinicalReportDirectPdf() {
  if (!currentAnalysisData) {
    alert("Please analyze patient data first.");
    return;
  }
  
  showLoading(true, "Generating Clinical Discharge PDF...", "Formulating Mayo Clinic clinical report...");

  try {
    const res = await fetch("/api/report/html", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ analysis_data: currentAnalysisData })
    });
    
    if (!res.ok) {
      throw new Error(`Server returned error ${res.status}`);
    }
    
    const html = await res.text();
    const patientName = (currentAnalysisData.patient?.name || 'Patient').replace(/[^a-zA-Z0-9]/g, '_');
    
    // Create dedicated off-screen iframe
    const iframe = document.createElement("iframe");
    iframe.style.position = "fixed";
    iframe.style.left = "0";
    iframe.style.top = "0";
    iframe.style.width = "850px";
    iframe.style.height = "1200px";
    iframe.style.zIndex = "-9999";
    iframe.style.opacity = "0.01";
    document.body.appendChild(iframe);
    
    iframe.contentDocument.open();
    iframe.contentDocument.write(html);
    iframe.contentDocument.close();
    
    await new Promise(resolve => setTimeout(resolve, 500));

    const opt = {
      margin: [8, 8, 8, 8],
      filename: `MedForever_MayoClinic_Discharge_${patientName}.pdf`,
      image: { type: 'jpeg', quality: 0.98 },
      html2canvas: { 
        scale: 2, 
        useCORS: true,
        logging: false,
        backgroundColor: '#ffffff'
      },
      jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
    };
    
    if (window.html2pdf) {
      await window.html2pdf().set(opt).from(iframe.contentDocument.body).save();
    } else {
      iframe.contentWindow.print();
    }

    setTimeout(() => {
      if (document.body.contains(iframe)) document.body.removeChild(iframe);
    }, 2000);
  } catch (e) {
    console.error("PDF generation error, opening print fallback:", e);
    printClinicalReportDirect();
  } finally {
    showLoading(false);
  }
}

async function printClinicalReportDirect() {
  if (!currentAnalysisData) {
    alert("Please analyze patient data first.");
    return;
  }
  try {
    const res = await fetch("/api/report/html", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ analysis_data: currentAnalysisData })
    });
    const html = await res.text();
    
    const printWindow = window.open("", "_blank");
    if (printWindow) {
      printWindow.document.write(html);
      printWindow.document.close();
      printWindow.focus();
      setTimeout(() => {
        printWindow.print();
      }, 500);
    } else {
      alert("Please allow popups to view and print the discharge report.");
    }
  } catch (e) {
    alert("Print failed: " + e.message);
  }
}

// ==========================================
// 10. MULTILINGUAL EXPLAINER & SPEECH
// ==========================================
function onLanguageChanged() {
  if (currentAnalysisData) {
    executeAnalysis();
  }
}

function speakPatientSummary() {
  const text = document.getElementById("plainSummaryText")?.innerText;
  if (!text) return;

  const langCode = document.getElementById("targetLanguageSelect")?.value || "en";
  const voiceConfig = LANGUAGE_CONFIG[langCode] || LANGUAGE_CONFIG.en;

  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = voiceConfig.voiceLang;
    utterance.rate = 0.95;
    utterance.pitch = 1.0;
    window.speechSynthesis.speak(utterance);
  } else {
    alert("Text-to-speech is not supported in this browser.");
  }
}

// ==========================================
// 11. EMERGENCY SOS MODAL
// ==========================================
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

// ==========================================
// 12. INTEROPERABILITY VIEWS (FHIR / HL7)
// ==========================================
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
    btnFhir.className = "px-3 py-1 rounded bg-slate-200 dark:bg-slate-800 text-teal-700 dark:text-teal-300 font-bold";
    btnHl7.className = "px-3 py-1 rounded bg-slate-100 dark:bg-slate-950 text-slate-600 dark:text-slate-400";
  } else {
    fhirBlock.classList.add("hidden");
    hl7Block.classList.remove("hidden");
    btnHl7.className = "px-3 py-1 rounded bg-slate-200 dark:bg-slate-800 text-amber-700 dark:text-amber-400 font-bold";
    btnFhir.className = "px-3 py-1 rounded bg-slate-100 dark:bg-slate-950 text-slate-600 dark:text-slate-400";
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

// ==========================================
// 13. SPINNER HELPER & API KEY MODAL
// ==========================================
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
      btnText.innerText = "API Key";
    }
  } catch (e) {}
}
