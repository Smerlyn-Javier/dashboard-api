from pydantic import BaseModel
from typing import List, Optional

class Point(BaseModel):
    lat: float
    lng: float
    
class Order(BaseModel):
    destination: str
    customer: str
    orderId: str
    origin: str
    status: str
    route: List[Point]
    
class TruckStatus(BaseModel):
    truck_id: str
    status: str
    
class Truck(BaseModel):
    driver: str
    location: str
    status: str 