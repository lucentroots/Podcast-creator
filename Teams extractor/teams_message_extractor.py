#!/usr/bin/env python3
"""
Microsoft Teams Message Extractor
Extracts messages from Teams channels using Microsoft Graph API
"""

import requests
import json
import urllib.parse
from typing import Dict, List, Optional
import os


class TeamsMessageExtractor:
    def __init__(self, access_token: str):
        """
        Initialize the extractor with an access token.
        
        Args:
            access_token: Microsoft Graph API access token
        """
        self.access_token = access_token
        self.base_url = "https://graph.microsoft.com/v1.0"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    
    def parse_channel_url(self, url: str) -> Dict[str, str]:
        """
        Parse a Teams channel URL to extract groupId, tenantId, and channelId.
        
        Args:
            url: Teams channel URL
            
        Returns:
            Dictionary with groupId, tenantId, and channelId
        """
        parsed = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(parsed.query)
        
        group_id = params.get('groupId', [None])[0]
        tenant_id = params.get('tenantId', [None])[0]
        
        # Extract channel ID from the path
        # Format: /l/channel/{channelId}/...
        path_parts = parsed.path.split('/')
        channel_id = None
        if 'channel' in path_parts:
            idx = path_parts.index('channel')
            if idx + 1 < len(path_parts):
                channel_id = urllib.parse.unquote(path_parts[idx + 1])
        
        return {
            'groupId': group_id,
            'tenantId': tenant_id,
            'channelId': channel_id
        }
    
    def get_team_id_from_group(self, group_id: str) -> Optional[str]:
        """
        Get the team ID from a group ID.
        
        Args:
            group_id: Azure AD group ID
            
        Returns:
            Team ID if found, None otherwise
        """
        url = f"{self.base_url}/groups/{group_id}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            # Check if the group is associated with a team
            if 'resourceProvisioningOptions' in data and 'Team' in data['resourceProvisioningOptions']:
                return data['id']
        except requests.exceptions.RequestException as e:
            print(f"Error getting team ID: {e}")
        return None
    
    def get_channel_messages(self, team_id: str, channel_id: str, top: int = 50) -> List[Dict]:
        """
        Get messages from a Teams channel.
        
        Args:
            team_id: Team ID
            channel_id: Channel ID
            top: Number of messages to retrieve (default: 50)
            
        Returns:
            List of message dictionaries
        """
        # URL decode the channel ID if needed
        channel_id = urllib.parse.unquote(channel_id)
        
        url = f"{self.base_url}/teams/{team_id}/channels/{channel_id}/messages"
        params = {"$top": top, "$orderby": "lastModifiedDateTime desc"}
        
        all_messages = []
        
        try:
            while url:
                response = requests.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                data = response.json()
                
                messages = data.get('value', [])
                all_messages.extend(messages)
                
                # Check for next page
                url = data.get('@odata.nextLink')
                params = None  # nextLink already includes parameters
                
        except requests.exceptions.RequestException as e:
            print(f"Error fetching channel messages: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
        
        return all_messages
    
    def get_user_chat_messages(self, user_id: str) -> List[Dict]:
        """
        Get all chat messages for a user using the getAllMessages endpoint.
        
        Args:
            user_id: User ID or 'me' for current user
            
        Returns:
            List of chat message dictionaries
        """
        url = f"{self.base_url}/users/{user_id}/chats/getAllMessages"
        
        all_messages = []
        
        try:
            while url:
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()
                data = response.json()
                
                messages = data.get('value', [])
                all_messages.extend(messages)
                
                # Check for next page
                url = data.get('@odata.nextLink')
                
        except requests.exceptions.RequestException as e:
            print(f"Error fetching user chat messages: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
        
        return all_messages
    
    def extract_messages_from_channel_url(self, channel_url: str) -> List[Dict]:
        """
        Extract messages from a Teams channel URL.
        
        Args:
            channel_url: Full Teams channel URL
            
        Returns:
            List of message dictionaries
        """
        # Parse the URL
        url_info = self.parse_channel_url(channel_url)
        
        if not url_info['groupId']:
            raise ValueError("Could not extract groupId from URL")
        
        # Get team ID from group ID
        team_id = self.get_team_id_from_group(url_info['groupId'])
        if not team_id:
            raise ValueError(f"Could not find team for group {url_info['groupId']}")
        
        if not url_info['channelId']:
            raise ValueError("Could not extract channelId from URL")
        
        # Get messages
        return self.get_channel_messages(team_id, url_info['channelId'])


def main():
    """
    Main function to extract messages from the provided Teams channel.
    """
    # Get access token from environment variable or user input
    access_token = os.getenv('GRAPH_ACCESS_TOKEN')
    if not access_token:
        access_token = input("Enter your Microsoft Graph API access token: ").strip()
    
    if not access_token:
        print("Error: Access token is required")
        print("\nTo get an access token:")
        print("1. Register an app in Azure AD")
        print("2. Grant permissions: ChannelMessage.Read.All or Chat.Read.All")
        print("3. Use OAuth2 to get an access token")
        return
    
    # Initialize extractor
    extractor = TeamsMessageExtractor(access_token)
    
    # Channel URL from user
    channel_url = "https://teams.microsoft.com/l/channel/19%3Af285e28086ef475b82c85ef3592d0457%40thread.tacv2/%F0%9F%9B%8E%EF%B8%8F%20%20DS_Design_SUPPORT?groupId=68e2d0f4-c57f-4d35-88fd-d4a80d670031&tenantId=fe1d95a9-4ce1-41a5-8eab-6dd43aa26d9f"
    
    print("Extracting messages from Teams channel...")
    print(f"URL: {channel_url}\n")
    
    try:
        # Extract messages
        messages = extractor.extract_messages_from_channel_url(channel_url)
        
        print(f"Found {len(messages)} messages\n")
        
        # Display messages
        for i, message in enumerate(messages, 1):
            print(f"\n--- Message {i} ---")
            print(f"ID: {message.get('id', 'N/A')}")
            print(f"From: {message.get('from', {}).get('user', {}).get('displayName', 'Unknown')}")
            print(f"Created: {message.get('createdDateTime', 'N/A')}")
            print(f"Body: {message.get('body', {}).get('content', 'N/A')[:200]}...")
            
            # Check for replies
            if 'replies' in message:
                print(f"Replies: {len(message['replies'])}")
        
        # Save to JSON file
        output_file = "teams_messages.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(messages, f, indent=2, ensure_ascii=False)
        
        print(f"\n\nMessages saved to {output_file}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()


