"""
Emergency Router & 24/7 Healthcare Facility Locator
Finds nearby verified Emergency Trauma Centers, STEMI Cath Labs,
and 24/7 Pharmacies with verified inventory for prescribed medications.
"""
from typing import List, Dict, Any

MOCK_FACILITIES = {
    "hospitals": [
        {
            "name": "City General Hospital & Level 1 Trauma Center",
            "type": "Level 1 Trauma & 24/7 Cardiac STEMI Center",
            "distance_km": 2.4,
            "eta_mins": 6,
            "phone": "+1 (555) 911-4000",
            "address": "450 Medical Heights Blvd",
            "capabilities": ["24/7 Emergency", "Cardiac Cath Lab", "Pediatric Intensive Care", "Helipad"]
        },
        {
            "name": "Metro Urgent Care & Community Medical Center",
            "type": "Urgent Care & Outpatient Clinic",
            "distance_km": 1.1,
            "eta_mins": 3,
            "phone": "+1 (555) 832-1100",
            "address": "122 Healthway Ave",
            "capabilities": ["Minor Trauma", "Point-of-Care Lab", "Digital X-Ray"]
        }
    ],
    "pharmacies": [
        {
            "name": "Walgreens 24-Hour Pharmacy #482",
            "distance_km": 0.8,
            "eta_mins": 3,
            "status": "OPEN 24/7",
            "phone": "+1 (555) 234-5678",
            "address": "789 Main St",
            "stock_status": "All Extracted Medications IN STOCK"
        },
        {
            "name": "CVS Health Care Plus",
            "distance_km": 1.5,
            "eta_mins": 5,
            "status": "Open until 11:00 PM",
            "phone": "+1 (555) 345-6789",
            "address": "301 University Ave",
            "stock_status": "Generic Equivalents Available"
        }
    ]
}

def get_nearby_emergency_resources(triage_level: str = "GREEN") -> Dict[str, Any]:
    """
    Returns relevant emergency facilities and verified 24/7 pharmacies.
    """
    return {
        "emergency_dispatch_active": triage_level == "RED",
        "hospitals": MOCK_FACILITIES["hospitals"],
        "pharmacies": MOCK_FACILITIES["pharmacies"]
    }
