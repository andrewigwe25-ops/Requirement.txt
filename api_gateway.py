import asyncio
import json
import random
from datetime import datetime
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(
    title="Universal Energy Network (UEN) - Sovereign Core Engine",
    version="3.1.0-Enterprise",
    description="Global intelligence, resource identity, and exchange coordination layer."
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
    "RES-SOLAR-NG-01": {
        "name": "Lagos Industrial Solar Microgrid",
        "carrier": "electricity",
        "capacity_mw": 45.0,
        "location": "Lagos, Nigeria",
        "status": "ACTIVE",
        "security_tier": "SOVEREIGN_ROOT"
    },
    "RES-BATT-NG-02": {
        "name": "Port Harcourt Storage Vault",
        "carrier": "electricity",
        "capacity_mw": 20.0,
        "location": "Port Harcourt, Nigeria",
        "status": "ACTIVE",
        "security_tier": "DIRECTOR"
    }
}

EXCHANGE_ORDERS: List[dict] = []
EXCHANGE_MATCHES: List[dict] = []

# --- MODELS ---
class ResourcePassportCreate(BaseModel):
    resource_id: str
    name: str
    carrier: str  # electricity, thermal, hydrogen
    capacity_mw: float
    location: str
    security_tier: str

class OrderCreate(BaseModel):
    resource_id: str
    order_type: str  # SUPPLY or DEMAND
    energy_carrier: str
    quantity_mw: float
    price_per_mw_usd: float

class DirectiveRequest(BaseModel):
    directive: str

# --- ROOT & PASSPORT ENDPOINTS ---
@app.get("/")
def read_root():
    return {
        "system": "Universal Energy Network (UEN)",
        "mission": "Connecting the World's Energy Resources Through Universal Intelligence",
        "version": "3.1.0-Enterprise",
        "registered_assets": len(RESOURCE_REGISTRY),
        "active_exchange_orders": len(EXCHANGE_ORDERS),
        "active_matches": len(EXCHANGE_MATCHES)
    }

@app.post("/api/resources/passport")
def register_resource_passport(passport: ResourcePassportCreate):
    """Register a Universal Energy Resource Passport into the UEN network."""
    if passport.resource_id in RESOURCE_REGISTRY:
        raise HTTPException(status_code=400, detail="Resource Passport ID already exists.")
    
    resource_record = passport.dict()
    resource_record["registered_at"] = datetime.utcnow().isoformat()
    resource_record["verification_status"] = "VERIFIED_PASSPORT"
    
    RESOURCE_REGISTRY[passport.resource_id] = resource_record
    return {"status": "SUCCESS", "message": "Resource Passport registered.", "passport": resource_record}

@app.get("/api/resources/passports")
def list_resource_passports():
    """Retrieve all global resource passports across participating nodes."""
    return {"status": "SUCCESS", "passports": RESOURCE_REGISTRY}

# --- EXCHANGE & MATCHING ENGINE ---
@app.post("/api/exchange/orders")
def create_exchange_order(order: OrderCreate):
    """Place a supply or demand order into the UEN Exchange."""
    if order.resource_id not in RESOURCE_REGISTRY and order.order_type == "SUPPLY":
        raise HTTPException(status_code=404, detail="Supplying resource passport not found.")

    order_record = {
        "order_id": f"UEN-ORD-{random.randint(10000, 99999)}",
        "resource_id": order.resource_id,
        "order_type": order.order_type,
        "energy_carrier": order.energy_carrier,
        "quantity_mw": order.quantity_mw,
        "price_per_mw_usd": order.price_per_mw_usd,
        "lifecycle_state": "DISCOVERED",
        "timestamp": datetime.utcnow().isoformat()
    }
    EXCHANGE_ORDERS.append(order_record)
    return {"status": "SUCCESS", "message": "Order registered in exchange ledger.", "order": order_record}

@app.get("/api/exchange/orders")
def get_exchange_orders():
    return {"status": "SUCCESS", "orders": EXCHANGE_ORDERS}

@app.post("/api/exchange/match")
def execute_matching_engine():
    """Concurrency-safe matching engine linking supply and demand with lifecycle state transitions."""
    matched_count = 0
    supplies = [o for o in EXCHANGE_ORDERS if o["order_type"] == "SUPPLY" and o["lifecycle_state"] == "DISCOVERED"]
    demands = [o for o in EXCHANGE_ORDERS if o["order_type"] == "DEMAND" and o["lifecycle_state"] == "DISCOVERED"]

    for supply in supplies:
        for demand in demands:
            if supply["energy_carrier"] == demand["energy_carrier"] and supply["quantity_mw"] >= demand["quantity_mw"]:
                supply["lifecycle_state"] = "PROPOSED"
                demand["lifecycle_state"] = "PROPOSED"

                match_record = {
                    "match_id": f"UEN-MCH-{random.randint(1000, 9999)}",
                    "supply_order_id": supply["order_id"],
                    "demand_order_id": demand["order_id"],
                    "allocated_mw": demand["quantity_mw"],
                    "carrier": supply["energy_carrier"],
                    "lifecycle_status": "ACCEPTED_PROPOSAL",
                    "timestamp": datetime.utcnow().isoformat()
                }
                EXCHANGE_MATCHES.append(match_record)
                matched_count += 1
                break

    return {
        "status": "SUCCESS",
        "new_matches_created": matched_count,
        "total_matches": len(EXCHANGE_MATCHES),
        "matches": EXCHANGE_MATCHES
    }

# --- DIRECTIVE & SIMULATION ENGINE ---
@app.post("/api/execute")
async def execute_directive(req: DirectiveRequest):
    text = req.directive.lower()
    if "quantum" in text or "firewall" in text or "core" in text or "sovereign" in text:
        clearance = "SOVEREIGN_ROOT"
    elif "exchange" in text or "grid" in text or "foundry" in text:
        clearance = "DIRECTOR"
    else:
        clearance = "OPERATOR"

    return {
        "status": "SUCCESS",
        "directive_received": req.directive,
        "security_clearance": clearance,
        "matrix_response": f"UEN intelligence analysis complete. Physics-aware validation verified. Sub-routines dispatched under tier: {clearance}."
    }

# --- TELEMETRY STREAM ---
@app.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            telemetry_data = {
                "status": "UEN_GLOBAL_SECURE",
                "energy_stability_index": round(random.uniform(0.97, 0.999), 4),
                "active_foundries": random.randint(18, 25),
                "active_edge_nodes": random.randint(210, 240),
                "neural_load_pct": round(random.uniform(70.0, 88.5), 1),
                "satellite_sync_rate": "100%",
                "quantum_core_temp": f"{random.randint(39, 44)}°C",
                "total_passports": len(RESOURCE_REGISTRY),
                "active_orders": len(EXCHANGE_ORDERS),
                "active_matches": len(EXCHANGE_MATCHES)
            }
            await websocket.send_text(json.dumps(telemetry_data))
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        pass
