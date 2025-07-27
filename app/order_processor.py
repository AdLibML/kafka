from kafka import KafkaConsumer
import json
import time
import random

def create_order_consumer():
    return KafkaConsumer(
        'orders',
        bootstrap_servers=['kafka:29092'],
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        group_id='order-processing-group',
        auto_offset_reset='earliest'
    )

def process_orders():
    consumer = create_order_consumer()
    
    print("🏭 Starting order processing service...")
    
    try:
        for message in consumer:
            order = message.value
            print(f"📦 Processing order: {order['order_id']}")
            
            # Simulate order processing time
            processing_time = random.uniform(1, 3)
            time.sleep(processing_time)
            
            # Simulate success/failure (90% success rate)
            if random.random() < 0.9:
                print(f"✅ Order {order['order_id']} processed successfully!")
                print(f"   User: {order['user_id']}")
                print(f"   Product: {order['product_id']}")
                print(f"   Total: ${order['total']:.2f}")
            else:
                print(f"❌ Order {order['order_id']} failed to process")
            
            print("-" * 50)
                
    except KeyboardInterrupt:
        print("🛑 Stopping order processor...")
    finally:
        consumer.close()

def main():
    process_orders()

if __name__ == "__main__":
    main()