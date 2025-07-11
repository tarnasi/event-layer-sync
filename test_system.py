#!/usr/bin/env python3
"""
Test script to demonstrate the event-driven logistic system
This script shows how to interact with the API and see events being published
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

def test_api():
    print("🚀 Testing Event-Driven Logistic System")
    print("=" * 50)
    
    # Test headers with operation-name
    headers = {
        "operation-name": "test-warehouse-creation",
        "Content-Type": "application/json"
    }
    
    # 1. Test ping endpoint
    print("\n1. Testing ping endpoint...")
    response = requests.get(f"{BASE_URL}/ping", headers=headers)
    print(f"Response: {response.json()}")
    
    # 2. Create a warehouse
    print("\n2. Creating a warehouse...")
    warehouse_data = {
        "name": "Main Warehouse",
        "location": "New York, NY"
    }
    
    headers["operation-name"] = "create-main-warehouse"
    response = requests.post(f"{BASE_URL}/warehouses/", 
                           json=warehouse_data, 
                           headers=headers)
    
    if response.status_code == 200:
        warehouse = response.json()
        warehouse_id = warehouse["id"]
        print(f"✅ Warehouse created: {warehouse}")
    else:
        print(f"❌ Failed to create warehouse: {response.text}")
        return
    
    # 3. Create a shipment
    print("\n3. Creating a shipment...")
    shipment_data = {
        "tracking_number": "TRK001",
        "origin": "New York, NY",
        "destination": "Los Angeles, CA",
        "weight": 25.5,
        "warehouse_id": warehouse_id
    }
    
    headers["operation-name"] = "create-shipment-trk001"
    response = requests.post(f"{BASE_URL}/shipments/", 
                           json=shipment_data, 
                           headers=headers)
    
    if response.status_code == 200:
        shipment = response.json()
        shipment_id = shipment["id"]
        print(f"✅ Shipment created: {shipment}")
    else:
        print(f"❌ Failed to create shipment: {response.text}")
        return
    
    # 4. Update shipment status
    print("\n4. Updating shipment status...")
    update_data = {
        "status": "in_transit"
    }
    
    headers["operation-name"] = "update-shipment-status"
    response = requests.put(f"{BASE_URL}/shipments/{shipment_id}", 
                          json=update_data, 
                          headers=headers)
    
    if response.status_code == 200:
        updated_shipment = response.json()
        print(f"✅ Shipment updated: {updated_shipment}")
    else:
        print(f"❌ Failed to update shipment: {response.text}")
    
    # 5. Get all warehouses
    print("\n5. Getting all warehouses...")
    headers["operation-name"] = "list-all-warehouses"
    response = requests.get(f"{BASE_URL}/warehouses/", headers=headers)
    
    if response.status_code == 200:
        warehouses = response.json()
        print(f"✅ Warehouses: {warehouses}")
    else:
        print(f"❌ Failed to get warehouses: {response.text}")
    
    # 6. Get all shipments
    print("\n6. Getting all shipments...")
    headers["operation-name"] = "list-all-shipments"
    response = requests.get(f"{BASE_URL}/shipments/", headers=headers)
    
    if response.status_code == 200:
        shipments = response.json()
        print(f"✅ Shipments: {shipments}")
    else:
        print(f"❌ Failed to get shipments: {response.text}")
    
    print("\n" + "=" * 50)
    print("✅ Test completed! Check the consumer logs to see the events.")
    print("\nTo run the consumer, use:")
    print("python -m app.consumer warehouse_events")
    print("python -m app.consumer shipment_events")

if __name__ == "__main__":
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API. Make sure the server is running:")
        print("python -m app.main")
    except Exception as e:
        print(f"❌ Test failed: {e}")