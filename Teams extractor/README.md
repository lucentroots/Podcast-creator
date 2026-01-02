# Teams Message Extractor

Extract messages from Microsoft Teams channels using the Microsoft Graph API.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Get a Microsoft Graph API access token:
   - Register an app in Azure AD (https://portal.azure.com)
   - Grant the following permissions:
     - `ChannelMessage.Read.All` (for channel messages)
     - `Chat.Read.All` (for user chat messages)
   - Use OAuth2 to authenticate and get an access token

3. Set the access token:
```bash
export GRAPH_ACCESS_TOKEN="your_access_token_here"
```

Or you'll be prompted to enter it when running the script.

## Usage

### Extract messages from a channel URL:

```bash
python teams_message_extractor.py
```

The script will:
1. Parse the Teams channel URL
2. Extract the team ID and channel ID
3. Fetch all messages from the channel
4. Display them in the console
5. Save them to `teams_messages.json`

### Using the API endpoint for user chats:

If you want to use the `/users/{id}/chats/getAllMessages` endpoint specifically, you can modify the script or use the `get_user_chat_messages()` method:

```python
from teams_message_extractor import TeamsMessageExtractor

extractor = TeamsMessageExtractor(access_token)
messages = extractor.get_user_chat_messages("user_id_or_me")
```

## Notes

### Important: Endpoint Differences

- **`/users/{id}/chats/getAllMessages`**: This endpoint retrieves all **chat messages** (1-on-1 or group chats) for a specific user. This is NOT for channel messages.
- **`/teams/{team-id}/channels/{channel-id}/messages`**: This endpoint retrieves messages from a **Teams channel**.

Since you provided a channel URL, the main script (`teams_message_extractor.py`) uses the channel messages endpoint. If you specifically need to use the `/users/{id}/chats/getAllMessages` endpoint, use `example_user_chats.py` instead.

### Other Notes

- The access token must have the appropriate permissions
- Messages are paginated, so the script handles multiple pages automatically
- For channel messages, you need `ChannelMessage.Read.All` permission
- For user chat messages, you need `Chat.Read.All` permission

## Channel URL Format

The script can parse Teams channel URLs in the format:
```
https://teams.microsoft.com/l/channel/{channelId}/{channelName}?groupId={groupId}&tenantId={tenantId}
```

