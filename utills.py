import os
from dotenv import load_dotenv

import socket
from pyngrok import ngrok, conf


load_dotenv(override=True)
API_PORT = os.getenv("API_PORT")
NGROK_AUTH_TOKEN = os.getenv("NGROK_AUTH_TOKEN")
ngrok.set_auth_token(NGROK_AUTH_TOKEN)


def get_whitelist():
    # reload environment variables
    print('reload')
    load_dotenv(override=True)
    USERS_WHITELIST = [int(user_id) for user_id in os.getenv("USERS_WHITELIST", "").split(',') if user_id]
    return USERS_WHITELIST


# Start ngrok when web service starts
def start_ngrok():
    conf.get_default().ngrok_path = os.path.join(os.path.dirname(__file__), "ngrok.exe")
    conf.get_default().region = 'us'  # Set your ngrok region
    public_url = ngrok.connect(API_PORT, hostname="awake-worm-secure.ngrok-free.app")
    print(f"ngrok tunnel opened at {public_url}")
    return public_url

# Stop ngrok when web service stops
def stop_ngrok():
    tunnels = ngrok.get_tunnels()
    if tunnels:
        for tunnel in tunnels:
            ngrok.disconnect(tunnel.public_url)
            print(f"Closed ngrok tunnel: {tunnel.public_url}")
    else:
        print("No active ngrok tunnels to close.")
    ngrok.kill()
    print("ngrok process terminated")
        

# Function to get the local IP address
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip