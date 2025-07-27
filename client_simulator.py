import requests
import time
import random
import json
from datetime import datetime

API_BASE_URL = "http://localhost:5699"

def simulate_customer_orders():
    """Simulate customers placing orders"""
    
    users = ['alice', 'bob', 'charlie', 'diana', 'eve', 'frank', 'grace']
    products = [
        {'id': 'laptop', 'price': 999.99},
        {'id': 'mouse', 'price': 29.99},
        {'id': 'keyboard', 'price': 79.99},
        {'id': 'monitor', 'price': 299.99},
        {'id': 'headphones', 'price': 149.99}
    ]
    
    print("🛒 Starting customer order simulation...")
    print(f"API endpoint: {API_BASE_URL}")
    print("-" * 50)
    
    try:
        for i in range(20):  # Simulate 20 orders
            # Random customer and product
            user = random.choice(users)
            product = random.choice(products)
            quantity = random.randint(1, 3)
            
            # Create order payload
            order_data = {
                "user_id": user,
                "product_id": product['id'],
                "quantity": quantity,
                "price": product['price']
            }
            
            print(f"🛍️  Customer {user} ordering {quantity}x {product['id']} (${product['price']})")
            
            # Send POST request to API
            try:
                response = requests.post(f"{API_BASE_URL}/orders", json=order_data)
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Order queued: {result['order_id']}")
                else:
                    print(f"❌ Failed: {response.status_code} - {response.text}")
                    
            except requests.exceptions.ConnectionError:
                print("❌ Cannot connect to API. Is it running?")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
            
            # Random delay between orders
            time.sleep(random.uniform(0.5, 2.0))
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping simulation...")

def simulate_user_events():
    """Simulate user activity events"""
    
    users = ['alice', 'bob', 'charlie', 'diana', 'eve']
    actions = ['login', 'logout', 'view_product', 'add_to_cart', 'search']
    
    print("👥 Simulating user events...")
    
    try:
        for i in range(10):
            user = random.choice(users)
            action = random.choice(actions)
            
            event_data = {
                "user_id": user,
                "action": action,
                "details": {
                    "timestamp": datetime.now().isoformat(),
                    "session_id": f"sess_{random.randint(1000, 9999)}"
                }
            }
            
            print(f"📊 User {user} -> {action}")
            
            try:
                response = requests.post(f"{API_BASE_URL}/events", json=event_data)
                if response.status_code == 200:
                    print("✅ Event tracked")
                else:
                    print(f"❌ Failed: {response.status_code}")
            except Exception as e:
                print(f"❌ Error: {e}")
            
            time.sleep(random.uniform(0.3, 1.0))
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping event simulation...")

def check_api_health():
    """Check if the API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API is healthy and running")
            return True
        else:
            print(f"❌ API unhealthy: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure Docker services are running.")
        return False
    except Exception as e:
        print(f"❌ Error checking API: {e}")
        return False

if __name__ == "__main__":
    print("🚀 API Client Simulator")
    print("=" * 50)
    
    # Check API health first
    if not check_api_health():
        print("\n💡 To start the services, run: docker compose up -d")
        exit(1)
    
    print("\nChoose simulation:")
    print("1. Simulate customer orders")
    print("2. Simulate user events")
    print("3. Both")
    
    choice = input("Enter choice (1-3): ")
    
    if choice == "1":
        simulate_customer_orders()
    elif choice == "2":
        simulate_user_events()
    elif choice == "3":
        simulate_user_events()
        time.sleep(1)
        simulate_customer_orders()
    else:
        print("Invalid choice")