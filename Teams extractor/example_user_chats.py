#!/usr/bin/env python3
"""
Example script using the /users/{id}/chats/getAllMessages endpoint
as specifically requested by the user.
"""

import os
import requests
import json
from teams_message_extractor import TeamsMessageExtractor


def get_user_chat_messages_direct(user_id: str, access_token: str):
    """
    Direct implementation of GET /users/{id}/chats/getAllMessages
    
    Args:
        user_id: User ID or 'me' for current user
        access_token: Microsoft Graph API access token
    """
    url = f"https://graph.microsoft.com/v1.0/users/{user_id}/chats/getAllMessages"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    all_messages = []
    
    try:
        while url:
            print(f"Fetching from: {url}")
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            messages = data.get('value', [])
            all_messages.extend(messages)
            print(f"Retrieved {len(messages)} messages (total: {len(all_messages)})")
            
            # Check for next page
            url = data.get('@odata.nextLink')
            
    except requests.exceptions.RequestException as e:
        print(f"Error fetching messages: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
        raise
    
    return all_messages


def main():
    """Main function to demonstrate the getAllMessages endpoint."""
    # Get access token
    access_token = os.getenv('GRAPH_ACCESS_TOKEN')
    if not access_token:
        access_token = input("Enter your Microsoft Graph API access token: ").strip()
    
    if not access_token:
        print("Error: Access token is required")
        return
    
    # Use 'me' to get messages for the current authenticated user
    # Or replace with a specific user ID
    user_id = input("Enter user ID (or 'me' for current user): ").strip() or "me"
    
    print(f"\nFetching all chat messages for user: {user_id}")
    print("Using endpoint: GET /users/{id}/chats/getAllMessages\n")
    
    try:
        # Method 1: Using the direct function
        messages = get_user_chat_messages_direct(user_id, access_token)
        
        # Method 2: Using the TeamsMessageExtractor class
        # extractor = TeamsMessageExtractor(access_token)
        # messages = extractor.get_user_chat_messages(user_id)
        
        print(f"\n✓ Successfully retrieved {len(messages)} messages\n")
        
        # Display summary
        for i, message in enumerate(messages[:10], 1):  # Show first 10
            print(f"\n--- Message {i} ---")
            print(f"ID: {message.get('id', 'N/A')}")
            print(f"Chat ID: {message.get('chatId', 'N/A')}")
            print(f"From: {message.get('from', {}).get('user', {}).get('displayName', 'Unknown')}")
            print(f"Created: {message.get('createdDateTime', 'N/A')}")
            body = message.get('body', {}).get('content', '')
            print(f"Body: {body[:100]}..." if len(body) > 100 else f"Body: {body}")
        
        if len(messages) > 10:
            print(f"\n... and {len(messages) - 10} more messages")
        
        # Save to JSON
        output_file = f"user_chat_messages_{user_id}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(messages, f, indent=2, ensure_ascii=False)
        
        print(f"\n\nAll messages saved to {output_file}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()



