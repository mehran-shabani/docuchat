#!/usr/bin/env python3
"""
Example script demonstrating DocuChat API usage
"""

import asyncio
import json

import httpx
import websockets

BASE_URL = "http://localhost:8000"
TENANT_ID = "1"


async def authenticate(email: str) -> str:
    """Authenticate and get JWT token"""

    async with httpx.AsyncClient() as client:
        # Request verification code
        print(f"📧 Requesting verification code for {email}...")
        response = await client.post(
            f"{BASE_URL}/v1/auth/request-code",
            json={"email": email},
            headers={"X-Tenant-ID": TENANT_ID},
        )
        print(f"Response: {response.json()}")

        # In a real scenario, get the code from email
        # For this example, check server logs
        code = input("Enter verification code from server logs: ")

        # Verify code
        print("🔑 Verifying code...")
        response = await client.post(
            f"{BASE_URL}/v1/auth/verify-code",
            json={"email": email, "code": code},
            headers={"X-Tenant-ID": TENANT_ID},
        )

        if response.status_code == 200:
            data = response.json()
            token = data["access_token"]
            print("✅ Authentication successful!")
            return token
        else:
            print(f"❌ Authentication failed: {response.text}")
            return None


async def upload_pdf(token: str, pdf_path: str):
    """Upload a PDF file"""

    async with httpx.AsyncClient() as client:
        print(f"📄 Uploading PDF: {pdf_path}...")

        with open(pdf_path, "rb") as f:
            files = {"file": (pdf_path, f, "application/pdf")}
            response = await client.post(
                f"{BASE_URL}/v1/files",
                files=files,
                headers={"X-Tenant-ID": TENANT_ID, "Authorization": f"Bearer {token}"},
            )

        if response.status_code == 200:
            data = response.json()
            print("✅ Upload successful!")
            print(f"   Document ID: {data['document_id']}")
            print(f"   Elapsed: {data['elapsed_ms']:.2f}ms")
            return data["document_id"]
        else:
            print(f"❌ Upload failed: {response.text}")
            return None


async def chat_websocket(token: str, message: str):
    """Chat via WebSocket"""

    uri = f"ws://localhost:8000/ws/chat?token={token}"

    print("💬 Connecting to chat...")

    async with websockets.connect(uri, extra_headers={"X-Tenant-ID": TENANT_ID}) as websocket:
        print("✅ Connected!")

        # Send message
        await websocket.send(json.dumps({"message": message}))

        print("🤖 Assistant: ", end="", flush=True)

        # Receive streaming response
        async for response in websocket:
            data = json.loads(response)

            if data["type"] == "start":
                print(f"\n[Session {data['session_id']}]")
                print("🤖 Assistant: ", end="", flush=True)

            elif data["type"] == "delta":
                print(data["token"], end="", flush=True)

            elif data["type"] == "end":
                print(f"\n\n📊 Usage: {data['usage']}")
                break

            elif data["type"] == "error":
                print(f"\n❌ Error: {data['message']}")
                break


async def get_usage(token: str):
    """Get usage statistics"""

    async with httpx.AsyncClient() as client:
        print("📊 Fetching usage statistics...")

        response = await client.get(
            f"{BASE_URL}/v1/usage",
            headers={"X-Tenant-ID": TENANT_ID, "Authorization": f"Bearer {token}"},
        )

        if response.status_code == 200:
            data = response.json()
            print("✅ Usage statistics:")
            print(f"   24h: {data['window_24h']}")
            print(f"   7d:  {data['window_7d']}")
        else:
            print(f"❌ Failed: {response.text}")


async def main():
    """Main example flow"""

    print("=" * 50)
    print("DocuChat API Usage Example")
    print("=" * 50)
    print()

    # Step 1: Authenticate
    email = input("Enter your email: ")
    token = await authenticate(email)

    if not token:
        return

    print()

    # Step 2: Upload PDF (optional)
    upload = input("Do you want to upload a PDF? (y/n): ")
    if upload.lower() == "y":
        pdf_path = input("Enter PDF path: ")
        await upload_pdf(token, pdf_path)
        print()

    # Step 3: Chat
    while True:
        message = input("\nYour question (or 'quit' to exit): ")
        if message.lower() == "quit":
            break

        await chat_websocket(token, message)

    # Step 4: Get usage stats
    print()
    await get_usage(token)


if __name__ == "__main__":
    asyncio.run(main())
