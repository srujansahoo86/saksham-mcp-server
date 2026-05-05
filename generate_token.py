import os
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/gmail.compose"
]

print("Starting Google Login...")
try:
    flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
    creds = flow.run_local_server(port=0)
    print("Login successful! Saving token.json...")
    with open("token.json", "w") as token:
        token.write(creds.to_json())
    print("✅ SUCCESS! token.json has been created in this folder!")
except Exception as e:
    print(f"❌ ERROR: {e}")
