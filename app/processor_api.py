import logging
from fastapi import FastAPI, HTTPException
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable
import json
import time
import random
import threading
import asyncio
from datetime import datetime
import uvicorn
from contextlib import asynccontextmanager

# Configure logging to integrate with Uvicorn
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("processor_api")

# Global state
processor_state = {
    "running": False,
    "processed_count": 0,
    "failed_count": 0,
    "last_processed": None,
    "thread": None,
    "connection_error": None
}

class ProcessorStats:
    def __init__(self):
        self.processed_count = 0
        self.failed_count = 0
        self.recent_orders = []

stats = ProcessorStats()

def create_order_consumer():
    """Create Kafka consumer subscribed to both topics."""
    consumer = KafkaConsumer(
        bootstrap_servers=['kafka:29092'],
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        group_id='order-processing-group',
        auto_offset_reset='earliest'
    )
    # subscribe() mutates and returns None, so call it, then return the consumer
    consumer.subscribe(['orders', 'user-events'])
    return consumer

def process_orders_background():
    """Background thread function to process incoming Kafka messages."""
    try:
        consumer = create_order_consumer()
    except Exception:
        processor_state["running"] = False
        return

    logger.info("🏭 Starting order processing service...")
    try:
        for message in consumer:
            if not processor_state["running"]:
                logger.info("🛑 Processor stopped, exiting loop")
                break

            # Dispatch by topic
            if message.topic == "orders":
                try:
                    order = message.value
                    logger.info(f"📦 Processing order: {order['order_id']}")

                    processing_time = random.uniform(1, 3)
                    time.sleep(processing_time)

                    success = random.random() < 0.9
                    if success:
                        processor_state["processed_count"] += 1
                        stats.processed_count += 1
                        logger.info(f"✅ Order {order['order_id']} processed successfully!")
                    else:
                        processor_state["failed_count"] += 1
                        stats.failed_count += 1
                        logger.warning(f"❌ Order {order['order_id']} failed to process")

                    order_info = {
                        "order_id": order['order_id'],
                        "user_id": order['user_id'],
                        "product_id": order['product_id'],
                        "total": order['total'],
                        "processed_at": datetime.now().isoformat(),
                        "success": success,
                        "processing_time": round(processing_time, 2)
                    }
                    stats.recent_orders.append(order_info)
                    if len(stats.recent_orders) > 50:
                        stats.recent_orders.pop(0)

                    processor_state["last_processed"] = datetime.now().isoformat()

                except KeyError as ke:
                    logger.warning(f"❌ Malformed order message: missing {ke}")
                    continue

            elif message.topic == "user-events":
                try:
                    event = message.value
                    logger.info(f"📰 Processing user-event: {event}")
                    # … votre logique de traitement d’user-event …
                except Exception as ue:
                    logger.exception(f"❌ Error in user-event handler: {ue}")
                continue
            else:
                logger.debug(f"Ignoring topic {message.topic}")
                continue

    except Exception as e:
        logger.exception(f"❌ Error in processor: {e}")
    finally:
        logger.info("🔌 Closing Kafka consumer…")
        consumer.close()
        processor_state["running"] = False
        logger.info("🛑 Order processor stopped")

def auto_start_processor():
    """Start the processor thread if not already running."""
    if processor_state["running"]:
        logger.info("⚠️ Processor already running, skipping start")
        return

    logger.info("🚀 Starting order processor...")
    processor_state["running"] = True
    thread = threading.Thread(target=process_orders_background, daemon=True)
    processor_state["thread"] = thread
    thread.start()
    logger.info("✅ Order processor thread started!")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: wait for Kafka and start processor
    logger.info("📡 Waiting for Kafka to be ready...")
    await asyncio.sleep(5)
    auto_start_processor()
    try:
        yield
    finally:
        # Shutdown: stop processor
        logger.info("🛑 Shutting down processor...")
        processor_state["running"] = False

# FastAPI app initialization
app = FastAPI(title="Order Processor API", version="1.0.0", lifespan=lifespan)

@app.get("/")
def read_root():
    return {
        "message": "Order Processor API",
        "status": "running",
        "auto_processing": processor_state["running"],
        "connection_error": processor_state["connection_error"]
    }

@app.post("/processor/start")
def start_processor():
    if processor_state["running"]:
        return {"status": "already_running", "message": "Processor is already running"}
    auto_start_processor()
    return {"status": "started", "message": "Order processor started"}

@app.post("/processor/stop")
def stop_processor():
    if not processor_state["running"]:
        return {"status": "not_running", "message": "Processor is not running"}
    processor_state["running"] = False
    return {"status": "stopped", "message": "Order processor stopped"}

@app.get("/processor/status")
def get_processor_status():
    total = processor_state["processed_count"] + processor_state["failed_count"]
    success_rate = round((processor_state["processed_count"] / max(1, total)) * 100, 2)
    return {
        "running": processor_state["running"],
        "processed_count": processor_state["processed_count"],
        "failed_count": processor_state["failed_count"],
        "success_rate": success_rate,
        "last_processed": processor_state["last_processed"],
        "connection_error": processor_state["connection_error"]
    }

@app.get("/processor/orders")
def get_processed_orders():
    return {"total_processed": len(stats.recent_orders), "orders": stats.recent_orders}

@app.get("/processor/orders/{order_id}")
def get_order_details(order_id: str):
    order = next((o for o in stats.recent_orders if o["order_id"] == order_id), None)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.delete("/processor/reset")
def reset_stats():
    processor_state["processed_count"] = 0
    processor_state["failed_count"] = 0
    processor_state["last_processed"] = None
    stats.recent_orders.clear()
    return {"status": "reset", "message": "Statistics reset"}

if __name__ == "__main__":
    # Run via script: disables in-process reload so lifespan fires immediately
    uvicorn.run(
        "processor_api:app",
        host="0.0.0.0",
        port=8001,
        reload=False,
        # Optional: uncomment to disable stdout/stderr capture
        # log_config=None
    )
