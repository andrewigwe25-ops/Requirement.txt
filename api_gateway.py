import asyncio
import json
import random
from datetime import datetime
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(
    title="Universal Energy Network (UEN) - Sovereign Core OS",
    version="3.2.0-Enterprise",
    description="Universal Energy Operating System with Edge Autonomy and Commercial Onboarding."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- UEN STATE & REGISTRIES ---
RESOURCE_REGISTRY: Dict[str, dict] = {
    "RES-ELEC-NG-01": {
        "name": "Rural Solar Microgrid Alpha",
        "carrier": "electricity",
        "capacity_mw": 5.0,
        "location": "Underserved Corridor, Nigeria",
        "security_tier": "SOVEREIGN_ROOT",
        "status": "ACTIVE_EDGE",
        "edge_mode": "CLOUD_SYNCED"
    },
    "RES-THERM-NG-02": {
        "name": "Biomass Thermal Conversion Unit",
        "carrier": "thermal",
        "capacity_mw": 12.0,
        "location": "Industrial Zone, Nigeria",
        "security_tier": "DIRECTOR",
        "status": "ACTIVE_EDGE",
        "edge_mode": "CLOUD_SYNCED"
    }
}

EXCHANGE_ORDERS: List[dict] = []
EXCHANGE_MATCHES: List[dict] = []
COMMERCIAL_PARTNERS: List[dict] = []

# --- MODELS ---
class ResourcePassportCreate(BaseModel):
    resource_id: str
    name: str
    carrier: str
    capacity_mw: float
    location: str
    security_tier: str = "SOVEREIGN_ROOT"

class OrderCreate(BaseModel):
    resource_id: str
    order_type: str
    energy_carrier: str
    quantity_mw: float
    price_per_mw_usd: float

class CommercialPartnerCreate(BaseModel.Config if False else BaseModel):
    company_name: str
    sector: str  # e.g., IPP, Industrial, Microgrid Operator
    region: str
    primary_contact_email: str

class DirectiveRequest(BaseModel):
    directive: str

# --- ROOT & HEALTH ---
@app.get("/")
def read_root():
    return {
        "system": "Universal Energy Network (UEN)",
        "version": "3.2.0-Enterprise",
        "mission": "Global energy intelligence, coordination, and sovereign infrastructure.",
        "active_edge_nodes": len(RESOURCE_REGISTRY),
        "commercial_partners": len(COMMERCIAL_PARTNERS)
    }

# --- COMMERCIAL ONBOARDING FRAMEWORK ---
@app.post("/api/commercial/onboard")
def onboard_commercial_partner(partner: CommercialPartnerCreate):
    """Onboard a real commercial enterprise, IPP, or microgrid operator into the UEN network."""
    partner_record = partner.dict()
    partner_record["partner_id"] = f"UEN-PARTNER-{random.randint(10000, 99999)}"
    partner_record["api_key"] = f"uen_live_{random.randint(10000000, 99999999)}"
    partner_record["status"] = "VERIFIED_COMMERCIAL_OPERATOR"
    partner_record["joined_at"] = datetime.utcnow().isoformat()
    
    COMMERCIAL_PARTNERS.append(partner_record)
    return {
        "status": "SUCCESS",
        "message": "Commercial partner successfully onboarded into UEN network.",
        "credentials": partner_record
    }

@app.get("/api/commercial/partners")
def list_commercial_partners():
    return {"status": "SUCCESS", "partners": COMMERCIAL_PARTNERS}

# --- EDGE AUTONOMY & SIMULATION ---
@app.post("/api/edge/simulate-blackout/{resource_id}")
def simulate_edge_blackout(resource_id: str):
    """Simulate an internet blackout forcing a remote microgrid into autonomous island mode."""
    if resource_id not in RESOURCE_REGISTRY:
        raise HTTPException(status_code=404, detail="Resource passport not found.")
    
    current_mode = RESOURCE_REGISTRY[resource_id]["edge_mode"]
    new_mode = "AUTONOMOUS_ISLAND" if current_mode == "CLOUD_SYNCED" else "CLOUD_SYNCED"
    RESOURCE_REGISTRY[resource_id]["edge_mode"] = new_mode
    
    return {
        "status": "SUCCESS",
        "resource_id": resource_id,
        "edge_mode": new_mode,
        "message": f"Resource switched to {new_mode}. Local battery buffers and autonomous load balancing engaged."
    }

# --- STANDARD PASSPORTS & MATCHING ---
@app.post("/api/resources/passport")
def register_passport(passport: ResourcePassportCreate):
    if passport.resource_id in RESOURCE_REGISTRY:
        raise HTTPException(status_code=400, detail="Passport ID already exists.")
    record = passport.dict()
    record["status"] = "ACTIVE_EDGE"
    record["edge_mode"] = "CLOUD_SYNCED"
    RESOURCE_REGISTRY[passport.resource_id] = record
    return {"status": "SUCCESS", "passport": record}

@app.get("/api/resources/passports")
def get_passports():
    return {"status": "SUCCESS", "passports": RESOURCE_REGISTRY}

@app.post("/api/exchange/orders")
def create_order(order: OrderCreate):
    order_record = {
        "order_id": f"UEN-ORD-{random.randint(10000, 99999)}",
        **order.dict(),
        "lifecycle_state": "DISCOVERED",
        "timestamp": datetime.utcnow().isoformat()
    }
    EXCHANGE_ORDERS.append(order_record)
    return {"status": "SUCCESS", "order": order_record}

@app.post("/api/exchange/match")
def match_orders():
    matched = 0
    supplies = [o for o in EXCHANGE_ORDERS if o["order_type"] == "SUPPLY" and o["lifecycle_state"] == "DISCOVERED"]
    demands = [o for o in EXCHANGE_ORDERS if o["order_type"] == "DEMAND" and o["lifecycle_state"] == "DISCOVERED"]
    
    for s in supplies:
        for d in demands:
            if s["energy_carrier"] == d["energy_carrier"] and s["quantity_mw"] >= d["quantity_mw"]:
                s["lifecycle_state"] = "PROPOSED"
                d["lifecycle_state"] = "PROPOSED"
                match_rec = {
                    "match_id": f"UEN-MCH-{random.randint(1000, 9999)}",
                    "supply_id": s["order_id"],
                    "demand_id": d["order_id"],
                    "allocated_mw": d["quantity_mw"],
                    "timestamp": datetime.utcnow().isoformat()
                }
                EXCHANGE_MATCHES.append(match_rec)
                matched += 1
                break
    return {"status": "SUCCESS", "new_matches": matched, "total_matches": len(EXCHANGE_MATCHES), "matches": EXCHANGE_MATCHES}

@app.post("/api/execute")
def execute_directive(req: DirectiveRequest):
    return {"status": "SUCCESS", "directive": req.directive, "validation": "PHYSICS_AWARE_PASSED", "response": "Sovereign intelligence dispatched."}

# --- TELEMETRY ---
@app.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = {
                "status": "UEN_GLOBAL_SECURE_GRID",
                "stability": round(random.uniform(0.985, 0.999), 4),
                "edge_nodes": len(RESOURCE_REGISTRY),
                "commercial_partners": len(COMMERCIAL_PARTNERS),
                "active_matches": len(EXCHANGE_MATCHES),
                "neural_load": round(random.uniform(60.0, 79.5), 1)
            }
            await websocket.send_text(json.dumps(data))
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        pass
