#!/usr/bin/env python3
"""
Helper script to get Microsoft Graph API access token using device code flow.
This is useful for testing and development.
"""

import requests
import json
import time
import webbrowser

# Replace these with your Azure AD app registration details
CLIENT_ID = "YOUR_CLIENT_ID"  # Application (client) ID
TENANT_ID = "YOUR_TENANT_ID"  # Directory (tenant) ID
SCOPES = ["https://graph.microsoft.com/ChannelMessage.Read.All", 
          "https://graph.microsoft.com/Chat.Read.All"]


def get_device_code():
    """Initiate device code flow."""
    url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/devicecode"
    data = {
        "client_id": CLIENT_ID,
        "scope": " ".join(SCOPES)
    }
    
    response = requests.post(url, data=data)
    response.raise_for_status()
    return response.json()


def get_access_token(device_code):
    """Poll for access token."""
    url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
    data = {
        "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
        "client_id": CLIENT_ID,
        "device_code": device_code
    }
    
    response = requests.post(url, data=data)
    return response.json()


def authenticate():
    """Authenticate and get access token."""
    print("Starting device code authentication...")
    
    # Get device code
    device_info = get_device_code()
    print(f"\n{device_info['message']}")
    print(f"Device code: {device_info['user_code']}")
    
    # Try to open browser
    try:
        webbrowser.open(device_info['verification_uri'])
    except:
        pass
    
    # Poll for token
    interval = device_info['interval']
    expires_in = device_info['expires_in']
    start_time = time.time()
    
    while time.time() - start_time < expires_in:
        time.sleep(interval)
        token_response = get_access_token(device_info['device_code'])
        
        if 'access_token' in token_response:
            print("\n✓ Authentication successful!")
            return token_response['access_token']
        elif token_response.get('error') == 'authorization_pending':
            continue
        else:
            print(f"\nError: {token_response.get('error_description', 'Unknown error')}")
            return None
    
    print("\nAuthentication timed out")
    return None


if __name__ == "__main__":
    if CLIENT_ID == "YOUR_CLIENT_ID" or TENANT_ID == "YOUR_TENANT_ID":
        print("Please update CLIENT_ID and TENANT_ID in this script")
        print("\nTo get these values:")
        print("1. Go to https://portal.azure.com")
        print("2. Navigate to Azure Active Directory > App registrations")
        print("3. Create a new registration or use an existing one")
        print("4. Copy the Application (client) ID and Directory (tenant) ID")
        print("5. Add API permissions: ChannelMessage.Read.All, Chat.Read.All")
    else:
        token = authenticate()
        if token:
            print(f"\nAccess Token: {token}")
            print("\nYou can now use this token with the extractor:")
            print(f"export GRAPH_ACCESS_TOKEN='{token}'")



