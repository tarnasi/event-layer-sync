#!/usr/bin/env python3
"""
Script to start a server with specific configuration
Usage: python start_server.py A  # Starts server A on port 8000
       python start_server.py B  # Starts server B on port 8001
"""

import sys
import os
import uvicorn
from app.core.config import settings

def main():
    if len(sys.argv) < 2:
        print("Usage: python start_server.py <server_id>")
        print("Available servers: A, B, C, D")
        sys.exit(1)
    
    server_id = sys.argv[1].upper()
    
    if server_id not in ["A", "B", "C", "D"]:
        print(f"Invalid server ID: {server_id}")
        print("Available servers: A, B, C, D")
        sys.exit(1)
    
    # Set environment variables for the server
    env_file = f".env.server_{server_id.lower()}"
    if os.path.exists(env_file):
        # Load environment variables from file
        with open(env_file, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value.strip('"[]')
    
    # Override with command line server ID
    os.environ['SERVER_ID'] = server_id
    
    # Determine port based on server ID
    port_map = {"A": 8000, "B": 8001, "C": 8002, "D": 8003}
    port = port_map.get(server_id, 8000)
    
    print(f"Starting server {server_id} on port {port}")
    print(f"Server will consume events from: {os.environ.get('ALLOWED_SERVERS', 'B,C,D')}")
    
    # Start the server
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()