from fastapi import FastAPI, HTTPException
from confluent_kafka import Producer
import json
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="Order Processing API", version="1.0.0")

# Pydantic models
class OrderRequest(BaseModel):
    user_id: str
    product_id: str
    quantity: int
    price: float

class OrderResponse(BaseModel):
    order_id: str
    status: str
    message: str

class UserEvent(BaseModel):
    user_id: str
    action: str
    details: Optional[dict] = None

# Kafka producer
def get_kafka_producer():
    return Producer({'bootstrap.servers': 'kafka:29092'})

@app.get("/")
def read_root():
    return {"message": "Order Processing API", "status": "running"}

@app.post("/orders", response_model=OrderResponse)
async def create_order(order: OrderRequest):
    """Create a new order and queue it for processing"""
    try:
        producer = get_kafka_producer()
        
        # Generate order ID
        order_id = str(uuid.uuid4())
        
        # Create order event
        order_event = {
            "order_id": order_id,
            "user_id": order.user_id,
            "product_id": order.product_id,
            "quantity": order.quantity,
            "price": order.price,
            "total": order.quantity * order.price,
            "timestamp": datetime.now().isoformat(),
            "status": "pending"
        }
        
        # Send to Kafka with key
        producer.produce(
          topic='orders',
          key=order_id,
          value=json.dumps(order_event).encode('utf-8')
        )
        producer.flush()
        
        return OrderResponse(
            order_id=order_id,
            status="queued",
            message="Order has been queued for processing"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to queue order: {str(e)}")

@app.post("/events")
async def track_user_event(event: UserEvent):
    """Track user events (login, logout, page views, etc.)"""
    try:
        producer = get_kafka_producer()
        
        # Create user event
        event_id = str(uuid.uuid4())
        # .dict() is deprecated in Pydantic v2, use model_dump()
        payload = event.model_dump()
        payload["event_id"] = event_id
        payload["timestamp"] = datetime.now().isoformat()
        
        # Send to Kafka with key
        producer.produce(
            topic="user-events",
            key=event_id,
            value=json.dumps(payload).encode("utf-8")
        )
        producer.flush()
        # confluent_kafka.Producer does not need explicit close()
        
        return {"status": "success", "message": "Event tracked successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to track event: {e}")

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

def main():
    """Main function to run the FastAPI application"""
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )

if __name__ == "__main__":
    main()