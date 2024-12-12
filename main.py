from fastapi import FastAPI, HTTPException,WebSocket, WebSocketDisconnect
from database import get_trucks_collection,get_orders_collection
from models import TruckStatus,Order,Truck 
from bson import ObjectId
from bson.errors import InvalidId
from typing import List

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8100"],
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"], 
)

trucks_collection = get_trucks_collection()
orders_collection = get_orders_collection()

def truck_serializer(truck):
    truck["_id"] = str(truck["_id"])
    return truck

def order_serializer(order):
    order["_id"] = str(order["_id"])
    return order

@app.get("/")
def read_root():
    return {"message": "Warehouse API is running"}

@app.post("/order")
async def add_order(order: Order):
    result = orders_collection.insert_one(order.dict())
    return {"id": str(result.inserted_id)}

@app.get("/orders")
async def get_orders():
    orders = list(orders_collection.find())
    return {"orders": [order_serializer(order) for order in orders]}

@app.get('/trucks')
async def get_trucks():
    trucks = list(trucks_collection.find())
    return {"trucks": [truck_serializer(truck) for truck in trucks]}

@app.post("/truck")
async def add_truck(truck: Truck):
    result = trucks_collection.insert_one(truck.dict())
    return {"id": str(result.inserted_id)}

# WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()
@app.put("/truck/{truck_id}")
async def update_truck_status(truck_id: str, status: TruckStatus):
    try:
        result = trucks_collection.update_one(
            {"_id": ObjectId(truck_id)},
            {"$set": status.dict()}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Truck not found")
        return {"message": "Truck status updated"}
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid Truck ID")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            await manager.broadcast(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
