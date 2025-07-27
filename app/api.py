from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from kafka import KafkaProducer
import json
import uuid
from datetime import datetime
from typing import Optional
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
    return KafkaProducer(
        bootstrap_servers=['kafka:29092'],
        key_serializer=lambda k: k.encode('utf-8'),
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

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
        producer.send('orders', key=order_id, value=order_event)
        producer.flush()
        producer.close()
        
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
        user_event = {
            "event_id": event_id,
            "user_id": event.user_id,
            "action": event.action,
            "details": event.details or {},
            "timestamp": datetime.now().isoformat()
        }
        
        # Send to Kafka with key
        producer.send('user-events', key=event_id, value=user_event)
        producer.flush()
        producer.close()
        
        return {"status": "success", "message": "Event tracked successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to track event: {str(e)}")

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